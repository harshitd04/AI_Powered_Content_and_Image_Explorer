"""
AI Content Explorer - FastAPI Server with PostgreSQL Integration
"""

import os
import threading
import logging
from datetime import datetime, timedelta, UTC

from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import json
import asyncio
from urllib.parse import urlencode
from contextlib import contextmanager

import jwt
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext

# Import MCP with correct paths
try:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    MCP_AVAILABLE = True
    print("✅ MCP packages loaded successfully!")
    print("   - ClientSession imported from mcp")
    print("   - streamablehttp_client imported from mcp.client.streamable_http")
except ImportError as e:
    MCP_AVAILABLE = False
    print(f"⚠️ MCP import failed: {e}")
    print("   Using mock services instead")

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "k_o8c9jDUgeMhF3-C8oG9FXMMuEwJEzyaYEv80kIvtw")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7
MCP_API_KEY = os.getenv("MCP_API_KEY", "5cba1d1c-7ce8-48c9-bf0b-e77955eea543")

# PostgreSQL Configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}
# Connection pool for better connection management
CONNECTION_POOL = None
POOL_LOCK = threading.Lock()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_connection_pool():
    """Initialize the connection pool."""
    global CONNECTION_POOL
    if CONNECTION_POOL is None:
        with POOL_LOCK:
            if CONNECTION_POOL is None:
                try:
                    CONNECTION_POOL = SimpleConnectionPool(
                        1, 20,  # min and max connections
                        **DB_CONFIG
                    )
                    logger.info("Database connection pool initialized successfully")
                    
                    # Create tables if they don't exist
                    create_tables()
                    
                    # Create admin user if not exists
                    create_admin_user()
                    
                except Exception as e:
                    logger.error(f"Failed to initialize connection pool: {e}")
                    raise

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    if CONNECTION_POOL is None:
        initialize_connection_pool()
    
    conn = None
    try:
        conn = CONNECTION_POOL.getconn()
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            CONNECTION_POOL.putconn(conn)

def create_tables():
    """Create database tables if they don't exist."""
    create_tables_sql = """
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        full_name VARCHAR(255),
        hashed_password VARCHAR(255) NOT NULL,
        role VARCHAR(20) DEFAULT 'basic' CHECK (role IN ('basic', 'admin')),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP WITH TIME ZONE,
        is_active BOOLEAN DEFAULT true
    );

    -- Search history table
    CREATE TABLE IF NOT EXISTS search_history (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        query TEXT NOT NULL,
        results JSONB,
        max_results INTEGER DEFAULT 10,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        saved BOOLEAN DEFAULT true,
        metadata JSONB
    );

    -- Image history table
    CREATE TABLE IF NOT EXISTS image_history (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        prompt TEXT NOT NULL,
        image_url TEXT,
        image_data TEXT,
        parameters JSONB,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        saved BOOLEAN DEFAULT true,
        metadata JSONB
    );

    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_search_history_user_id ON search_history(user_id);
    CREATE INDEX IF NOT EXISTS idx_search_history_timestamp ON search_history(timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_image_history_user_id ON image_history(user_id);
    CREATE INDEX IF NOT EXISTS idx_image_history_timestamp ON image_history(timestamp DESC);
    """
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(create_tables_sql)
            conn.commit()
            logger.info("Database tables created/verified successfully")

def create_admin_user():
    """Create admin user if it doesn't exist."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Check if admin user exists
            cur.execute("SELECT id FROM users WHERE username = %s", ("admin",))
            if not cur.fetchone():
                # Create admin user
                hashed_password = pwd_context.hash("admin123")
                cur.execute("""
                    INSERT INTO users (username, email, full_name, hashed_password, role)
                    VALUES (%s, %s, %s, %s, %s)
                """, ("admin", "admin@aiexplorer.com", "System Administrator", hashed_password, "admin"))
                conn.commit()
                logger.info("Admin user created successfully")

# User Roles
class UserRole(str, Enum):
    BASIC = "basic"
    ADMIN = "admin"

# FastAPI app
app = FastAPI(
    title="AI Content Explorer",
    description="Platform for AI-powered search and image generation with PostgreSQL",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# MCP Server URLs
FLUX_SERVER_URL = f"https://server.smithery.ai/@falahgs/flux-imagegen-mcp-server/mcp?{urlencode({'api_key': MCP_API_KEY})}"
DUCKDUCKGO_SERVER_URL = f"https://server.smithery.ai/@nickclyde/duckduckgo-mcp-server/mcp?{urlencode({'api_key': MCP_API_KEY})}"

# Pydantic Models
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime]

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    max_results: Optional[int] = Field(10, ge=1, le=50)
    save_result: bool = True

class SearchResult(BaseModel):
    id: Optional[int] = None
    query: str
    results: List[Dict[str, Any]]
    timestamp: datetime
    saved: bool = False

class ImageRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    width: Optional[int] = Field(512, ge=256, le=1024)
    height: Optional[int] = Field(512, ge=256, le=1024)
    steps: Optional[int] = Field(20, ge=10, le=50)
    save_result: bool = True

class ImageResult(BaseModel):
    id: Optional[int] = None
    prompt: str
    image_url: Optional[str] = None
    image_data: Optional[str] = None
    parameters: Dict[str, Any]
    timestamp: datetime
    saved: bool = False

class DashboardStats(BaseModel):
    total_searches: int
    total_images: int
    searches_today: int
    images_today: int
    member_since: datetime
    last_activity: Optional[datetime]

class DashboardData(BaseModel):
    stats: DashboardStats
    recent_searches: List[SearchResult]
    recent_images: List[ImageResult]

# Initialize connection pool on startup
try:
    initialize_connection_pool()
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise

# Utility Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC)+ (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials.credentials)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Get user from database
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE username = %s AND is_active = true", (username,))
            user = cur.fetchone()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return dict(user)

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# MCP Service Functions
async def search_with_mcp(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """Real search using DuckDuckGo MCP server"""
    
    try:
        async with streamablehttp_client(DUCKDUCKGO_SERVER_URL) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                tools_result = await session.list_tools()
                search_tool = next(
                    (tool for tool in tools_result.tools if 'search' in tool.name.lower()),
                    None
                )
                
                if not search_tool:
                    return [{"error": "Search service temporarily unavailable"}]
                
                result = await session.call_tool(
                    search_tool.name, 
                    {"query": query, "max_results": max_results}
                )
                
                # Handle the result content properly
                if hasattr(result, 'content') and result.content:
                    search_results = []
                    
                    # Handle list of content items
                    if isinstance(result.content, list):
                        for content_item in result.content:
                            if hasattr(content_item, 'text'):
                                # This is a TextContent object
                                try:
                                    # Try to parse as JSON first
                                    parsed_data = json.loads(content_item.text)
                                    if isinstance(parsed_data, dict):
                                        search_results.append(parsed_data)
                                    elif isinstance(parsed_data, list):
                                        search_results.extend(parsed_data)
                                    else:
                                        search_results.append({
                                            "title": f"Search result for '{query}'",
                                            "content": str(parsed_data),
                                            "source": "DuckDuckGo"
                                        })
                                except json.JSONDecodeError:
                                    # If not JSON, treat as plain text
                                    search_results.append({
                                        "title": f"Search result for '{query}'",
                                        "content": content_item.text,
                                        "source": "DuckDuckGo"
                                    })
                            else:
                                # Handle other content types
                                search_results.append({
                                    "title": f"Search result for '{query}'",
                                    "content": str(content_item),
                                    "source": "DuckDuckGo"
                                })
                    
                    # Handle single content item
                    elif hasattr(result.content, 'text'):
                        try:
                            # Try to parse as JSON
                            parsed_data = json.loads(result.content.text)
                            if isinstance(parsed_data, list):
                                search_results = parsed_data
                            elif isinstance(parsed_data, dict):
                                search_results = [parsed_data]
                            else:
                                search_results = [{
                                    "title": f"Search result for '{query}'",
                                    "content": str(parsed_data),
                                    "source": "DuckDuckGo"
                                }]
                        except json.JSONDecodeError:
                            search_results = [{
                                "title": f"Search result for '{query}'",
                                "content": result.content.text,
                                "source": "DuckDuckGo"
                            }]
                    
                    # Handle string content (legacy)
                    elif isinstance(result.content, str):
                        try:
                            parsed_content = json.loads(result.content)
                            if isinstance(parsed_content, list):
                                search_results = parsed_content
                            elif isinstance(parsed_content, dict):
                                search_results = [parsed_content]
                            else:
                                search_results = [{
                                    "title": f"Search result for '{query}'",
                                    "content": str(parsed_content),
                                    "source": "DuckDuckGo"
                                }]
                        except json.JSONDecodeError:
                            search_results = [{
                                "title": f"Search result for '{query}'",
                                "content": result.content,
                                "source": "DuckDuckGo"
                            }]
                    
                    else:
                        # Fallback for unknown content types
                        search_results = [{
                            "title": f"Search result for '{query}'",
                            "content": str(result.content),
                            "source": "DuckDuckGo"
                        }]
                    
                    # Ensure all items are dictionaries and limit results
                    final_results = []
                    for item in search_results[:max_results]:
                        if isinstance(item, dict):
                            final_results.append(item)
                        else:
                            final_results.append({
                                "title": f"Search result for '{query}'",
                                "content": str(item),
                                "source": "DuckDuckGo"
                            })
                    
                    return final_results if final_results else [{
                        "title": f"No results found for '{query}'",
                        "content": "No search results available",
                        "source": "DuckDuckGo"
                    }]
                
                # If no content, return fallback
                return [{
                    "title": f"Search completed for '{query}'",
                    "content": str(result) if result else "No results available",
                    "source": "DuckDuckGo"
                }]
                
    except Exception as e:
        logger.error(f"MCP search error: {e}", exc_info=True)
        return [{"error": f"Search service unavailable: {str(e)}"}]


async def generate_image_with_mcp(prompt: str, **kwargs) -> Dict[str, Any]:
    """Real image generation using Flux MCP server"""
    if not MCP_AVAILABLE:
        return await mock_image_service(prompt, **kwargs)
    
    try:
        async with streamablehttp_client(FLUX_SERVER_URL) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                tools_result = await session.list_tools()
                print(f"Available image tools: {', '.join([t.name for t in tools_result.tools])}")
                
                # Find the image generation tool
                image_tool = next(
                    (tool for tool in tools_result.tools 
                     if any(keyword in tool.name.lower() for keyword in ['generate', 'image', 'flux'])),
                    None
                )
                
                if not image_tool:
                    return {"error": "Image generation service temporarily unavailable"}
                
                # Prepare parameters
                params = {"prompt": prompt}
                # Add other parameters if they exist in kwargs
                if "width" in kwargs:
                    params["width"] = kwargs["width"]
                if "height" in kwargs:
                    params["height"] = kwargs["height"]
                if "steps" in kwargs:
                    params["steps"] = kwargs["steps"]
                
                print(f"Using image tool: {image_tool.name} with params: {params}")
                result = await session.call_tool(image_tool.name, params)
                
                # Handle the result content - based on your working example
                image_data = None
                image_url = None
                
                if hasattr(result, 'content') and result.content:
                    if isinstance(result.content, list) and len(result.content) > 0:
                        # Get the first content item (as in your working example)
                        text_obj = result.content[0]
                        
                        if hasattr(text_obj, 'text'):
                            try:
                                # Parse the JSON response
                                parsed_data = json.loads(text_obj.text)
                                print(f"Parsed JSON data: {parsed_data}")
                                
                                # Extract image URL and data based on the actual response structure
                                # Your working example shows "imageUrl" field
                                image_url = parsed_data.get('imageUrl') or parsed_data.get('image_url') or parsed_data.get('url')
                                image_data = parsed_data.get('imageData') or parsed_data.get('image_data') or parsed_data.get('data') or parsed_data.get('base64')
                                
                                print(f"Extracted image_url: {image_url}")
                                print(f"Extracted image_data: {'Present' if image_data else 'None'}")
                                
                            except json.JSONDecodeError as e:
                                print(f"JSON decode error: {e}")
                                # Fallback: treat as raw text
                                text_content = text_obj.text.strip()
                                if text_content.startswith('http'):
                                    image_url = text_content
                                elif text_content.startswith('data:image/'):
                                    image_data = text_content
                        else:
                            print(f"No text attribute in content item: {type(text_obj)}")
                    else:
                        print(f"Content is not a list or is empty: {type(result.content)}")
                else:
                    print("No content in result")
                
                return {
                    "image_data": image_data,
                    "image_url": image_url,
                    "status": "success",
                    "prompt_used": prompt
                }
                
    except Exception as e:
        logger.error(f"MCP image generation error: {e}", exc_info=True)
        return {"error": f"Image generation service unavailable: {str(e)}"}


# Mock Service Functions (fallback)
async def mock_search_service(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    await asyncio.sleep(0.5)
    return [
        {
            "title": f"Search Result {i+1} for '{query}'",
            "snippet": f"Mock search result snippet for query: {query}. Result number {i+1}.",
            "url": f"https://example.com/result-{i+1}",
            "source": "Mock Search Engine"
        }
        for i in range(min(max_results, 5))
    ]

async def mock_image_service(prompt: str, **kwargs) -> Dict[str, Any]:
    await asyncio.sleep(1.0)
    return {
        "image_url": f"https://picsum.photos/{kwargs.get('width', 512)}/{kwargs.get('height', 512)}?random={hash(prompt) % 1000}",
        "image_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
        "status": "success",
        "prompt_used": prompt
    }

# Authentication Routes
@app.post("/auth/register", response_model=Token)
async def register(user_data: UserRegister):
    """Register a new user"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Check if username exists
            cur.execute("SELECT id FROM users WHERE username = %s", (user_data.username,))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Username already exists")
            
            # Check if email exists
            cur.execute("SELECT id FROM users WHERE email = %s", (user_data.email,))
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Create new user
            hashed_password = get_password_hash(user_data.password)
            cur.execute("""
                INSERT INTO users (username, email, full_name, hashed_password, role)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, (user_data.username, user_data.email, user_data.full_name, hashed_password, UserRole.BASIC))
            
            user_id = cur.fetchone()[0]
            conn.commit()
    
    access_token = create_access_token(data={"sub": user_data.username})
    refresh_token = create_refresh_token(data={"sub": user_data.username})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Authenticate user and return tokens"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM users WHERE username = %s AND is_active = true", 
                (user_credentials.username,)
            )
            user = cur.fetchone()
    
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Update last login
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                (user["id"],)
            )
            conn.commit()
    
    access_token = create_access_token(data={"sub": user_credentials.username})
    refresh_token = create_refresh_token(data={"sub": user_credentials.username})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.get("/auth/profile", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        role=current_user["role"],
        created_at=current_user["created_at"],
        last_login=current_user.get("last_login")
    )

# Search Routes
@app.post("/search", response_model=SearchResult)
async def search_information(
    search_request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """Search for information via MCP and optionally save in DB"""
    try:
        # Call MCP search
        results = await search_with_mcp(search_request.query, search_request.max_results)
        timestamp = datetime.now(UTC)

        # Build SearchResult
        search_result = SearchResult(
            query=search_request.query,
            results=results,
            timestamp=timestamp,
            saved=search_request.save_result
        )

        # Save to DB if requested
        if search_request.save_result:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO search_history (user_id, query, results, max_results, timestamp, saved)
                        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                    """, (
                        current_user["id"],
                        search_request.query,
                        json.dumps(results),
                        search_request.max_results,
                        timestamp.isoformat(),
                        search_request.save_result
                    ))
                    search_result.id = cur.fetchone()[0]
                    conn.commit()

        return search_result

    except Exception as e:
        logger.error(f"Search endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# Image Routes
@app.post("/image", response_model=ImageResult)
async def generate_image(
    image_request: ImageRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate AI image"""
    kwargs = {
        "width": image_request.width,
        "height": image_request.height,
        "steps": image_request.steps
    }
    
    result = await generate_image_with_mcp(image_request.prompt, **kwargs)
    timestamp = datetime.now(UTC)

    image_result = ImageResult(
        prompt=image_request.prompt,
        image_url=result.get("image_url"),
        image_data=result.get("image_data"),
        parameters=kwargs,
        timestamp=timestamp,
        saved=image_request.save_result
    )
    
    if image_request.save_result:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO image_history (user_id, prompt, image_url, image_data, parameters, timestamp, saved)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (
                    current_user["id"],
                    image_request.prompt,
                    result.get("image_url"),
                    result.get("image_data"),
                    json.dumps(kwargs),
                    timestamp,
                    image_request.save_result
                ))
                image_result.id = cur.fetchone()[0]
                conn.commit()
    
    return image_result

# Dashboard Routes
@app.get("/dashboard", response_model=DashboardData)
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    """Get user dashboard"""
    user_id = current_user["id"]
    today = datetime.now(UTC).date()
    
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get search stats
            cur.execute("SELECT COUNT(*) FROM search_history WHERE user_id = %s", (user_id,))
            total_searches = cur.fetchone()[0]
            
            cur.execute(
                "SELECT COUNT(*) FROM search_history WHERE user_id = %s AND DATE(timestamp) = %s",
                (user_id, today)
            )
            searches_today = cur.fetchone()[0]
            
            # Get image stats
            cur.execute("SELECT COUNT(*) FROM image_history WHERE user_id = %s", (user_id,))
            total_images = cur.fetchone()[0]
            
            cur.execute(
                "SELECT COUNT(*) FROM image_history WHERE user_id = %s AND DATE(timestamp) = %s",
                (user_id, today)
            )
            images_today = cur.fetchone()[0]
            
            # Get last activity
            cur.execute("""
                SELECT MAX(timestamp) FROM (
                    SELECT timestamp FROM search_history WHERE user_id = %s
                    UNION ALL
                    SELECT timestamp FROM image_history WHERE user_id = %s
                ) AS activities
            """, (user_id, user_id))
            last_activity = cur.fetchone()[0]
            
            # Get recent searches
            cur.execute("""
                SELECT id, query, results, timestamp, saved
                FROM search_history 
                WHERE user_id = %s 
                ORDER BY timestamp DESC 
                LIMIT 5
            """, (user_id,))
            recent_searches = [
                SearchResult(
                    id=row["id"],
                    query=row["query"],
                    results=row["results"],
                    timestamp=row["timestamp"],
                    saved=row["saved"]
                )
                for row in cur.fetchall()
            ]
            
            # Get recent images
            cur.execute("""
                SELECT id, prompt, image_url, image_data, parameters, timestamp, saved
                FROM image_history 
                WHERE user_id = %s 
                ORDER BY timestamp DESC 
                LIMIT 5
            """, (user_id,))
            recent_images = [
                ImageResult(
                    id=row["id"],
                    prompt=row["prompt"],
                    image_url=row["image_url"],
                    image_data=row["image_data"],
                    parameters=row["parameters"],
                    timestamp=row["timestamp"],
                    saved=row["saved"]
                )
                for row in cur.fetchall()
            ]
    
    stats = DashboardStats(
        total_searches=total_searches,
        total_images=total_images,
        searches_today=searches_today,
        images_today=images_today,
        member_since=current_user["created_at"],
        last_activity=last_activity
    )
    
    return DashboardData(
        stats=stats,
        recent_searches=recent_searches,
        recent_images=recent_images
    )

@app.delete("/dashboard/search/{search_id}")
async def delete_search(search_id: int, current_user: dict = Depends(get_current_user)):
    """Delete a search entry"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM search_history WHERE id = %s AND user_id = %s",
                (search_id, current_user["id"])
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Search entry not found")
            conn.commit()
    
    return {"message": "Search entry deleted successfully"}

@app.delete("/dashboard/image/{image_id}")
async def delete_image(image_id: int, current_user: dict = Depends(get_current_user)):
    """Delete an image entry"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM image_history WHERE id = %s AND user_id = %s",
                (image_id, current_user["id"])
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Image entry not found")
            conn.commit()
    
    return {"message": "Image entry deleted successfully"}

# Admin Routes
@app.get("/admin/users")
async def list_all_users(admin_user: dict = Depends(get_admin_user)):
    """Admin: List all users"""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, username, email, full_name, role, created_at, last_login, is_active
                FROM users 
                ORDER BY created_at DESC
            """)
            return cur.fetchall()

@app.get("/admin/stats")
async def get_system_stats(admin_user: dict = Depends(get_admin_user)):
    """Admin: Get system statistics"""
    today = datetime.now(UTC).date()
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Get total counts
            cur.execute("SELECT COUNT(*) FROM users")
            total_users = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM search_history")
            total_searches = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM image_history")
            total_images = cur.fetchone()[0]
            
            # Get today's counts
            cur.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = %s", (today,))
            users_today = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM search_history WHERE DATE(timestamp) = %s", (today,))
            searches_today = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM image_history WHERE DATE(timestamp) = %s", (today,))
            images_today = cur.fetchone()[0]
    
    return {
        "total_users": total_users,
        "total_searches": total_searches,
        "total_images": total_images,
        "users_today": users_today,
        "searches_today": searches_today,
        "images_today": images_today
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Test database connection
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC),
        "version": "3.0.0",
        "database": db_status,
        "mcp_available": MCP_AVAILABLE
    }



@app.get("/")
async def root():
    """API information"""
    return {
        "name": "AI Content Explorer",
        "version": "2.0.0",
        "description": "Platform for AI-powered search and image generation",
        "endpoints": {
            "authentication": "/auth/*",
            "search": "/search",
            "images": "/image",
            "dashboard": "/dashboard",
            "admin": "/admin/* (admin only)",
            "documentation": "/docs"
        },
        "features": [
            "JWT Authentication with role-based access",
            "DuckDuckGo web search integration", 
            "AI image generation with Flux",
            "Personal dashboard and history",
            "Content filtering and management"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
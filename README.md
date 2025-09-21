# AI Content Explorer

A full-stack web application that provides AI-powered search and image generation capabilities through a modern, responsive interface. Built with FastAPI backend and React frontend, featuring secure authentication, real-time search, and AI image generation.

## Features

### Core Functionality
- **AI-Powered Search**: Intelligent web search using DuckDuckGo MCP server integration
- **Image Generation**: AI-driven image creation using Flux ImageGen MCP server
- **User Authentication**: Secure JWT-based authentication with role-based access control
- **Personal Dashboard**: Track search history, generated images, and user statistics
- **Data Persistence**: PostgreSQL database with connection pooling for reliable data storage

### User Experience
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Dark/Light Mode**: System preference detection with manual toggle
- **Real-time Updates**: Live search results and image generation status
- **History Management**: Save, view, and delete search results and generated images
- **Admin Panel**: Administrative features for user management

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework with automatic API documentation
- **PostgreSQL**: Robust relational database with TimescaleDB extensions
- **JWT Authentication**: Secure token-based authentication system
- **MCP Integration**: Model Context Protocol for AI service connectivity
- **Docker**: Containerized database deployment
- **Pydantic**: Data validation and serialization

### Frontend
- **React 18**: Modern React with functional components and hooks
- **React Router**: Client-side routing and navigation
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Axios**: HTTP client for API communication
- **Context API**: State management for authentication and theming
- **Heroicons**: Professional SVG icon library

### Infrastructure
- **Docker Compose**: Multi-container application orchestration
- **TimescaleDB**: Time-series database capabilities
- **Ollama**: Local AI model hosting (optional)
- **Connection Pooling**: Efficient database connection management

## Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Docker** and Docker Compose
- **Git** for version control

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-content-explorer
```

### 2. Start the Database
```bash
cd backend
docker-compose up -d
```

### 3. Set Up Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export SECRET_KEY="your-secret-key"
export MCP_API_KEY="your-mcp-api-key"

# Start the FastAPI server
python main.py
```

### 4. Set Up Frontend
```bash
cd frontend
npm install
npm start
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Configuration

### Environment Variables

#### Backend Configuration
```bash
# Security
SECRET_KEY=your-jwt-secret-key
MCP_API_KEY=your-mcp-api-key

# Database
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### Default Credentials
- **Admin User**: username `admin`, password `admin123`
- **Database**: PostgreSQL on port 5432

## Project Structure

```
ai-content-explorer/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── docker-compose.yml      # Database container configuration
│   ├── debug_mcp.py           # MCP debugging utilities
│   └── error-debugging.py     # Error handling utilities
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── contexts/          # React Context providers
│   │   ├── pages/             # Application pages
│   │   └── App.js             # Main application component
│   ├── public/                # Static assets
│   ├── package.json           # Node.js dependencies
│   └── tailwind.config.js     # Tailwind CSS configuration
└── README.md                  # Project documentation
```

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `GET /auth/profile` - Get user profile

### Search
- `POST /search` - Perform AI-powered search
- `GET /search/history` - Get search history
- `DELETE /search/{id}` - Delete search entry

### Image Generation
- `POST /image` - Generate AI images
- `GET /image/history` - Get image history
- `DELETE /image/{id}` - Delete image entry

### Dashboard
- `GET /dashboard` - Get user dashboard data

## Development

### Backend Development
```bash
cd backend
# Install development dependencies
pip install -r requirements-dev.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
# Start development server with hot reload
npm start

# Build for production
npm run build
```

### Database Management
```bash
# Start database
docker-compose up -d

# Stop database
docker-compose down

# Reset database (removes all data)
docker-compose down -v
```

## Security Features

- **JWT Token Authentication**: Secure access and refresh token system
- **Password Hashing**: Bcrypt encryption for user passwords
- **CORS Protection**: Configured for specific origins
- **SQL Injection Prevention**: Parameterized queries throughout
- **Role-Based Access**: Admin and basic user roles
- **Input Validation**: Pydantic models for request validation

## Performance Optimizations

- **Connection Pooling**: Efficient database connection management
- **Async Operations**: Non-blocking I/O for better concurrency
- **Response Caching**: Optimized API response handling
- **Lazy Loading**: Frontend components loaded on demand
- **Image Optimization**: Efficient image handling and storage

## Deployment

### Production Considerations
- Set strong `SECRET_KEY` and `MCP_API_KEY` values
- Use environment-specific database credentials
- Configure CORS for production domains
- Set up SSL/TLS certificates
- Implement proper logging and monitoring
- Use production-grade database hosting

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.

## Acknowledgments

- **FastAPI**: For the excellent Python web framework
- **React**: For the powerful frontend library
- **MCP Protocol**: For AI service integration capabilities
- **TimescaleDB**: For robust database functionality
- **Tailwind CSS**: For rapid UI development
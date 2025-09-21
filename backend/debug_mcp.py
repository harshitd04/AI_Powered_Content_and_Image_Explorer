#!/usr/bin/env python3
"""
Debug script to check MCP installation and find correct imports
Run this to see what's available in your MCP installation
"""

import sys
import importlib

def test_import(module_path, item_name):
    """Test importing a specific item from a module"""
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, item_name):
            print(f"✅ Found {item_name} in {module_path}")
            return True
        else:
            print(f"❌ {item_name} not found in {module_path}")
            print(f"   Available: {[x for x in dir(module) if not x.startswith('_')]}")
            return False
    except ImportError as e:
        print(f"❌ Cannot import {module_path}: {e}")
        return False

def main():
    print("=== MCP Installation Debug ===\n")
    
    # Test basic MCP import
    try:
        import mcp
        print(f"✅ MCP module imported successfully")
        print(f"   Version: {getattr(mcp, '__version__', 'unknown')}")
        print(f"   Location: {mcp.__file__}")
        print(f"   Contents: {[x for x in dir(mcp) if not x.startswith('_')]}")
        print()
    except ImportError as e:
        print(f"❌ Cannot import MCP: {e}")
        return
    
    # Test different client import paths
    print("=== Testing Client Imports ===")
    
    client_paths = [
        ("mcp", "ClientSession"),
        ("mcp.client", "ClientSession"), 
        ("mcp", "Client"),
        ("mcp.client", "Client"),
    ]
    
    for module_path, class_name in client_paths:
        test_import(module_path, class_name)
    
    print("\n=== Testing HTTP Client Imports ===")
    
    http_paths = [
        ("mcp.client.streamable_http", "streamablehttp_client"),
        ("mcp.client", "streamablehttp_client"),
        ("mcp.client.http", "streamablehttp_client"),
        ("mcp", "streamablehttp_client"),
        ("mcp.client.streamable_http", "StreamableHTTPClient"),
        ("mcp.client", "StreamableHTTPClient"),
    ]
    
    for module_path, func_name in http_paths:
        test_import(module_path, func_name)
    
    # Check what's in client module if it exists
    print("\n=== Detailed Client Module Analysis ===")
    try:
        import mcp.client
        print(f"✅ mcp.client module found")
        print(f"   Contents: {[x for x in dir(mcp.client) if not x.startswith('_')]}")
        
        # Check submodules
        for item in dir(mcp.client):
            if not item.startswith('_'):
                try:
                    submodule = getattr(mcp.client, item)
                    if hasattr(submodule, '__module__'):
                        print(f"   - {item}: {type(submodule)}")
                except:
                    pass
                    
    except ImportError:
        print("❌ mcp.client not found")
    
    # Try to find any HTTP-related modules
    print("\n=== Searching for HTTP modules ===")
    try:
        import mcp.client as client_module
        for attr_name in dir(client_module):
            if 'http' in attr_name.lower():
                print(f"   Found HTTP-related: {attr_name}")
    except:
        pass
    
    print("\n=== Final Import Test ===")
    
    # Try the most common patterns
    import_tests = [
        "from mcp import ClientSession",
        "from mcp.client import ClientSession", 
        "from mcp import Client as ClientSession",
        "from mcp.client.streamable_http import streamablehttp_client",
        "from mcp.client import streamablehttp_client",
        "from mcp import streamablehttp_client",
    ]
    
    for test_import_str in import_tests:
        try:
            exec(test_import_str)
            print(f"✅ SUCCESS: {test_import_str}")
        except Exception as e:
            print(f"❌ FAILED: {test_import_str} - {e}")

if __name__ == "__main__":
    main()
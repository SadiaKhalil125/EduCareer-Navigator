#!/usr/bin/env python3
"""
MongoDB configuration settings
"""

import os
from typing import Optional

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "guidance_assistant")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "chat_history")

# Connection settings
MONGODB_CONNECT_TIMEOUT_MS = int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", "5000"))
MONGODB_SERVER_SELECTION_TIMEOUT_MS = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "5000"))
MONGODB_SOCKET_TIMEOUT_MS = int(os.getenv("MONGODB_SOCKET_TIMEOUT_MS", "10000"))

# Index settings
CREATE_INDEXES = os.getenv("CREATE_INDEXES", "true").lower() == "true"

# Logging
MONGODB_LOGGING = os.getenv("MONGODB_LOGGING", "false").lower() == "true"

def get_mongodb_config() -> dict:
    """Get MongoDB configuration as a dictionary."""
    return {
        "uri": MONGODB_URI,
        "database": MONGODB_DATABASE,
        "collection": MONGODB_COLLECTION,
        "connect_timeout_ms": MONGODB_CONNECT_TIMEOUT_MS,
        "server_selection_timeout_ms": MONGODB_SERVER_SELECTION_TIMEOUT_MS,
        "socket_timeout_ms": MONGODB_SOCKET_TIMEOUT_MS,
        "create_indexes": CREATE_INDEXES,
        "logging": MONGODB_LOGGING
    }

def validate_mongodb_config() -> bool:
    """Validate MongoDB configuration."""
    try:
        config = get_mongodb_config()
        
        # Basic validation
        if not config["uri"]:
            print("❌ MONGODB_URI is not set")
            return False
            
        if not config["database"]:
            print("❌ MONGODB_DATABASE is not set")
            return False
            
        if not config["collection"]:
            print("❌ MONGODB_COLLECTION is not set")
            return False
            
        print("✅ MongoDB configuration is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error validating MongoDB configuration: {e}")
        return False 
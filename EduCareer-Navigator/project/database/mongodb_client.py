#!/usr/bin/env python3
"""
Simple MongoDB client for storing chat history
"""

import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import json

class ChatHistoryDB:
    """Simple MongoDB client for chat history storage"""
    
    def __init__(self, connection_string: Optional[str] = None, database_name: str = "guidance_assistant"):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB connection string (defaults to localhost)
            database_name: Name of the database to use
        """
        self.connection_string = connection_string or "mongodb://localhost:27017/"
        self.database_name = database_name
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.chat_collection: Optional[Collection] = None
        
        # Connect to MongoDB
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            self.chat_collection = self.db["chat_history"]
            
            # Create indexes for better performance
            self.chat_collection.create_index("thread_id")
            self.chat_collection.create_index("timestamp")
            self.chat_collection.create_index("user_id")
            
            print(f"✅ Connected to MongoDB database: {self.database_name}")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    def save_chat_message(self, thread_id: str, role: str, content: str, 
                         user_id: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
        """
        Save a single chat message
        
        Args:
            thread_id: Unique identifier for the chat session
            role: Role of the message sender ('user' or 'assistant')
            content: Message content
            user_id: Optional user identifier
            metadata: Optional additional metadata
            
        Returns:
            Message ID
        """
        if self.chat_collection is None:
            raise Exception("Database not connected")
        
        message_doc = {
            "thread_id": thread_id,
            "role": role,
            "content": content,
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        result = self.chat_collection.insert_one(message_doc)
        return str(result.inserted_id)
    
    def save_chat_session(self, thread_id: str, messages: List[Dict], 
                         user_id: Optional[str] = None, metadata: Optional[Dict] = None) -> List[str]:
        """
        Save an entire chat session
        
        Args:
            thread_id: Unique identifier for the chat session
            messages: List of message dictionaries with 'role' and 'content'
            user_id: Optional user identifier
            metadata: Optional additional metadata
            
        Returns:
            List of message IDs
        """
        if self.chat_collection is None:
            raise Exception("Database not connected")
        
        message_ids = []
        timestamp = datetime.utcnow()
        
        for i, message in enumerate(messages):
            if message.get("role") == "system":
                continue  # Skip system messages
                
            message_doc = {
                "thread_id": thread_id,
                "role": message["role"],
                "content": message["content"],
                "user_id": user_id,
                "timestamp": timestamp,
                "message_order": i,
                "metadata": metadata or {}
            }
            
            result = self.chat_collection.insert_one(message_doc)
            message_ids.append(str(result.inserted_id))
        
        return message_ids
    
    def get_chat_history(self, thread_id: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Retrieve chat history for a specific thread
        
        Args:
            thread_id: Thread identifier
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of chat messages
        """
        if self.chat_collection is None:
            raise Exception("Database not connected")
        
        query = {"thread_id": thread_id}
        cursor = self.chat_collection.find(query).sort("timestamp", 1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        messages = []
        for doc in cursor:
            # Convert ObjectId to string and datetime to ISO format
            doc["_id"] = str(doc["_id"])
            doc["timestamp"] = doc["timestamp"].isoformat()
            messages.append(doc)
        
        return messages
    
    def get_user_chat_sessions(self, user_id: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all chat sessions for a specific user
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions to retrieve
            
        Returns:
            List of chat sessions
        """
        if self.chat_collection is None:
            raise Exception("Database not connected")
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$thread_id",
                "last_message": {"$last": "$$ROOT"},
                "message_count": {"$sum": 1},
                "first_message": {"$first": "$$ROOT"}
            }},
            {"$sort": {"last_message.timestamp": -1}}
        ]
        
        if limit:
            pipeline.append({"$limit": limit})
        
        sessions = []
        for doc in self.chat_collection.aggregate(pipeline):
            session = {
                "thread_id": doc["_id"],
                "message_count": doc["message_count"],
                "last_message_time": doc["last_message"]["timestamp"].isoformat(),
                "first_message_time": doc["first_message"]["timestamp"].isoformat()
            }
            sessions.append(session)
        
        return sessions
    
    def delete_chat_session(self, thread_id: str) -> bool:
        """
        Delete all messages for a specific chat session
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            True if successful
        """
        if self.chat_collection is None:
            raise Exception("Database not connected")
        
        result = self.chat_collection.delete_many({"thread_id": thread_id})
        return result.deleted_count > 0
    
    def delete_user_chat_history(self, user_id: str) -> bool:
        """
        Delete all chat history for a specific user
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful
        """
        if self.chat_collection is None:
            raise Exception("Database not connected")
        
        result = self.chat_collection.delete_many({"user_id": user_id})
        return result.deleted_count > 0
    
    def search_chat_history(self, query: str, user_id: Optional[str] = None, 
                           limit: Optional[int] = None) -> List[Dict]:
        """
        Search chat history by content
        
        Args:
            query: Search query
            user_id: Optional user filter
            limit: Maximum number of results
            
        Returns:
            List of matching messages
        """
        if self.chat_collection is None:
            raise Exception("Database not connected")
        
        search_filter = {"content": {"$regex": query, "$options": "i"}}
        if user_id:
            search_filter["user_id"] = user_id
        
        cursor = self.chat_collection.find(search_filter).sort("timestamp", -1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        messages = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            doc["timestamp"] = doc["timestamp"].isoformat()
            messages.append(doc)
        
        return messages
    
    def get_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get chat statistics
        
        Args:
            user_id: Optional user filter
            
        Returns:
            Dictionary with statistics
        """
        if self.chat_collection is None:
            raise Exception("Database not connected")
        
        match_filter = {}
        if user_id:
            match_filter["user_id"] = user_id
        
        pipeline = [
            {"$match": match_filter},
            {"$group": {
                "_id": None,
                "total_messages": {"$sum": 1},
                "unique_threads": {"$addToSet": "$thread_id"},
                "unique_users": {"$addToSet": "$user_id"}
            }},
            {"$project": {
                "total_messages": 1,
                "unique_threads": {"$size": "$unique_threads"},
                "unique_users": {"$size": "$unique_users"}
            }}
        ]
        
        result = list(self.chat_collection.aggregate(pipeline))
        
        if result:
            stats = result[0]
            stats.pop("_id", None)
        else:
            stats = {
                "total_messages": 0,
                "unique_threads": 0,
                "unique_users": 0
            }
        
        return stats
    
    def close(self):
        """Close the MongoDB connection"""
        if self.client is not None:
            self.client.close()
            print("✅ MongoDB connection closed")

# Global instance for easy access
chat_db = None

def get_chat_db() -> ChatHistoryDB:
    """Get or create the global chat database instance"""
    global chat_db
    if chat_db is None:
        # Try to get connection string from environment variable
        connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        database_name = os.getenv("MONGODB_DATABASE", "guidance_assistant")
        chat_db = ChatHistoryDB(connection_string, database_name)
    return chat_db

def close_chat_db():
    """Close the global chat database connection"""
    global chat_db
    if chat_db is not None:
        chat_db.close()
        chat_db = None 
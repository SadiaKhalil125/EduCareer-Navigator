"""
Database utilities for the Guidance Assistant
"""

from .mongodb_client import ChatHistoryDB, get_chat_db, close_chat_db

__all__ = ['ChatHistoryDB', 'get_chat_db', 'close_chat_db'] 
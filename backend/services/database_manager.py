"""
Database Manager Service for SQLite and ChromaDB
"""

import sqlite3
import json
import logging
import asyncio
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
import os

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.sqlite_db_path = "body_language_translator.db"
        self.chroma_db_path = "./chroma_db"
        self.sqlite_conn = None
        self.chroma_client = None
        self.chroma_collection = None
        
    async def initialize(self):
        """Initialize both SQLite and ChromaDB connections"""
        try:
            # Initialize SQLite
            await self._init_sqlite()
            
            # Initialize ChromaDB
            await self._init_chromadb()
            
            logger.info("Database Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Database Manager: {str(e)}")
            raise

    async def _init_sqlite(self):
        """Initialize SQLite database and create tables"""
        try:
            self.sqlite_conn = sqlite3.connect(self.sqlite_db_path)
            self.sqlite_conn.row_factory = sqlite3.Row
            
            # Create tables
            await self._create_sqlite_tables()
            
            logger.info("SQLite database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing SQLite: {str(e)}")
            raise

    async def _init_chromadb(self):
        """Initialize ChromaDB for vector storage"""
        try:
            # Create ChromaDB client
            self.chroma_client = chromadb.PersistentClient(
                path=self.chroma_db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection for body language embeddings
            try:
                self.chroma_collection = self.chroma_client.get_collection("body_language_embeddings")
            except:
                self.chroma_collection = self.chroma_client.create_collection(
                    name="body_language_embeddings",
                    metadata={"description": "Body language gesture embeddings"}
                )
            
            logger.info("ChromaDB initialized")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            raise

    async def _create_sqlite_tables(self):
        """Create SQLite tables"""
        cursor = self.sqlite_conn.cursor()
        
        # Translation sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS translation_sessions (
                session_id TEXT PRIMARY KEY,
                translation_type TEXT NOT NULL,
                input_type TEXT NOT NULL,
                output_type TEXT NOT NULL,
                input_data TEXT NOT NULL,
                output_data TEXT NOT NULL,
                confidence REAL,
                processing_time REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                context TEXT
            )
        """)
        
        # User feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                feedback_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                accuracy_rating INTEGER,
                speed_rating INTEGER,
                comments TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES translation_sessions (session_id)
            )
        """)
        
        # User profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                preferred_language TEXT DEFAULT 'en',
                accessibility_settings TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Gesture patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gesture_patterns (
                pattern_id TEXT PRIMARY KEY,
                gesture_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence_threshold REAL DEFAULT 0.7,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # System logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                log_id TEXT PRIMARY KEY,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                user_id TEXT
            )
        """)
        
        self.sqlite_conn.commit()

    async def store_translation_session(self, input_type: str, output_type: str, 
                                      input_data: Dict[str, Any], output_data: Dict[str, Any],
                                      confidence: float = 0.0, processing_time: float = 0.0,
                                      user_id: Optional[str] = None, context: Optional[str] = None) -> str:
        """
        Store a translation session in SQLite
        """
        try:
            session_id = str(uuid.uuid4())
            translation_type = f"{input_type}_to_{output_type}"
            
            cursor = self.sqlite_conn.cursor()
            cursor.execute("""
                INSERT INTO translation_sessions 
                (session_id, translation_type, input_type, output_type, input_data, output_data, 
                 confidence, processing_time, user_id, context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, translation_type, input_type, output_type,
                json.dumps(input_data), json.dumps(output_data),
                confidence, processing_time, user_id, context
            ))
            
            self.sqlite_conn.commit()
            
            # Store embeddings in ChromaDB if applicable
            await self._store_embeddings(session_id, input_data, output_data)
            
            logger.info(f"Translation session stored: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error storing translation session: {str(e)}")
            raise

    async def get_translation_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a translation session by ID
        """
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("""
                SELECT * FROM translation_sessions WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "session_id": row["session_id"],
                    "translation_type": row["translation_type"],
                    "input_type": row["input_type"],
                    "output_type": row["output_type"],
                    "input_data": json.loads(row["input_data"]),
                    "output_data": json.loads(row["output_data"]),
                    "confidence": row["confidence"],
                    "processing_time": row["processing_time"],
                    "timestamp": row["timestamp"],
                    "user_id": row["user_id"],
                    "context": row["context"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving translation session: {str(e)}")
            return None

    async def get_recent_sessions(self, limit: int = 10, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get recent translation sessions
        """
        try:
            cursor = self.sqlite_conn.cursor()
            
            if user_id:
                cursor.execute("""
                    SELECT * FROM translation_sessions 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (user_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM translation_sessions 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
            
            rows = cursor.fetchall()
            sessions = []
            
            for row in rows:
                sessions.append({
                    "session_id": row["session_id"],
                    "translation_type": row["translation_type"],
                    "input_type": row["input_type"],
                    "output_type": row["output_type"],
                    "confidence": row["confidence"],
                    "timestamp": row["timestamp"],
                    "user_id": row["user_id"]
                })
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error retrieving recent sessions: {str(e)}")
            return []

    async def store_feedback(self, session_id: str, rating: int, comments: Optional[str] = None,
                           accuracy_rating: Optional[int] = None, speed_rating: Optional[int] = None) -> str:
        """
        Store user feedback for a translation session
        """
        try:
            feedback_id = str(uuid.uuid4())
            
            cursor = self.sqlite_conn.cursor()
            cursor.execute("""
                INSERT INTO user_feedback 
                (feedback_id, session_id, rating, accuracy_rating, speed_rating, comments)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (feedback_id, session_id, rating, accuracy_rating, speed_rating, comments))
            
            self.sqlite_conn.commit()
            
            logger.info(f"Feedback stored: {feedback_id}")
            return feedback_id
            
        except Exception as e:
            logger.error(f"Error storing feedback: {str(e)}")
            raise

    async def get_session_feedback(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get feedback for a specific session
        """
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("""
                SELECT * FROM user_feedback WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "feedback_id": row["feedback_id"],
                    "session_id": row["session_id"],
                    "rating": row["rating"],
                    "accuracy_rating": row["accuracy_rating"],
                    "speed_rating": row["speed_rating"],
                    "comments": row["comments"],
                    "timestamp": row["timestamp"]
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving feedback: {str(e)}")
            return None

    async def store_gesture_pattern(self, gesture_type: str, pattern_data: Dict[str, Any], 
                                  confidence_threshold: float = 0.7) -> str:
        """
        Store a gesture pattern for future recognition
        """
        try:
            pattern_id = str(uuid.uuid4())
            
            cursor = self.sqlite_conn.cursor()
            cursor.execute("""
                INSERT INTO gesture_patterns 
                (pattern_id, gesture_type, pattern_data, confidence_threshold)
                VALUES (?, ?, ?, ?)
            """, (pattern_id, gesture_type, json.dumps(pattern_data), confidence_threshold))
            
            self.sqlite_conn.commit()
            
            logger.info(f"Gesture pattern stored: {pattern_id}")
            return pattern_id
            
        except Exception as e:
            logger.error(f"Error storing gesture pattern: {str(e)}")
            raise

    async def get_gesture_patterns(self, gesture_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get gesture patterns for recognition
        """
        try:
            cursor = self.sqlite_conn.cursor()
            
            if gesture_type:
                cursor.execute("""
                    SELECT * FROM gesture_patterns WHERE gesture_type = ?
                """, (gesture_type,))
            else:
                cursor.execute("SELECT * FROM gesture_patterns")
            
            rows = cursor.fetchall()
            patterns = []
            
            for row in rows:
                patterns.append({
                    "pattern_id": row["pattern_id"],
                    "gesture_type": row["gesture_type"],
                    "pattern_data": json.loads(row["pattern_data"]),
                    "confidence_threshold": row["confidence_threshold"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error retrieving gesture patterns: {str(e)}")
            return []

    async def _store_embeddings(self, session_id: str, input_data: Dict[str, Any], output_data: Dict[str, Any]):
        """
        Store embeddings in ChromaDB for similarity search
        """
        try:
            if not self.chroma_collection:
                return
            
            # Extract text content for embedding
            text_content = ""
            
            if "text" in input_data:
                text_content += f"Input: {input_data['text']} "
            if "text" in output_data:
                text_content += f"Output: {output_data['text']}"
            
            if text_content.strip():
                # Generate simple embedding (in production, use proper embedding model)
                embedding = self._generate_simple_embedding(text_content)
                
                # Store in ChromaDB
                self.chroma_collection.add(
                    embeddings=[embedding],
                    documents=[text_content],
                    metadatas=[{
                        "session_id": session_id,
                        "input_type": input_data.get("type", "unknown"),
                        "output_type": output_data.get("type", "unknown"),
                        "timestamp": datetime.now().isoformat()
                    }],
                    ids=[session_id]
                )
                
                logger.info(f"Embeddings stored for session: {session_id}")
                
        except Exception as e:
            logger.error(f"Error storing embeddings: {str(e)}")

    def _generate_simple_embedding(self, text: str) -> List[float]:
        """
        Generate a simple embedding for text (placeholder implementation)
        In production, use proper embedding models like sentence-transformers
        """
        # This is a simplified embedding generation
        # In a real implementation, you would use a proper embedding model
        import hashlib
        
        # Generate a hash-based embedding
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert hex to list of floats
        embedding = []
        for i in range(0, len(hash_hex), 2):
            if len(embedding) >= 384:  # Standard embedding size
                break
            embedding.append(float(int(hash_hex[i:i+2], 16)) / 255.0)
        
        # Pad or truncate to 384 dimensions
        while len(embedding) < 384:
            embedding.append(0.0)
        
        return embedding[:384]

    async def search_similar_sessions(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar translation sessions using ChromaDB
        """
        try:
            if not self.chroma_collection:
                return []
            
            # Generate embedding for query
            query_embedding = self._generate_simple_embedding(query_text)
            
            # Search in ChromaDB
            results = self.chroma_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            
            similar_sessions = []
            if results["ids"] and results["ids"][0]:
                for i, session_id in enumerate(results["ids"][0]):
                    session = await self.get_translation_session(session_id)
                    if session:
                        session["similarity_score"] = results["distances"][0][i] if results["distances"] else 0.0
                        similar_sessions.append(session)
            
            return similar_sessions
            
        except Exception as e:
            logger.error(f"Error searching similar sessions: {str(e)}")
            return []

    async def log_system_event(self, level: str, message: str, session_id: Optional[str] = None,
                             user_id: Optional[str] = None) -> str:
        """
        Log system events
        """
        try:
            log_id = str(uuid.uuid4())
            
            cursor = self.sqlite_conn.cursor()
            cursor.execute("""
                INSERT INTO system_logs 
                (log_id, level, message, session_id, user_id)
                VALUES (?, ?, ?, ?, ?)
            """, (log_id, level, message, session_id, user_id))
            
            self.sqlite_conn.commit()
            
            return log_id
            
        except Exception as e:
            logger.error(f"Error logging system event: {str(e)}")
            raise

    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics
        """
        try:
            cursor = self.sqlite_conn.cursor()
            
            # Total sessions
            cursor.execute("SELECT COUNT(*) as total FROM translation_sessions")
            total_sessions = cursor.fetchone()["total"]
            
            # Sessions by type
            cursor.execute("""
                SELECT translation_type, COUNT(*) as count 
                FROM translation_sessions 
                GROUP BY translation_type
            """)
            sessions_by_type = {row["translation_type"]: row["count"] for row in cursor.fetchall()}
            
            # Average confidence
            cursor.execute("SELECT AVG(confidence) as avg_confidence FROM translation_sessions")
            avg_confidence = cursor.fetchone()["avg_confidence"] or 0.0
            
            # Recent activity
            cursor.execute("""
                SELECT COUNT(*) as recent_count 
                FROM translation_sessions 
                WHERE timestamp > datetime('now', '-24 hours')
            """)
            recent_activity = cursor.fetchone()["recent_count"]
            
            return {
                "total_sessions": total_sessions,
                "sessions_by_type": sessions_by_type,
                "average_confidence": round(avg_confidence, 3),
                "recent_activity_24h": recent_activity,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
            return {}

    async def close(self):
        """Close database connections"""
        try:
            if self.sqlite_conn:
                self.sqlite_conn.close()
            
            logger.info("Database connections closed")
            
        except Exception as e:
            logger.error(f"Error closing database connections: {str(e)}")

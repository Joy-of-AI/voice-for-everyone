"""
WebSocket Manager for real-time body language translation
"""

import json
import logging
from typing import Dict, List, Any
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_data: Dict[WebSocket, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_data[websocket] = {
            "connected_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "session_id": None,
            "user_id": None
        }
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_data:
            del self.connection_data[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        try:
            # Add timestamp if not present
            if "timestamp" not in message:
                message["timestamp"] = datetime.now().isoformat()
            
            # Update last activity
            if websocket in self.connection_data:
                self.connection_data[websocket]["last_activity"] = datetime.now().isoformat()
            
            await websocket.send_text(json.dumps(message))
            
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")
            await self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected WebSockets"""
        disconnected = []
        
        for websocket in self.active_connections:
            try:
                # Add timestamp if not present
                if "timestamp" not in message:
                    message["timestamp"] = datetime.now().isoformat()
                
                # Update last activity
                if websocket in self.connection_data:
                    self.connection_data[websocket]["last_activity"] = datetime.now().isoformat()
                
                await websocket.send_text(json.dumps(message))
                
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")
                disconnected.append(websocket)
        
        # Remove disconnected connections
        for websocket in disconnected:
            self.disconnect(websocket)

    async def broadcast_to_session(self, message: Dict[str, Any], session_id: str):
        """Broadcast message to all connections in a specific session"""
        disconnected = []
        
        for websocket in self.active_connections:
            try:
                if (websocket in self.connection_data and 
                    self.connection_data[websocket].get("session_id") == session_id):
                    
                    # Add timestamp if not present
                    if "timestamp" not in message:
                        message["timestamp"] = datetime.now().isoformat()
                    
                    # Update last activity
                    self.connection_data[websocket]["last_activity"] = datetime.now().isoformat()
                    
                    await websocket.send_text(json.dumps(message))
                    
            except Exception as e:
                logger.error(f"Error broadcasting to session: {str(e)}")
                disconnected.append(websocket)
        
        # Remove disconnected connections
        for websocket in disconnected:
            self.disconnect(websocket)

    def set_session_id(self, websocket: WebSocket, session_id: str):
        """Set session ID for a WebSocket connection"""
        if websocket in self.connection_data:
            self.connection_data[websocket]["session_id"] = session_id

    def set_user_id(self, websocket: WebSocket, user_id: str):
        """Set user ID for a WebSocket connection"""
        if websocket in self.connection_data:
            self.connection_data[websocket]["user_id"] = user_id

    def get_connection_info(self, websocket: WebSocket) -> Dict[str, Any]:
        """Get connection information"""
        return self.connection_data.get(websocket, {})

    def get_active_connections_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)

    def get_connections_by_session(self, session_id: str) -> List[WebSocket]:
        """Get all connections for a specific session"""
        return [
            websocket for websocket in self.active_connections
            if (websocket in self.connection_data and 
                self.connection_data[websocket].get("session_id") == session_id)
        ]

    def get_connections_by_user(self, user_id: str) -> List[WebSocket]:
        """Get all connections for a specific user"""
        return [
            websocket for websocket in self.active_connections
            if (websocket in self.connection_data and 
                self.connection_data[websocket].get("user_id") == user_id)
        ]

    async def send_system_message(self, websocket: WebSocket, message_type: str, content: str):
        """Send system message to WebSocket"""
        system_message = {
            "type": "system",
            "message_type": message_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(system_message, websocket)

    async def send_error_message(self, websocket: WebSocket, error_message: str, error_code: str = None):
        """Send error message to WebSocket"""
        error_msg = {
            "type": "error",
            "message": error_message,
            "error_code": error_code,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(error_msg, websocket)

    async def send_translation_result(self, websocket: WebSocket, translation_data: Dict[str, Any]):
        """Send translation result to WebSocket"""
        translation_message = {
            "type": "translation_result",
            "data": translation_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(translation_message, websocket)

    async def send_body_instructions(self, websocket: WebSocket, instructions: List[Dict[str, Any]]):
        """Send body language instructions to WebSocket"""
        instructions_message = {
            "type": "body_instructions",
            "instructions": instructions,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(instructions_message, websocket)

    async def send_audio_transcription(self, websocket: WebSocket, transcription: Dict[str, Any]):
        """Send audio transcription to WebSocket"""
        transcription_message = {
            "type": "audio_transcription",
            "transcription": transcription,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(transcription_message, websocket)

    async def send_confidence_update(self, websocket: WebSocket, confidence: float, gesture_type: str):
        """Send confidence update to WebSocket"""
        confidence_message = {
            "type": "confidence_update",
            "confidence": confidence,
            "gesture_type": gesture_type,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(confidence_message, websocket)

    async def send_gesture_detected(self, websocket: WebSocket, gesture_data: Dict[str, Any]):
        """Send gesture detection notification to WebSocket"""
        gesture_message = {
            "type": "gesture_detected",
            "gesture": gesture_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(gesture_message, websocket)

    def cleanup_inactive_connections(self, max_inactive_minutes: int = 30):
        """Clean up inactive connections"""
        current_time = datetime.now()
        inactive_connections = []
        
        for websocket in self.active_connections:
            if websocket in self.connection_data:
                last_activity = datetime.fromisoformat(
                    self.connection_data[websocket]["last_activity"]
                )
                inactive_minutes = (current_time - last_activity).total_seconds() / 60
                
                if inactive_minutes > max_inactive_minutes:
                    inactive_connections.append(websocket)
        
        for websocket in inactive_connections:
            logger.info(f"Cleaning up inactive connection: {websocket}")
            self.disconnect(websocket)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        stats = {
            "total_connections": len(self.active_connections),
            "connections_by_session": {},
            "connections_by_user": {},
            "oldest_connection": None,
            "newest_connection": None
        }
        
        if self.connection_data:
            # Count connections by session
            for data in self.connection_data.values():
                session_id = data.get("session_id")
                if session_id:
                    stats["connections_by_session"][session_id] = stats["connections_by_session"].get(session_id, 0) + 1
                
                user_id = data.get("user_id")
                if user_id:
                    stats["connections_by_user"][user_id] = stats["connections_by_user"].get(user_id, 0) + 1
            
            # Find oldest and newest connections
            connection_times = [
                datetime.fromisoformat(data["connected_at"]) 
                for data in self.connection_data.values()
            ]
            
            if connection_times:
                stats["oldest_connection"] = min(connection_times).isoformat()
                stats["newest_connection"] = max(connection_times).isoformat()
        
        return stats

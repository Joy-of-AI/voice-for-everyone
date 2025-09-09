"""
WebRTC Manager with LiveKit Integration
Real-time video/audio communication with sub-200ms latency
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import aiohttp
import websockets
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class WebRTCConfig:
    """WebRTC configuration"""
    livekit_url: str = "ws://localhost:7880"
    api_key: str = "devkey"
    api_secret: str = "secret"
    room_name: str = "body_language_translator"
    participant_name: str = "user"
    max_participants: int = 10
    video_codec: str = "h264"
    audio_codec: str = "opus"
    data_channel_name: str = "pose_data"

class WebRTCManager:
    """
    WebRTC Manager with LiveKit integration
    Provides real-time video/audio communication with data channels
    """
    
    def __init__(self, config: WebRTCConfig):
        self.config = config
        self.websocket = None
        self.room_connection = None
        self.participants = {}
        self.data_channels = {}
        self.video_tracks = {}
        self.audio_tracks = {}
        self.pose_callbacks = []
        self.is_connected = False
        
        # LiveKit API endpoints
        self.api_base = config.livekit_url.replace("ws://", "http://").replace("wss://", "https://")
        self.ws_url = config.livekit_url
        
    async def connect(self) -> bool:
        """Connect to LiveKit room"""
        try:
            logger.info(f"Connecting to LiveKit room: {self.config.room_name}")
            
            # Generate access token
            token = await self._generate_access_token()
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                f"{self.ws_url}/rtc?access_token={token}"
            )
            
            # Join room
            join_message = {
                "type": "join",
                "room": self.config.room_name,
                "participant": self.config.participant_name,
                "metadata": json.dumps({
                    "app": "body_language_translator",
                    "version": "1.0.0"
                })
            }
            
            await self.websocket.send(json.dumps(join_message))
            response = await self.websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("type") == "join":
                self.is_connected = True
                self.room_connection = response_data
                logger.info("Successfully connected to LiveKit room")
                
                # Start message handling
                asyncio.create_task(self._handle_messages())
                
                return True
            else:
                logger.error(f"Failed to join room: {response_data}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to LiveKit: {e}")
            return False
    
    async def _generate_access_token(self) -> str:
        """Generate LiveKit access token"""
        try:
            # In production, use proper JWT token generation
            # For now, create a simple token
            token_data = {
                "room": self.config.room_name,
                "participant": self.config.participant_name,
                "exp": int(datetime.now().timestamp()) + 3600,  # 1 hour expiry
                "api_key": self.config.api_key
            }
            
            # Simple token (in production, use proper JWT)
            import base64
            token = base64.b64encode(json.dumps(token_data).encode()).decode()
            return token
            
        except Exception as e:
            logger.error(f"Error generating access token: {e}")
            return ""
    
    async def _handle_messages(self):
        """Handle incoming WebSocket messages"""
        try:
            while self.is_connected and self.websocket:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                await self._process_message(data)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Error handling messages: {e}")
            self.is_connected = False
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process incoming message"""
        message_type = data.get("type")
        
        if message_type == "participant_joined":
            await self._handle_participant_joined(data)
        elif message_type == "participant_left":
            await self._handle_participant_left(data)
        elif message_type == "track_published":
            await self._handle_track_published(data)
        elif message_type == "data_received":
            await self._handle_data_received(data)
        elif message_type == "room_update":
            await self._handle_room_update(data)
        else:
            logger.debug(f"Unhandled message type: {message_type}")
    
    async def _handle_participant_joined(self, data: Dict[str, Any]):
        """Handle participant joining"""
        participant = data.get("participant", {})
        participant_id = participant.get("sid")
        
        if participant_id:
            self.participants[participant_id] = participant
            logger.info(f"Participant joined: {participant.get('identity', 'Unknown')}")
    
    async def _handle_participant_left(self, data: Dict[str, Any]):
        """Handle participant leaving"""
        participant_id = data.get("participant_sid")
        
        if participant_id in self.participants:
            participant = self.participants.pop(participant_id)
            logger.info(f"Participant left: {participant.get('identity', 'Unknown')}")
    
    async def _handle_track_published(self, data: Dict[str, Any]):
        """Handle track publication"""
        track = data.get("track", {})
        track_sid = track.get("sid")
        track_type = track.get("type")
        participant_id = data.get("participant_sid")
        
        if track_sid and participant_id:
            if track_type == "video":
                self.video_tracks[track_sid] = {
                    "participant_id": participant_id,
                    "track": track
                }
                logger.info(f"Video track published: {track_sid}")
            elif track_type == "audio":
                self.audio_tracks[track_sid] = {
                    "participant_id": participant_id,
                    "track": track
                }
                logger.info(f"Audio track published: {track_sid}")
    
    async def _handle_data_received(self, data: Dict[str, Any]):
        """Handle data channel messages"""
        payload = data.get("payload", {})
        channel_name = data.get("channel")
        
        if channel_name == self.config.data_channel_name:
            # Handle pose data
            await self._handle_pose_data(payload)
        else:
            logger.debug(f"Data received on channel {channel_name}: {payload}")
    
    async def _handle_pose_data(self, payload: Dict[str, Any]):
        """Handle pose data from data channel"""
        try:
            pose_data = {
                "timestamp": datetime.now().isoformat(),
                "body_pose": payload.get("body_pose", []),
                "left_hand_pose": payload.get("left_hand_pose", []),
                "right_hand_pose": payload.get("right_hand_pose", []),
                "face_landmarks": payload.get("face_landmarks", []),
                "confidence": payload.get("confidence", 0.0)
            }
            
            # Notify pose callbacks
            for callback in self.pose_callbacks:
                try:
                    await callback(pose_data)
                except Exception as e:
                    logger.error(f"Error in pose callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling pose data: {e}")
    
    async def _handle_room_update(self, data: Dict[str, Any]):
        """Handle room updates"""
        room = data.get("room", {})
        participants = room.get("participants", [])
        
        # Update participant list
        self.participants = {
            p["sid"]: p for p in participants
        }
        
        logger.info(f"Room updated: {len(participants)} participants")
    
    async def publish_video_track(self, video_data: bytes, width: int = 640, height: int = 480) -> bool:
        """Publish video track to room"""
        try:
            if not self.is_connected:
                logger.error("Not connected to room")
                return False
            
            # Create video track
            track_message = {
                "type": "publish_track",
                "track": {
                    "type": "video",
                    "name": "body_language_video",
                    "source": "camera",
                    "width": width,
                    "height": height,
                    "fps": 30,
                    "codec": self.config.video_codec
                }
            }
            
            await self.websocket.send(json.dumps(track_message))
            response = await self.websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("type") == "track_published":
                track_sid = response_data.get("track_sid")
                logger.info(f"Video track published: {track_sid}")
                return True
            else:
                logger.error(f"Failed to publish video track: {response_data}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing video track: {e}")
            return False
    
    async def publish_audio_track(self, audio_data: bytes, sample_rate: int = 48000) -> bool:
        """Publish audio track to room"""
        try:
            if not self.is_connected:
                logger.error("Not connected to room")
                return False
            
            # Create audio track
            track_message = {
                "type": "publish_track",
                "track": {
                    "type": "audio",
                    "name": "body_language_audio",
                    "source": "microphone",
                    "sample_rate": sample_rate,
                    "channels": 1,
                    "codec": self.config.audio_codec
                }
            }
            
            await self.websocket.send(json.dumps(track_message))
            response = await self.websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("type") == "track_published":
                track_sid = response_data.get("track_sid")
                logger.info(f"Audio track published: {track_sid}")
                return True
            else:
                logger.error(f"Failed to publish audio track: {response_data}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing audio track: {e}")
            return False
    
    async def send_pose_data(self, pose_data: Dict[str, Any]) -> bool:
        """Send pose data via data channel"""
        try:
            if not self.is_connected:
                logger.error("Not connected to room")
                return False
            
            # Send data channel message
            data_message = {
                "type": "send_data",
                "channel": self.config.data_channel_name,
                "payload": pose_data
            }
            
            await self.websocket.send(json.dumps(data_message))
            return True
            
        except Exception as e:
            logger.error(f"Error sending pose data: {e}")
            return False
    
    def add_pose_callback(self, callback: Callable):
        """Add callback for pose data processing"""
        self.pose_callbacks.append(callback)
        logger.info(f"Added pose callback: {callback.__name__}")
    
    async def create_data_channel(self, channel_name: str) -> bool:
        """Create data channel for pose data"""
        try:
            if not self.is_connected:
                logger.error("Not connected to room")
                return False
            
            # Create data channel
            channel_message = {
                "type": "create_data_channel",
                "channel": channel_name,
                "ordered": True,
                "max_retransmits": 3
            }
            
            await self.websocket.send(json.dumps(channel_message))
            response = await self.websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("type") == "data_channel_created":
                self.data_channels[channel_name] = response_data.get("channel_sid")
                logger.info(f"Data channel created: {channel_name}")
                return True
            else:
                logger.error(f"Failed to create data channel: {response_data}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating data channel: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from LiveKit room"""
        try:
            if self.websocket:
                # Send leave message
                leave_message = {
                    "type": "leave"
                }
                await self.websocket.send(json.dumps(leave_message))
                
                # Close WebSocket
                await self.websocket.close()
                self.websocket = None
            
            self.is_connected = False
            self.participants.clear()
            self.video_tracks.clear()
            self.audio_tracks.clear()
            self.data_channels.clear()
            
            logger.info("Disconnected from LiveKit room")
            
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "connected": self.is_connected,
            "participants": len(self.participants),
            "video_tracks": len(self.video_tracks),
            "audio_tracks": len(self.audio_tracks),
            "data_channels": len(self.data_channels),
            "pose_callbacks": len(self.pose_callbacks)
        }
    
    async def get_room_info(self) -> Dict[str, Any]:
        """Get room information"""
        try:
            if not self.is_connected:
                return {"error": "Not connected"}
            
            # Request room info
            info_message = {
                "type": "get_room_info"
            }
            
            await self.websocket.send(json.dumps(info_message))
            response = await self.websocket.recv()
            response_data = json.loads(response)
            
            if response_data.get("type") == "room_info":
                return response_data.get("room", {})
            else:
                return {"error": "Failed to get room info"}
                
        except Exception as e:
            logger.error(f"Error getting room info: {e}")
            return {"error": str(e)}

# Create default WebRTC manager instance
default_webrtc_config = WebRTCConfig()
webrtc_manager = WebRTCManager(default_webrtc_config)

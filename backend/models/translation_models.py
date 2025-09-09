"""
Pydantic models for body language translation API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TranslationType(str, Enum):
    BODY_TO_TEXT = "body_to_text"
    TEXT_TO_BODY = "text_to_body"
    AUDIO_TO_BODY = "audio_to_body"
    BODY_TO_AUDIO = "body_to_audio"

class GestureType(str, Enum):
    HAND = "hand"
    FACE = "face"
    BODY = "body"
    POSE = "pose"

class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to be translated to body language")
    context: Optional[str] = Field(None, description="Additional context for better translation")
    language: Optional[str] = Field("en", description="Target language for translation")
    emotion: Optional[str] = Field(None, description="Desired emotion to convey")

class TranslationResponse(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    translated_text: str = Field(..., description="Translated text from body language")
    confidence: float = Field(..., description="Confidence score of translation (0-1)")
    timestamp: str = Field(..., description="Translation timestamp")
    detected_gestures: Optional[List[str]] = Field(None, description="List of detected gestures")

class BodyLanguageData(BaseModel):
    gestures: List[Dict[str, Any]] = Field(..., description="Detected gestures and their data")
    pose_landmarks: Optional[List[Dict[str, float]]] = Field(None, description="Body pose landmarks")
    hand_landmarks: Optional[List[Dict[str, float]]] = Field(None, description="Hand landmarks")
    face_landmarks: Optional[List[Dict[str, float]]] = Field(None, description="Facial landmarks")
    timestamp: datetime = Field(default_factory=datetime.now)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)

class BodyLanguageInstruction(BaseModel):
    gesture_type: GestureType = Field(..., description="Type of gesture")
    description: str = Field(..., description="Human-readable description of the gesture")
    coordinates: Optional[Dict[str, Any]] = Field(None, description="Specific coordinates or positions")
    duration: Optional[float] = Field(None, description="Recommended duration in seconds")
    intensity: Optional[float] = Field(None, description="Gesture intensity (0-1)")
    sequence_order: Optional[int] = Field(None, description="Order in gesture sequence")

class AudioTranscription(BaseModel):
    text: str = Field(..., description="Transcribed text from audio")
    confidence: float = Field(..., description="Transcription confidence (0-1)")
    language: str = Field(..., description="Detected language")
    timestamp: datetime = Field(default_factory=datetime.now)
    audio_features: Optional[Dict[str, Any]] = Field(None, description="Audio analysis features")

class TranslationSession(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    translation_type: TranslationType = Field(..., description="Type of translation performed")
    input_data: Dict[str, Any] = Field(..., description="Original input data")
    output_data: Dict[str, Any] = Field(..., description="Translation output data")
    confidence: float = Field(..., description="Overall confidence score")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)
    user_feedback: Optional[Dict[str, Any]] = Field(None, description="User feedback on translation")

class UserFeedback(BaseModel):
    session_id: str = Field(..., description="Associated session ID")
    rating: int = Field(..., ge=1, le=5, description="User rating (1-5)")
    accuracy_rating: Optional[int] = Field(None, ge=1, le=5, description="Accuracy rating")
    speed_rating: Optional[int] = Field(None, ge=1, le=5, description="Speed rating")
    comments: Optional[str] = Field(None, description="Additional user comments")
    timestamp: datetime = Field(default_factory=datetime.now)

class RealTimeFrame(BaseModel):
    frame_data: str = Field(..., description="Base64 encoded frame data")
    frame_number: int = Field(..., description="Frame sequence number")
    timestamp: datetime = Field(default_factory=datetime.now)
    context: Optional[str] = Field(None, description="Additional context")

class WebSocketMessage(BaseModel):
    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(..., description="Message data")
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: Optional[str] = Field(None, description="Associated session ID")

class SystemHealth(BaseModel):
    status: str = Field(..., description="System status")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    active_sessions: int = Field(..., description="Number of active sessions")
    total_translations: int = Field(..., description="Total translations processed")
    uptime: float = Field(..., description="System uptime in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)

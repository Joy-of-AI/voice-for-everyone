"""
Comprehensive test suite for Body Language Translator Backend
"""

import pytest
import asyncio
import json
import base64
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import the services to test
from services.ai_translator import AITranslator
from services.body_language_processor import BodyLanguageProcessor
from services.audio_processor import AudioProcessor
from services.database_manager import DatabaseManager
from utils.websocket_manager import WebSocketManager
from models.translation_models import (
    TranslationRequest, TranslationResponse, BodyLanguageData,
    TranslationType, GestureType
)

class TestAITranslator:
    """Test AI Translator service"""
    
    @pytest.fixture
    async def ai_translator(self):
        """Create AI translator instance for testing"""
        translator = AITranslator()
        # Mock OpenAI client for testing
        translator.client = AsyncMock()
        return translator
    
    @pytest.mark.asyncio
    async def test_initialization(self, ai_translator):
        """Test AI translator initialization"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            await ai_translator.initialize()
            assert ai_translator.client is not None
    
    @pytest.mark.asyncio
    async def test_body_language_to_text(self, ai_translator):
        """Test body language to text translation"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "text": "Hello, how are you?",
            "confidence": 0.85,
            "detected_gestures": ["wave", "smile"]
        })
        ai_translator.client.chat.completions.create.return_value = mock_response
        
        # Test data
        body_language_data = {
            "gestures": [
                {"type": "wave", "confidence": 0.8, "description": "Hand waving gesture"},
                {"type": "smile", "confidence": 0.7, "description": "Facial smile"}
            ],
            "pose_landmarks": [{"x": 0.5, "y": 0.5, "z": 0.0}],
            "confidence_scores": {"wave": 0.8, "smile": 0.7}
        }
        
        result = await ai_translator.body_language_to_text(body_language_data, "greeting context")
        
        assert result["text"] == "Hello, how are you?"
        assert result["confidence"] == 0.85
        assert "wave" in result["detected_gestures"]
        assert "smile" in result["detected_gestures"]
    
    @pytest.mark.asyncio
    async def test_text_to_body_language(self, ai_translator):
        """Test text to body language translation"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps([
            {
                "gesture_type": "hand",
                "description": "Wave your hand from side to side",
                "duration": 2.0,
                "intensity": 0.7,
                "sequence_order": 1
            }
        ])
        ai_translator.client.chat.completions.create.return_value = mock_response
        
        result = await ai_translator.text_to_body_language("Hello", "greeting context")
        
        assert len(result) > 0
        assert result[0]["gesture_type"] == "hand"
        assert "wave" in result[0]["description"].lower()

class TestBodyLanguageProcessor:
    """Test Body Language Processor service"""
    
    @pytest.fixture
    def body_processor(self):
        """Create body language processor instance for testing"""
        return BodyLanguageProcessor()
    
    @pytest.mark.asyncio
    async def test_process_frame(self, body_processor):
        """Test frame processing"""
        # Create a simple test image (1x1 pixel)
        test_image_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf5\xa5\xa5\xd4\x00\x00\x00\x00IEND\xaeB`\x82'
        
        result = await body_processor.process_frame(test_image_bytes)
        
        assert "gestures" in result
        assert "pose_landmarks" in result
        assert "hand_landmarks" in result
        assert "face_landmarks" in result
        assert "timestamp" in result
    
    def test_gesture_detection_helpers(self, body_processor):
        """Test gesture detection helper methods"""
        # Test thumbs up detection
        landmarks = [
            {"x": 0.5, "y": 0.3},  # thumb tip
            {"x": 0.5, "y": 0.4},  # thumb joint
            {"x": 0.5, "y": 0.6},  # index tip
            {"x": 0.5, "y": 0.7},  # middle tip
            {"x": 0.5, "y": 0.5},  # index joint
            {"x": 0.5, "y": 0.6},  # middle joint
        ]
        
        # This should return False for the simplified test data
        assert body_processor._is_thumbs_up(landmarks) == False

class TestAudioProcessor:
    """Test Audio Processor service"""
    
    @pytest.fixture
    async def audio_processor(self):
        """Create audio processor instance for testing"""
        processor = AudioProcessor()
        return processor
    
    @pytest.mark.asyncio
    async def test_text_to_speech(self, audio_processor):
        """Test text to speech conversion"""
        with patch('pyttsx3.init') as mock_init:
            mock_engine = Mock()
            mock_init.return_value = mock_engine
            audio_processor.tts_engine = mock_engine
            
            # Create temporary file for testing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(b'test audio data')
                temp_file_path = temp_file.name
            
            try:
                with patch('builtins.open', return_value=Mock()) as mock_open:
                    mock_file = Mock()
                    mock_file.read.return_value = b'generated audio data'
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    result = await audio_processor.text_to_speech("Hello world")
                    
                    assert result == b'generated audio data'
                    mock_engine.save_to_file.assert_called_once()
                    mock_engine.runAndWait.assert_called_once()
                    
            finally:
                os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_speech_to_text(self, audio_processor):
        """Test speech to text conversion"""
        # Mock speech recognition
        with patch('speech_recognition.Recognizer') as mock_recognizer_class:
            mock_recognizer = Mock()
            mock_recognizer_class.return_value = mock_recognizer
            mock_recognizer.recognize_google.return_value = "Hello world"
            
            # Create temporary audio file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(b'test audio data')
                temp_file_path = temp_file.name
            
            try:
                with patch('speech_recognition.AudioFile') as mock_audio_file:
                    mock_source = Mock()
                    mock_audio_file.return_value.__enter__.return_value = mock_source
                    
                    result = await audio_processor.speech_to_text(b'test audio data')
                    
                    assert result["text"] == "Hello world"
                    assert result["confidence"] == 0.8
                    assert result["language"] == "en"
                    
            finally:
                os.unlink(temp_file_path)

class TestDatabaseManager:
    """Test Database Manager service"""
    
    @pytest.fixture
    async def db_manager(self):
        """Create database manager instance for testing"""
        manager = DatabaseManager()
        # Use in-memory SQLite for testing
        manager.sqlite_db_path = ":memory:"
        manager.chroma_db_path = "./test_chroma_db"
        return manager
    
    @pytest.mark.asyncio
    async def test_initialization(self, db_manager):
        """Test database initialization"""
        await db_manager.initialize()
        assert db_manager.sqlite_conn is not None
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_session(self, db_manager):
        """Test storing and retrieving translation sessions"""
        await db_manager.initialize()
        
        # Test data
        input_data = {"text": "Hello", "type": "text"}
        output_data = {"text": "Wave hand", "type": "gesture"}
        
        session_id = await db_manager.store_translation_session(
            "text", "body_language", input_data, output_data, 0.8, 1.5
        )
        
        assert session_id is not None
        
        # Retrieve session
        session = await db_manager.get_translation_session(session_id)
        
        assert session is not None
        assert session["input_type"] == "text"
        assert session["output_type"] == "body_language"
        assert session["input_data"]["text"] == "Hello"
        assert session["output_data"]["text"] == "Wave hand"
        assert session["confidence"] == 0.8
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_feedback(self, db_manager):
        """Test storing and retrieving user feedback"""
        await db_manager.initialize()
        
        # First create a session
        session_id = await db_manager.store_translation_session(
            "text", "body_language", {"text": "test"}, {"text": "test"}, 0.8, 1.0
        )
        
        # Store feedback
        feedback_id = await db_manager.store_feedback(
            session_id, 5, "Great translation!", 5, 4
        )
        
        assert feedback_id is not None
        
        # Retrieve feedback
        feedback = await db_manager.get_session_feedback(session_id)
        
        assert feedback is not None
        assert feedback["rating"] == 5
        assert feedback["comments"] == "Great translation!"
        assert feedback["accuracy_rating"] == 5
        assert feedback["speed_rating"] == 4

class TestWebSocketManager:
    """Test WebSocket Manager"""
    
    @pytest.fixture
    def ws_manager(self):
        """Create WebSocket manager instance for testing"""
        return WebSocketManager()
    
    @pytest.mark.asyncio
    async def test_connection_management(self, ws_manager):
        """Test WebSocket connection management"""
        # Mock WebSocket
        mock_websocket = AsyncMock()
        
        # Test connection
        await ws_manager.connect(mock_websocket)
        assert len(ws_manager.active_connections) == 1
        assert mock_websocket in ws_manager.connection_data
        
        # Test disconnection
        ws_manager.disconnect(mock_websocket)
        assert len(ws_manager.active_connections) == 0
        assert mock_websocket not in ws_manager.connection_data
    
    @pytest.mark.asyncio
    async def test_message_sending(self, ws_manager):
        """Test message sending functionality"""
        mock_websocket = AsyncMock()
        await ws_manager.connect(mock_websocket)
        
        # Test personal message
        test_message = {"type": "test", "content": "Hello"}
        await ws_manager.send_personal_message(test_message, mock_websocket)
        
        # Verify message was sent
        mock_websocket.send_text.assert_called_once()
        sent_data = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_data["type"] == "test"
        assert sent_data["content"] == "Hello"
        assert "timestamp" in sent_data

class TestTranslationModels:
    """Test Pydantic models"""
    
    def test_translation_request(self):
        """Test TranslationRequest model"""
        request = TranslationRequest(
            text="Hello world",
            context="Greeting",
            language="en",
            emotion="happy"
        )
        
        assert request.text == "Hello world"
        assert request.context == "Greeting"
        assert request.language == "en"
        assert request.emotion == "happy"
    
    def test_translation_response(self):
        """Test TranslationResponse model"""
        response = TranslationResponse(
            session_id="test-session-123",
            translated_text="Hello world",
            confidence=0.85,
            timestamp="2023-01-01T00:00:00",
            detected_gestures=["wave", "smile"]
        )
        
        assert response.session_id == "test-session-123"
        assert response.translated_text == "Hello world"
        assert response.confidence == 0.85
        assert "wave" in response.detected_gestures
    
    def test_body_language_data(self):
        """Test BodyLanguageData model"""
        data = BodyLanguageData(
            gestures=[
                {"type": "wave", "confidence": 0.8, "description": "Hand wave"}
            ],
            pose_landmarks=[{"x": 0.5, "y": 0.5, "z": 0.0}],
            confidence_scores={"wave": 0.8}
        )
        
        assert len(data.gestures) == 1
        assert data.gestures[0]["type"] == "wave"
        assert len(data.pose_landmarks) == 1
        assert data.confidence_scores["wave"] == 0.8

class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_translation_pipeline(self):
        """Test complete translation pipeline"""
        # Initialize services
        ai_translator = AITranslator()
        ai_translator.client = AsyncMock()
        
        body_processor = BodyLanguageProcessor()
        audio_processor = AudioProcessor()
        db_manager = DatabaseManager()
        db_manager.sqlite_db_path = ":memory:"
        
        # Mock AI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "text": "Hello, how are you?",
            "confidence": 0.85,
            "detected_gestures": ["wave", "smile"]
        })
        ai_translator.client.chat.completions.create.return_value = mock_response
        
        # Initialize database
        await db_manager.initialize()
        
        # Test body language to text translation
        body_language_data = {
            "gestures": [
                {"type": "wave", "confidence": 0.8, "description": "Hand waving gesture"}
            ],
            "confidence_scores": {"wave": 0.8}
        }
        
        translation_result = await ai_translator.body_language_to_text(
            body_language_data, "greeting context"
        )
        
        # Store in database
        session_id = await db_manager.store_translation_session(
            "body_language", "text", body_language_data, translation_result,
            translation_result["confidence"], 1.0
        )
        
        # Verify results
        assert translation_result["text"] == "Hello, how are you?"
        assert translation_result["confidence"] == 0.85
        
        # Retrieve from database
        stored_session = await db_manager.get_translation_session(session_id)
        assert stored_session is not None
        assert stored_session["input_type"] == "body_language"
        assert stored_session["output_type"] == "text"

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])

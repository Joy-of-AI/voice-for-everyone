"""
Body Language Translation API
Main FastAPI application for translating body language to text/audio and vice versa
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import base64
import io
from typing import List, Dict, Any
import logging
from datetime import datetime

# Local imports
from services.body_language_processor import BodyLanguageProcessor
from services.ai_translator import AITranslator
from services.audio_processor import AudioProcessor
from services.database_manager import DatabaseManager
from services.asl_processor import asl_processor
from services.avatar_engine import avatar_engine
from services.wlasl_integration import wlasl_integration
from services.how2sign_integration import how2sign_integration
from services.smplx_avatar_engine import smplx_avatar_engine
from services.webrtc_manager import webrtc_manager
from services.movenet_processor import movenet_processor
from services.onnx_inference_server import onnx_inference_server
from services.sigml_synthesis import sigml_synthesis
from models.translation_models import TranslationRequest, TranslationResponse
from utils.websocket_manager import WebSocketManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Body Language Translator API",
    description="AI-powered body language translation for communication accessibility",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
body_language_processor = BodyLanguageProcessor()
ai_translator = AITranslator()
audio_processor = AudioProcessor()
db_manager = DatabaseManager()
websocket_manager = WebSocketManager()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Body Language Translator API...")
    await db_manager.initialize()
    await ai_translator.initialize()
    logger.info("All services initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Body Language Translator API...")
    await db_manager.close()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Body Language Translator API is running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/translate/body-to-text")
async def translate_body_language_to_text(
    video_file: UploadFile = File(...),
    context: str = None
):
    """
    Translate body language from video to text
    """
    try:
        # Read video file
        video_content = await video_file.read()
        
        # Process body language
        body_language_data = await body_language_processor.process_video(video_content)
        
        # Translate to text using AI
        translation_result = await ai_translator.body_language_to_text(
            body_language_data, 
            context=context
        )
        
        # Store in database
        session_id = await db_manager.store_translation_session(
            input_type="body_language",
            output_type="text",
            input_data=body_language_data,
            output_data=translation_result
        )
        
        return TranslationResponse(
            session_id=session_id,
            translated_text=translation_result["text"],
            confidence=translation_result["confidence"],
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in body language to text translation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate/text-to-body")
async def translate_text_to_body_language(request: TranslationRequest):
    """
    Translate text to body language instructions
    """
    try:
        # Generate body language instructions using AI
        body_language_instructions = await ai_translator.text_to_body_language(
            request.text,
            context=request.context
        )
        
        # Store in database
        session_id = await db_manager.store_translation_session(
            input_type="text",
            output_type="body_language",
            input_data={"text": request.text},
            output_data=body_language_instructions
        )
        
        return {
            "session_id": session_id,
            "body_language_instructions": body_language_instructions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in text to body language translation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate/audio-to-body")
async def translate_audio_to_body_language(
    audio_file: UploadFile = File(...),
    context: str = None
):
    """
    Translate audio to body language instructions
    """
    try:
        # Read audio file
        audio_content = await audio_file.read()
        
        # Convert audio to text
        transcription = await audio_processor.speech_to_text(audio_content)
        
        # Generate body language instructions
        body_language_instructions = await ai_translator.text_to_body_language(
            transcription["text"],
            context=context
        )
        
        # Store in database
        session_id = await db_manager.store_translation_session(
            input_type="audio",
            output_type="body_language",
            input_data=transcription,
            output_data=body_language_instructions
        )
        
        return {
            "session_id": session_id,
            "transcription": transcription,
            "body_language_instructions": body_language_instructions,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in audio to body language translation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate/body-to-audio")
async def translate_body_language_to_audio(
    video_file: UploadFile = File(...),
    context: str = None
):
    """
    Translate body language to audio speech
    """
    try:
        # Read video file
        video_content = await video_file.read()
        
        # Process body language
        body_language_data = await body_language_processor.process_video(video_content)
        
        # Translate to text using AI
        translation_result = await ai_translator.body_language_to_text(
            body_language_data,
            context=context
        )
        
        # Convert text to speech
        audio_data = await audio_processor.text_to_speech(translation_result["text"])
        
        # Store in database
        session_id = await db_manager.store_translation_session(
            input_type="body_language",
            output_type="audio",
            input_data=body_language_data,
            output_data={"text": translation_result["text"], "audio": audio_data}
        )
        
        return {
            "session_id": session_id,
            "translated_text": translation_result["text"],
            "audio_base64": base64.b64encode(audio_data).decode(),
            "confidence": translation_result["confidence"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in body language to audio translation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/realtime-translation")
async def websocket_realtime_translation(websocket: WebSocket):
    """
    WebSocket endpoint for real-time body language translation
    """
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Receive video frame or audio data
            data = await websocket.receive_json()
            
            if data["type"] == "video_frame":
                # Process video frame for body language
                frame_data = base64.b64decode(data["frame"])
                body_language_data = await body_language_processor.process_frame(frame_data)
                
                if body_language_data["gestures"]:
                    # Translate to text
                    translation = await ai_translator.body_language_to_text(
                        body_language_data,
                        context=data.get("context")
                    )
                    
                    # Send translation back
                    await websocket_manager.send_personal_message({
                        "type": "translation",
                        "text": translation["text"],
                        "confidence": translation["confidence"],
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                    
            elif data["type"] == "audio_chunk":
                # Process audio chunk
                audio_data = base64.b64decode(data["audio"])
                transcription = await audio_processor.speech_to_text_realtime(audio_data)
                
                if transcription["text"]:
                    # Generate body language instructions
                    body_instructions = await ai_translator.text_to_body_language(
                        transcription["text"],
                        context=data.get("context")
                    )
                    
                    # Send instructions back
                    await websocket_manager.send_personal_message({
                        "type": "body_instructions",
                        "text": transcription["text"],
                        "instructions": body_instructions,
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                    
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket_manager.send_personal_message({
            "type": "error",
            "message": str(e)
        }, websocket)

@app.get("/sessions/{session_id}")
async def get_translation_session(session_id: str):
    """
    Retrieve a translation session by ID
    """
    try:
        session = await db_manager.get_translation_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        logger.error(f"Error retrieving session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def get_recent_sessions(limit: int = 10):
    """
    Get recent translation sessions
    """
    try:
        sessions = await db_manager.get_recent_sessions(limit)
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Error retrieving sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def submit_feedback(session_id: str, rating: int, comments: str = None):
    """
    Submit feedback for a translation session
    """
    try:
        await db_manager.store_feedback(session_id, rating, comments)
        return {"message": "Feedback submitted successfully"}
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ASL Processing Endpoints
@app.post("/asl/text-to-animation")
async def text_to_asl_animation(text: str, duration: float = 3.0):
    """
    Convert text to ASL animation with 3D avatar
    """
    try:
        logger.info(f"Processing ASL animation for text: {text}")
        
        # Process text to ASL animation
        animation = asl_processor.process_text_to_asl(text, duration)
        
        # Generate 3D avatar animation
        avatar_data = avatar_engine.generate_threejs_scene(animation)
        
        # Store in database
        session_id = await db_manager.store_translation_session(
            input_type="text",
            output_type="asl_animation",
            input_data={"text": text},
            output_data=avatar_data
        )
        
        return {
            "session_id": session_id,
            "original_text": text,
            "asl_gloss": animation.gloss.gloss_sequence,
            "animation_data": avatar_data,
            "metadata": {
                "duration": animation.duration,
                "fps": animation.fps,
                "total_frames": len(animation.pose_sequence),
                "confidence": animation.gloss.confidence
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in text to ASL animation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/asl/gloss-to-animation")
async def gloss_to_asl_animation(gloss_sequence: List[str], duration: float = 3.0):
    """
    Convert ASL gloss sequence to 3D animation
    """
    try:
        logger.info(f"Processing ASL animation for gloss: {gloss_sequence}")
        
        # Create ASL gloss object
        from services.asl_processor import ASLGloss
        gloss = ASLGloss(
            original_text=" ".join(gloss_sequence),
            gloss_sequence=gloss_sequence,
            confidence=0.9,
            metadata={"processing_method": "direct_gloss"}
        )
        
        # Generate pose animation
        animation = asl_processor.generate_pose_from_gloss(gloss, duration)
        
        # Generate 3D avatar animation
        avatar_data = avatar_engine.generate_threejs_scene(animation)
        
        return {
            "gloss_sequence": gloss_sequence,
            "animation_data": avatar_data,
            "metadata": {
                "duration": animation.duration,
                "fps": animation.fps,
                "total_frames": len(animation.pose_sequence)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in gloss to ASL animation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/asl/vocabulary")
async def get_asl_vocabulary():
    """
    Get available ASL vocabulary
    """
    try:
        return {
            "vocabulary": asl_processor.asl_gloss_vocab,
            "total_words": len(asl_processor.asl_gloss_vocab),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting ASL vocabulary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/asl/wlasl-vocabulary")
async def get_wlasl_vocabulary():
    """Get comprehensive WLASL vocabulary"""
    try:
        vocab_info = wlasl_integration.get_comprehensive_vocabulary()
        return {
            "success": True,
            "vocabulary_info": vocab_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting WLASL vocabulary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/asl/text-to-wlasl-animation")
async def text_to_wlasl_animation(request: dict):
    """Convert text to ASL animation using WLASL dataset"""
    try:
        text = request.get("text", "")
        duration = request.get("duration", 3.0)
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Use WLASL integration for advanced text-to-gloss conversion
        gloss_result = wlasl_integration.text_to_asl_gloss_advanced(text)
        
        # Create synthetic animation data for demonstration
        animation_data = {
            "frames": [],
            "duration": duration,
            "fps": 30,
            "total_frames": int(duration * 30)
        }
        
        # Generate synthetic frames
        for i in range(animation_data["total_frames"]):
            frame = {
                "frame_id": i,
                "timestamp": i / 30.0,
                "pose_landmarks": self._generate_synthetic_pose_landmarks(),
                "confidence": 0.8
            }
            animation_data["frames"].append(frame)
        
        # Store in database
        session_id = await db_manager.store_translation_session(
            input_type="text",
            output_type="wlasl_animation",
            input_data={"text": text},
            output_data=animation_data
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "original_text": text,
            "gloss": [item["gloss"] for item in gloss_result["gloss_sequence"]],
            "animation_data": animation_data,
            "wlasl_coverage": gloss_result.get("translated_words", 0),
            "processing_method": "wlasl_integration",
            "metadata": {
                "duration": duration,
                "fps": 30,
                "total_frames": animation_data["total_frames"],
                "confidence": gloss_result.get("confidence", 0.5)
            },
            "timestamp": datetime.now().isoformat()
        }

    def _generate_synthetic_pose_landmarks(self):
        """Generate synthetic pose landmarks for demonstration"""
        import random
        landmarks = []
        for i in range(33):  # MediaPipe Pose landmarks
            landmarks.append({
                "x": random.uniform(-1, 1),
                "y": random.uniform(-1, 1),
                "z": random.uniform(-1, 1),
                "confidence": random.uniform(0.7, 1.0)
            })
        return landmarks
        
    except Exception as e:
        logger.error(f"Error in text-to-WLASL animation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/asl/wlasl-stats")
async def get_wlasl_stats():
    """Get WLASL dataset statistics"""
    try:
        vocab_info = wlasl_integration.get_comprehensive_vocabulary()
        return {
            "success": True,
            "dataset_stats": {
                "total_words": vocab_info["total_words"],
                "total_samples": vocab_info["dataset_info"]["total_samples"],
                "unique_signers": vocab_info["dataset_info"]["unique_signers"],
                "unique_videos": vocab_info["dataset_info"]["unique_videos"],
                "coverage_stats": vocab_info["coverage_stats"]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting WLASL stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/how2sign/info")
async def get_how2sign_info():
    """Get How2Sign dataset information"""
    try:
        dataset_info = how2sign_integration.get_dataset_info()
        return {
            "success": True,
            "info": dataset_info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting How2Sign info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/how2sign/animation")
async def get_how2sign_animation(request: dict):
    """Get professional How2Sign animation for text"""
    try:
        text = request.get("text", "")
        sign_gloss = request.get("sign_gloss", "")
        
        # Accept either text or sign_gloss parameter
        input_text = text if text else sign_gloss
        if not input_text:
            raise HTTPException(status_code=400, detail="Text or sign_gloss is required")
        
        animation_data = how2sign_integration.get_professional_animation(input_text)
        if animation_data:
            return {
                "success": True,
                "animation": animation_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "No animation found for this text",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error getting How2Sign animation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/asl/export-animation")
async def export_asl_animation(session_id: str, format: str = "json"):
    """
    Export ASL animation in various formats
    """
    try:
        # Get session data
        session = await db_manager.get_translation_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session["output_type"] != "asl_animation":
            raise HTTPException(status_code=400, detail="Session is not an ASL animation")
        
        animation_data = session["output_data"]
        
        if format == "json":
            return JSONResponse(content=animation_data)
        elif format == "threejs":
            # Return Three.js compatible format
            return {
                "type": "threejs_scene",
                "data": animation_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
            
    except Exception as e:
        logger.error(f"Error exporting ASL animation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/asl-realtime")
async def websocket_asl_realtime(websocket: WebSocket):
    """
    WebSocket endpoint for real-time ASL animation
    """
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Receive text for real-time ASL conversion
            data = await websocket.receive_json()
            
            if data["type"] == "text":
                text = data["text"]
                duration = data.get("duration", 3.0)
                
                # Process text to ASL animation
                animation = asl_processor.process_text_to_asl(text, duration)
                avatar_data = avatar_engine.generate_threejs_scene(animation)
                
                # Send animation data back
                await websocket_manager.send_personal_message({
                    "type": "asl_animation",
                    "text": text,
                    "gloss": animation.gloss.gloss_sequence,
                    "animation_data": avatar_data,
                    "timestamp": datetime.now().isoformat()
                }, websocket)
                
            elif data["type"] == "gloss":
                gloss_sequence = data["gloss_sequence"]
                duration = data.get("duration", 3.0)
                
                # Create ASL gloss object
                from services.asl_processor import ASLGloss
                gloss = ASLGloss(
                    original_text=" ".join(gloss_sequence),
                    gloss_sequence=gloss_sequence,
                    confidence=0.9,
                    metadata={"processing_method": "websocket_gloss"}
                )
                
                # Generate animation
                animation = asl_processor.generate_pose_from_gloss(gloss, duration)
                avatar_data = avatar_engine.generate_threejs_scene(animation)
                
                # Send animation data back
                await websocket_manager.send_personal_message({
                    "type": "asl_animation",
                    "gloss_sequence": gloss_sequence,
                    "animation_data": avatar_data,
                    "timestamp": datetime.now().isoformat()
                }, websocket)
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"ASL WebSocket error: {str(e)}")
        await websocket_manager.send_personal_message({
            "type": "error",
            "message": str(e)
        }, websocket)

# SMPL-X Avatar Endpoints
@app.post("/avatar/smplx/create")
async def create_smplx_avatar(request: dict):
    """Create SMPL-X avatar"""
    try:
        gender = request.get("gender", "neutral")
        height = request.get("height", 1.7)
        
        avatar_id = smplx_avatar_engine.create_avatar(gender, height)
        
        return {
            "success": True,
            "avatar_id": avatar_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating SMPL-X avatar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/avatar/smplx/animation")
async def get_smplx_animation(request: dict):
    """Get SMPL-X animation"""
    try:
        avatar_id = request.get("avatar_id", "")
        gesture_type = request.get("gesture_type", "swim")
        duration = request.get("duration", 3.0)
        
        if gesture_type == "swim":
            animation = smplx_avatar_engine.generate_swimming_animation(avatar_id, duration)
        else:
            # Generic pose animation
            pose_data = {
                "body_pose": request.get("body_pose", []),
                "left_hand_pose": request.get("left_hand_pose", []),
                "right_hand_pose": request.get("right_hand_pose", []),
                "face_expression": request.get("face_expression", {})
            }
            animation = smplx_avatar_engine.apply_pose_animation(avatar_id, pose_data)
        
        return {
            "success": True,
            "animation": animation,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting SMPL-X animation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# MoveNet Endpoints
@app.post("/pose/movenet/process")
async def process_movenet_pose(request: dict):
    """Process frame with MoveNet"""
    try:
        import numpy as np
        
        # Convert frame data to numpy array
        frame_data = request.get("frame_data", [])
        frame = np.array(frame_data)
        
        result = movenet_processor.process_frame(frame)
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing MoveNet pose: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pose/movenet/stats")
async def get_movenet_stats():
    """Get MoveNet performance statistics"""
    try:
        stats = movenet_processor.get_performance_stats()
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting MoveNet stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ONNX Inference Endpoints
@app.post("/inference/onnx/process")
async def process_onnx_inference(request: dict):
    """Process inference with ONNX/Triton"""
    try:
        import numpy as np
        
        input_data = {}
        for key, value in request.get("input_data", {}).items():
            input_data[key] = np.array(value)
        
        result = await onnx_inference_server.infer(input_data)
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error processing ONNX inference: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/inference/onnx/stats")
async def get_onnx_stats():
    """Get ONNX inference statistics"""
    try:
        stats = onnx_inference_server.get_performance_stats()
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting ONNX stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# SiGML Synthesis Endpoints
@app.post("/sign/sigml/generate")
async def generate_sigml_sign(request: dict):
    """Generate SiGML sign animation"""
    try:
        text = request.get("text", "")
        duration = request.get("duration", 3.0)
        
        animation = sigml_synthesis.generate_sign_animation(text, duration)
        
        return {
            "success": True,
            "animation": animation,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating SiGML sign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sign/sigml/jasigning")
async def export_to_jasigning(request: dict):
    """Export animation to JASigning format"""
    try:
        animation_data = request.get("animation", {})
        
        jasigning_data = sigml_synthesis.export_to_jasigning(animation_data)
        
        return {
            "success": True,
            "jasigning": jasigning_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error exporting to JASigning: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sign/sigml/stats")
async def get_sigml_stats():
    """Get SiGML synthesis statistics"""
    try:
        stats = sigml_synthesis.get_dictionary_stats()
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting SiGML stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebRTC Endpoints
@app.get("/webrtc/status")
async def get_webrtc_status():
    """Get WebRTC connection status"""
    try:
        stats = webrtc_manager.get_connection_stats()
        
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting WebRTC status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

"""
Audio Processing Service for Speech-to-Text and Text-to-Speech
"""

import asyncio
import logging
import io
import base64
import tempfile
import os
from typing import Dict, Any, Optional
import numpy as np
import soundfile as sf
import librosa
import pyttsx3
import speech_recognition as sr
from datetime import datetime

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = None
        self.supported_languages = {
            "en": "english",
            "es": "spanish", 
            "fr": "french",
            "de": "german",
            "it": "italian",
            "pt": "portuguese",
            "ru": "russian",
            "ja": "japanese",
            "ko": "korean",
            "zh": "chinese"
        }
        
        # Audio processing parameters
        self.sample_rate = 16000
        self.chunk_duration = 0.5  # seconds
        self.silence_threshold = 0.01
        
    async def initialize(self):
        """Initialize text-to-speech engine"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS settings
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)
            
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.9)  # Volume level
            
            logger.info("Audio Processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Audio Processor: {str(e)}")
            raise

    async def speech_to_text(self, audio_data: bytes, language: str = "en") -> Dict[str, Any]:
        """
        Convert speech audio to text using SpeechRecognition
        """
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Load audio file
                with sr.AudioFile(temp_file_path) as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    # Record audio
                    audio = self.recognizer.record(source)
                
                # Perform speech recognition
                text = self.recognizer.recognize_google(
                    audio, 
                    language=f"{language}-{language.upper()}"
                )
                
                # Calculate confidence (Google doesn't provide confidence scores)
                confidence = 0.8  # Default confidence for Google Speech Recognition
                
                # Extract audio features for additional analysis
                audio_features = await self._extract_audio_features(audio_data)
                
                result = {
                    "text": text,
                    "confidence": confidence,
                    "language": language,
                    "timestamp": datetime.now().isoformat(),
                    "audio_features": audio_features
                }
                
                logger.info(f"Speech to text successful: {text[:50]}...")
                return result
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except sr.UnknownValueError:
            logger.warning("Speech recognition could not understand audio")
            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "error": "Speech not recognized"
            }
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {str(e)}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "error": f"Service error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error in speech to text conversion: {str(e)}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    async def speech_to_text_realtime(self, audio_chunk: bytes, language: str = "en") -> Dict[str, Any]:
        """
        Convert real-time audio chunk to text
        """
        try:
            # Convert audio chunk to proper format
            audio_array = await self._bytes_to_audio_array(audio_chunk)
            
            if audio_array is None:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "language": language,
                    "timestamp": datetime.now().isoformat(),
                    "error": "Invalid audio data"
                }
            
            # Check if audio contains speech (not just silence)
            if np.max(np.abs(audio_array)) < self.silence_threshold:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "language": language,
                    "timestamp": datetime.now().isoformat(),
                    "is_silence": True
                }
            
            # Save chunk to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                sf.write(temp_file.name, audio_array, self.sample_rate)
                temp_file_path = temp_file.name
            
            try:
                # Load audio file
                with sr.AudioFile(temp_file_path) as source:
                    audio = self.recognizer.record(source)
                
                # Perform speech recognition
                text = self.recognizer.recognize_google(
                    audio, 
                    language=f"{language}-{language.upper()}"
                )
                
                result = {
                    "text": text,
                    "confidence": 0.7,  # Lower confidence for real-time
                    "language": language,
                    "timestamp": datetime.now().isoformat(),
                    "is_silence": False
                }
                
                return result
                
            finally:
                os.unlink(temp_file_path)
                
        except sr.UnknownValueError:
            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "is_silence": False
            }
        except Exception as e:
            logger.error(f"Error in real-time speech to text: {str(e)}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    async def text_to_speech(self, text: str, language: str = "en", voice_speed: float = 1.0) -> bytes:
        """
        Convert text to speech audio using pyttsx3
        """
        try:
            if not self.tts_engine:
                await self.initialize()
            
            # Configure voice settings
            self.tts_engine.setProperty('rate', int(150 * voice_speed))
            
            # Set language if supported
            if language in self.supported_languages:
                # Note: pyttsx3 language support is limited
                # This is a simplified implementation
                pass
            
            # Save speech to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file_path = temp_file.name
            
            try:
                # Generate speech
                self.tts_engine.save_to_file(text, temp_file_path)
                self.tts_engine.runAndWait()
                
                # Read the generated audio file
                with open(temp_file_path, 'rb') as audio_file:
                    audio_data = audio_file.read()
                
                logger.info(f"Text to speech successful: {text[:50]}...")
                return audio_data
                
            finally:
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"Error in text to speech conversion: {str(e)}")
            # Return empty audio data on error
            return b""

    async def text_to_speech_advanced(self, text: str, language: str = "en", 
                                    voice_type: str = "neutral", 
                                    emotion: str = "neutral") -> bytes:
        """
        Advanced text-to-speech with voice and emotion control
        """
        try:
            if not self.tts_engine:
                await self.initialize()
            
            # Configure voice based on type and emotion
            voices = self.tts_engine.getProperty('voices')
            
            # Select appropriate voice
            if voices:
                if voice_type == "male" and len(voices) > 1:
                    # Try to find a male voice
                    for voice in voices:
                        if "male" in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
                elif voice_type == "female":
                    # Try to find a female voice
                    for voice in voices:
                        if "female" in voice.name.lower():
                            self.tts_engine.setProperty('voice', voice.id)
                            break
            
            # Adjust speech parameters based on emotion
            if emotion == "happy":
                self.tts_engine.setProperty('rate', 160)
                self.tts_engine.setProperty('volume', 1.0)
            elif emotion == "sad":
                self.tts_engine.setProperty('rate', 120)
                self.tts_engine.setProperty('volume', 0.7)
            elif emotion == "angry":
                self.tts_engine.setProperty('rate', 180)
                self.tts_engine.setProperty('volume', 1.0)
            elif emotion == "calm":
                self.tts_engine.setProperty('rate', 130)
                self.tts_engine.setProperty('volume', 0.8)
            else:
                # Neutral
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 0.9)
            
            # Generate speech
            return await self.text_to_speech(text, language)
            
        except Exception as e:
            logger.error(f"Error in advanced text to speech: {str(e)}")
            return await self.text_to_speech(text, language)  # Fallback to basic TTS

    async def _extract_audio_features(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Extract audio features for analysis
        """
        try:
            # Convert bytes to audio array
            audio_array = await self._bytes_to_audio_array(audio_data)
            
            if audio_array is None:
                return {}
            
            features = {}
            
            # Basic audio features
            features["duration"] = len(audio_array) / self.sample_rate
            features["rms_energy"] = np.sqrt(np.mean(audio_array**2))
            features["peak_amplitude"] = np.max(np.abs(audio_array))
            features["zero_crossing_rate"] = np.sum(np.diff(np.sign(audio_array))) / len(audio_array)
            
            # Spectral features
            if len(audio_array) > 1024:
                # Compute spectrogram
                spec = librosa.feature.melspectrogram(
                    y=audio_array, 
                    sr=self.sample_rate,
                    n_mels=128
                )
                
                features["spectral_centroid"] = np.mean(librosa.feature.spectral_centroid(
                    y=audio_array, sr=self.sample_rate
                ))
                features["spectral_bandwidth"] = np.mean(librosa.feature.spectral_bandwidth(
                    y=audio_array, sr=self.sample_rate
                ))
                features["spectral_rolloff"] = np.mean(librosa.feature.spectral_rolloff(
                    y=audio_array, sr=self.sample_rate
                ))
                
                # MFCC features
                mfccs = librosa.feature.mfcc(y=audio_array, sr=self.sample_rate, n_mfcc=13)
                features["mfcc_mean"] = np.mean(mfccs, axis=1).tolist()
                features["mfcc_std"] = np.std(mfccs, axis=1).tolist()
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting audio features: {str(e)}")
            return {}

    async def _bytes_to_audio_array(self, audio_bytes: bytes) -> Optional[np.ndarray]:
        """
        Convert audio bytes to numpy array
        """
        try:
            # Try to load with soundfile first
            with io.BytesIO(audio_bytes) as audio_io:
                audio_array, sample_rate = sf.read(audio_io)
                
                # Resample if necessary
                if sample_rate != self.sample_rate:
                    audio_array = librosa.resample(
                        audio_array, 
                        orig_sr=sample_rate, 
                        target_sr=self.sample_rate
                    )
                
                # Convert to mono if stereo
                if len(audio_array.shape) > 1:
                    audio_array = np.mean(audio_array, axis=1)
                
                return audio_array
                
        except Exception as e:
            logger.error(f"Error converting audio bytes to array: {str(e)}")
            return None

    async def detect_language(self, audio_data: bytes) -> str:
        """
        Detect the language of spoken audio
        """
        try:
            # This is a simplified language detection
            # In a real implementation, you would use a language detection model
            
            # Try recognition with multiple languages
            languages = ["en", "es", "fr", "de", "it"]
            
            for lang in languages:
                result = await self.speech_to_text(audio_data, lang)
                if result["text"] and result["confidence"] > 0.5:
                    return lang
            
            return "en"  # Default to English
            
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return "en"

    async def analyze_speech_emotion(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Analyze emotional content of speech
        """
        try:
            audio_features = await self._extract_audio_features(audio_data)
            
            # Simplified emotion analysis based on audio features
            emotion_scores = {
                "happy": 0.0,
                "sad": 0.0,
                "angry": 0.0,
                "calm": 0.0,
                "excited": 0.0
            }
            
            if audio_features:
                # Analyze based on spectral features
                if "spectral_centroid" in audio_features:
                    centroid = audio_features["spectral_centroid"]
                    if centroid > 2000:
                        emotion_scores["excited"] += 0.3
                        emotion_scores["happy"] += 0.2
                    elif centroid < 1000:
                        emotion_scores["sad"] += 0.3
                        emotion_scores["calm"] += 0.2
                
                # Analyze based on energy
                if "rms_energy" in audio_features:
                    energy = audio_features["rms_energy"]
                    if energy > 0.1:
                        emotion_scores["angry"] += 0.3
                        emotion_scores["excited"] += 0.2
                    elif energy < 0.01:
                        emotion_scores["calm"] += 0.3
                        emotion_scores["sad"] += 0.2
                
                # Normalize scores
                total = sum(emotion_scores.values())
                if total > 0:
                    emotion_scores = {k: v/total for k, v in emotion_scores.items()}
            
            # Get dominant emotion
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            
            return {
                "emotion_scores": emotion_scores,
                "dominant_emotion": dominant_emotion,
                "confidence": emotion_scores[dominant_emotion],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing speech emotion: {str(e)}")
            return {
                "emotion_scores": {"neutral": 1.0},
                "dominant_emotion": "neutral",
                "confidence": 0.0,
                "error": str(e)
            }

    async def get_available_voices(self) -> Dict[str, Any]:
        """
        Get available TTS voices
        """
        try:
            if not self.tts_engine:
                await self.initialize()
            
            voices = self.tts_engine.getProperty('voices')
            voice_list = []
            
            for i, voice in enumerate(voices):
                voice_info = {
                    "id": voice.id,
                    "name": voice.name,
                    "languages": voice.languages,
                    "gender": voice.gender if hasattr(voice, 'gender') else "unknown",
                    "index": i
                }
                voice_list.append(voice_info)
            
            return {
                "voices": voice_list,
                "total_count": len(voices),
                "current_voice": self.tts_engine.getProperty('voice')
            }
            
        except Exception as e:
            logger.error(f"Error getting available voices: {str(e)}")
            return {"voices": [], "total_count": 0, "error": str(e)}

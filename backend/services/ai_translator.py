"""
AI Translation Service using GPT-OSS-120B for context-aware body language translation
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

from models.translation_models import BodyLanguageData, BodyLanguageInstruction, GestureType

load_dotenv()

logger = logging.getLogger(__name__)

class AITranslator:
    def __init__(self):
        self.model = "openai/gpt-oss-120b"  # Using GPT-OSS-120B for high accuracy
        self.max_tokens = 2000
        self.temperature = 0.3  # Lower temperature for more consistent translations
        self.mock_mode = True  # Force mock mode for now
        self.pipe = None
        self.tokenizer = None
        
        # Body language gesture vocabulary
        self.gesture_vocabulary = {
            "greetings": ["wave", "handshake", "bow", "nod", "smile"],
            "emotions": ["happy", "sad", "angry", "surprised", "confused", "excited"],
            "basic_needs": ["hungry", "thirsty", "tired", "pain", "help"],
            "responses": ["yes", "no", "maybe", "okay", "stop", "continue"],
            "directions": ["up", "down", "left", "right", "forward", "backward"],
            "numbers": ["one", "two", "three", "four", "five", "ten"],
            "common_phrases": ["please", "thank_you", "sorry", "excuse_me", "goodbye"]
        }
        
    async def initialize(self):
        """Initialize GPT-OSS-120B model"""
        try:
            # Check if GPU is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            # Initialize the pipeline with GPT-OSS-120B
            self.pipe = pipeline(
                "text-generation",
                model=self.model,
                torch_dtype="auto",
                device_map="auto",
            )
            
            self.mock_mode = True  # Keep mock mode for now
            logger.info("AI Translator initialized successfully with GPT-OSS-120B (mock mode)")
            
        except Exception as e:
            logger.error(f"Failed to initialize GPT-OSS-120B: {str(e)}")
            logger.warning("Using mock implementation for demonstration.")
            self.pipe = None
            self.mock_mode = True

    async def body_language_to_text(self, body_language_data: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert body language data to natural text using GPT-4
        """
        try:
            # Check if we're in mock mode
            if self.mock_mode:
                return self._get_mock_body_language_translation(body_language_data, context)
            
            # Prepare the prompt with body language data
            gestures_description = self._format_gestures_for_prompt(body_language_data)
            
            # Use GPT-OSS-120B with harmony format
            messages = [
                {"role": "system", "content": "Reasoning: high\n\nYou are an expert body language interpreter and translator. Your task is to convert detected body language gestures, poses, and facial expressions into natural, contextually appropriate text.\n\nGuidelines:\n1. Interpret gestures holistically, considering context and cultural meanings\n2. Provide natural, conversational text that captures the intended message\n3. Consider emotional context and non-verbal cues\n4. Return JSON with 'text', 'confidence', and 'detected_gestures' fields\n5. Confidence should be 0.0-1.0 based on gesture clarity and context\n6. Be sensitive to accessibility needs and communication intent"},
                {"role": "user", "content": f"Body Language Data:\n{gestures_description}\n\nAdditional Context: {context or 'No additional context provided'}\n\nPlease interpret this body language and provide:\n1. The most likely intended message in natural text\n2. Confidence level (0.0-1.0)\n3. List of key gestures detected\n\nReturn as JSON format."}
            ]
            
            # Generate response using GPT-OSS-120B
            outputs = self.pipe(
                messages,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                do_sample=True
            )
            
            # Extract the generated text
            generated_text = outputs[0]["generated_text"][-1]["content"]
            
            # Parse the response
            try:
                result = json.loads(generated_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                result = {
                    "text": generated_text,
                    "confidence": 0.7,
                    "detected_gestures": []
                }
            
            # Ensure required fields exist
            if "text" not in result:
                result["text"] = "Could not interpret body language clearly"
            if "confidence" not in result:
                result["confidence"] = 0.5
            if "detected_gestures" not in result:
                result["detected_gestures"] = []
                
            logger.info(f"Body language translated to text: {result['text'][:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error in body language to text translation: {str(e)}")
            return {
                "text": "Translation error occurred",
                "confidence": 0.0,
                "detected_gestures": [],
                "error": str(e)
            }

    async def text_to_body_language(self, text: str, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Convert text to body language instructions using GPT-4
        """
        try:
            # Check if we're in mock mode
            if self.mock_mode:
                return self._get_mock_body_language_instructions(text, context)
            
            system_prompt = """
            You are an expert in body language and non-verbal communication. Your task is to convert text into detailed body language instructions that can be performed to communicate the message effectively.
            
            Guidelines:
            1. Break down the message into clear, performable gestures
            2. Include facial expressions, hand gestures, body posture, and movements
            3. Consider cultural sensitivity and accessibility
            4. Provide timing and intensity guidance
            5. Return structured JSON with gesture instructions
            6. Focus on universal gestures that are widely understood
            """
            
            user_prompt = f"""
            Text to translate: "{text}"
            Context: {context or "General communication"}
            
            Please provide detailed body language instructions to communicate this message. Include:
            1. Gesture type (hand, face, body, pose)
            2. Detailed description of the gesture
            3. Timing and duration recommendations
            4. Intensity level (0.0-1.0)
            5. Sequence order for multiple gestures
            
            Return as JSON array of gesture instructions.
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Parse the response
            instructions = json.loads(response.choices[0].message.content)
            
            # Ensure it's a list
            if not isinstance(instructions, list):
                instructions = [instructions] if isinstance(instructions, dict) else []
            
            # Validate and format instructions
            formatted_instructions = []
            for i, instruction in enumerate(instructions):
                formatted_instruction = {
                    "gesture_type": instruction.get("gesture_type", "hand"),
                    "description": instruction.get("description", ""),
                    "duration": instruction.get("duration", 2.0),
                    "intensity": instruction.get("intensity", 0.7),
                    "sequence_order": instruction.get("sequence_order", i + 1),
                    "coordinates": instruction.get("coordinates"),
                    "timing_notes": instruction.get("timing_notes", "")
                }
                formatted_instructions.append(formatted_instruction)
            
            logger.info(f"Text translated to {len(formatted_instructions)} body language instructions")
            return formatted_instructions
            
        except Exception as e:
            logger.error(f"Error in text to body language translation: {str(e)}")
            return [{
                "gesture_type": "hand",
                "description": "Error occurred during translation",
                "duration": 2.0,
                "intensity": 0.5,
                "sequence_order": 1,
                "error": str(e)
            }]

    async def enhance_translation_with_context(self, translation: str, context_history: List[str]) -> str:
        """
        Enhance translation accuracy using conversation context
        """
        try:
            system_prompt = """
            You are helping to improve body language translation accuracy by considering conversation context and history.
            Refine the translation to be more contextually appropriate and natural.
            """
            
            context_text = "\n".join(context_history[-5:])  # Last 5 messages for context
            
            user_prompt = f"""
            Current translation: "{translation}"
            Conversation context:
            {context_text}
            
            Please refine this translation to be more contextually appropriate and natural.
            Return only the improved translation text.
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.2
            )
            
            enhanced_translation = response.choices[0].message.content.strip()
            logger.info("Translation enhanced with context")
            return enhanced_translation
            
        except Exception as e:
            logger.error(f"Error enhancing translation with context: {str(e)}")
            return translation  # Return original if enhancement fails

    def _format_gestures_for_prompt(self, body_language_data: Dict[str, Any]) -> str:
        """
        Format body language data for GPT-4 prompt
        """
        formatted_data = []
        
        if "gestures" in body_language_data:
            formatted_data.append(f"Gestures detected: {len(body_language_data['gestures'])}")
            for gesture in body_language_data['gestures']:
                gesture_info = f"- {gesture.get('type', 'unknown')}: {gesture.get('description', 'no description')}"
                if 'confidence' in gesture:
                    gesture_info += f" (confidence: {gesture['confidence']:.2f})"
                formatted_data.append(gesture_info)
        
        if "pose_landmarks" in body_language_data and body_language_data["pose_landmarks"]:
            formatted_data.append(f"Body pose landmarks: {len(body_language_data['pose_landmarks'])} points detected")
        
        if "hand_landmarks" in body_language_data and body_language_data["hand_landmarks"]:
            formatted_data.append(f"Hand landmarks: {len(body_language_data['hand_landmarks'])} points detected")
        
        if "face_landmarks" in body_language_data and body_language_data["face_landmarks"]:
            formatted_data.append(f"Facial landmarks: {len(body_language_data['face_landmarks'])} points detected")
        
        if "confidence_scores" in body_language_data:
            avg_confidence = sum(body_language_data["confidence_scores"].values()) / len(body_language_data["confidence_scores"])
            formatted_data.append(f"Average detection confidence: {avg_confidence:.2f}")
        
        return "\n".join(formatted_data) if formatted_data else "No clear body language data detected"

    async def get_gesture_suggestions(self, partial_text: str) -> List[Dict[str, str]]:
        """
        Get gesture suggestions for partial text input (for real-time assistance)
        """
        try:
            # Quick gesture suggestions based on common patterns
            suggestions = []
            
            for category, gestures in self.gesture_vocabulary.items():
                for gesture in gestures:
                    if gesture.lower() in partial_text.lower():
                        suggestions.append({
                            "gesture": gesture,
                            "category": category,
                            "description": f"Common gesture for '{gesture}'"
                        })
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error getting gesture suggestions: {str(e)}")
            return []

    def _get_mock_body_language_translation(self, body_language_data: Dict[str, Any], context: Optional[str] = None) -> Dict[str, Any]:
        """
        Provide mock translation responses when OpenAI API is not available
        """
        import random
        
        # Mock responses based on detected gestures
        mock_responses = [
            "Hello! How are you today?",
            "I need help, please.",
            "Thank you very much!",
            "I'm sorry, I don't understand.",
            "Yes, that's correct.",
            "No, that's not right.",
            "Please wait a moment.",
            "I'm feeling good today.",
            "Can you help me?",
            "I understand now."
        ]
        
        # Mock confidence based on data quality
        confidence = 0.7 + (random.random() * 0.2)  # 0.7-0.9 range
        
        # Mock detected gestures
        detected_gestures = []
        if "gestures" in body_language_data and body_language_data["gestures"]:
            detected_gestures = [gesture.get("type", "unknown") for gesture in body_language_data["gestures"][:3]]
        
        return {
            "text": random.choice(mock_responses),
            "confidence": confidence,
            "detected_gestures": detected_gestures,
            "mock_mode": True
        }

    def _get_mock_body_language_instructions(self, text: str, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Provide specific body language instructions for communication accessibility
        """
        text_lower = text.lower()
        instructions = []
        
        # Comprehensive gesture mappings for common phrases and words
        gesture_mappings = {
            # Basic needs and wants
            "want": [{"gesture_type": "hand", "description": "Point to your chest with index finger, then point forward", "duration": 2.0, "intensity": 0.8}],
            "need": [{"gesture_type": "hand", "description": "Hold both hands palms up, then bring them toward your chest", "duration": 2.5, "intensity": 0.9}],
            "go": [{"gesture_type": "hand", "description": "Point forward with index finger, then make walking motion with fingers", "duration": 2.0, "intensity": 0.8}],
            "come": [{"gesture_type": "hand", "description": "Wave hand toward yourself with palm facing up", "duration": 1.5, "intensity": 0.7}],
            
            # Places
            "school": [{"gesture_type": "hand", "description": "Make writing motion with hand, then point to building location", "duration": 3.0, "intensity": 0.8}],
            "home": [{"gesture_type": "hand", "description": "Point to your chest, then make roof shape with hands above head", "duration": 2.5, "intensity": 0.8}],
            "hospital": [{"gesture_type": "hand", "description": "Make cross sign on chest, then point to building location", "duration": 3.0, "intensity": 0.9}],
            "store": [{"gesture_type": "hand", "description": "Make money counting motion, then point to building location", "duration": 2.5, "intensity": 0.8}],
            
            # Actions
            "eat": [{"gesture_type": "hand", "description": "Bring hand to mouth in eating motion", "duration": 1.5, "intensity": 0.8}],
            "drink": [{"gesture_type": "hand", "description": "Make cup shape with hand, bring to mouth", "duration": 1.5, "intensity": 0.8}],
            "sleep": [{"gesture_type": "hand", "description": "Place hands together under tilted head", "duration": 2.0, "intensity": 0.7}],
            "work": [{"gesture_type": "hand", "description": "Make hammering motion with fist", "duration": 2.0, "intensity": 0.8}],
            "swim": [{"gesture_type": "swim", "description": "Make swimming motion with both arms in alternating pattern", "duration": 3.0, "intensity": 0.8}],
            
            # Emotions and responses
            "happy": [{"gesture_type": "face", "description": "Smile broadly, then point to your smile", "duration": 2.0, "intensity": 0.9}],
            "sad": [{"gesture_type": "face", "description": "Frown, then point to your face", "duration": 2.0, "intensity": 0.8}],
            "angry": [{"gesture_type": "face", "description": "Frown deeply, then make fist", "duration": 2.0, "intensity": 0.9}],
            "tired": [{"gesture_type": "body", "description": "Slump shoulders, then yawn motion", "duration": 2.5, "intensity": 0.8}],
            
            # Communication
            "hello": [{"gesture_type": "hand", "description": "Wave hand from side to side", "duration": 2.0, "intensity": 0.8}],
            "goodbye": [{"gesture_type": "hand", "description": "Wave hand, then point away", "duration": 2.0, "intensity": 0.7}],
            "thank": [{"gesture_type": "hand", "description": "Place hand over heart, then nod head", "duration": 2.0, "intensity": 0.8}],
            "sorry": [{"gesture_type": "hand", "description": "Place hand over heart, then bow head slightly", "duration": 2.0, "intensity": 0.8}],
            
            # Basic responses
            "yes": [{"gesture_type": "head", "description": "Nod head up and down", "duration": 1.0, "intensity": 0.8}],
            "no": [{"gesture_type": "head", "description": "Shake head side to side", "duration": 1.0, "intensity": 0.8}],
            "maybe": [{"gesture_type": "hand", "description": "Hold hand palm up, then tilt side to side", "duration": 2.0, "intensity": 0.6}],
            "okay": [{"gesture_type": "hand", "description": "Make OK sign with thumb and index finger", "duration": 1.5, "intensity": 0.8}],
            
            # Urgency and needs
            "help": [{"gesture_type": "hand", "description": "Raise hand above head, then point to yourself", "duration": 3.0, "intensity": 0.9}],
            "stop": [{"gesture_type": "hand", "description": "Hold palm forward like traffic stop", "duration": 1.5, "intensity": 0.9}],
            "wait": [{"gesture_type": "hand", "description": "Hold palm up, then point to watch", "duration": 2.0, "intensity": 0.7}],
            "hurry": [{"gesture_type": "hand", "description": "Make fast circular motion with hand", "duration": 2.0, "intensity": 0.9}],
            
            # Questions
            "what": [{"gesture_type": "hand", "description": "Hold hands palms up, then shrug shoulders", "duration": 2.0, "intensity": 0.8}],
            "where": [{"gesture_type": "hand", "description": "Point to different directions with questioning look", "duration": 2.5, "intensity": 0.8}],
            "when": [{"gesture_type": "hand", "description": "Point to watch, then hold hands palms up", "duration": 2.0, "intensity": 0.8}],
            "why": [{"gesture_type": "hand", "description": "Point to head, then hold hands palms up", "duration": 2.0, "intensity": 0.8}],
            
            # Numbers
            "one": [{"gesture_type": "hand", "description": "Hold up index finger", "duration": 1.0, "intensity": 0.8}],
            "two": [{"gesture_type": "hand", "description": "Hold up index and middle finger", "duration": 1.0, "intensity": 0.8}],
            "three": [{"gesture_type": "hand", "description": "Hold up three fingers", "duration": 1.0, "intensity": 0.8}],
        }
        
        # Find matching gestures for the text
        for keyword, gestures in gesture_mappings.items():
            if keyword in text_lower:
                instructions.extend(gestures)
        
        # If no specific matches found, break down the sentence and provide instructions
        if not instructions:
            # Check for common phrases
            if "let's" in text_lower:
                if "swim" in text_lower:
                    instructions = [
                        {"gesture_type": "swim", "description": "Make swimming motion with both arms in alternating pattern", "duration": 3.0, "intensity": 0.8},
                        {"gesture_type": "point", "description": "Point to indicate swimming location", "duration": 2.0, "intensity": 0.7}
                    ]
                elif "go" in text_lower:
                    instructions = [
                        {"gesture_type": "hand", "description": "Point forward with index finger, then make walking motion", "duration": 2.5, "intensity": 0.8}
                    ]
                else:
                    instructions = [
                        {"gesture_type": "hand", "description": "Gesture to indicate invitation or suggestion", "duration": 2.0, "intensity": 0.7}
                    ]
            words = text_lower.split()
            for word in words:
                if word in gesture_mappings:
                    instructions.extend(gesture_mappings[word])
        
        # If still no matches, provide context-based instructions
        if not instructions:
            if "go" in text_lower or "want" in text_lower:
                instructions = [
                    {"gesture_type": "hand", "description": "Point to your chest, then point forward in the direction you want to go", "duration": 3.0, "intensity": 0.8},
                    {"gesture_type": "face", "description": "Show determined expression", "duration": 2.0, "intensity": 0.7}
                ]
            elif "need" in text_lower or "help" in text_lower:
                instructions = [
                    {"gesture_type": "hand", "description": "Hold both hands palms up toward the person", "duration": 2.0, "intensity": 0.9},
                    {"gesture_type": "face", "description": "Show concerned or urgent expression", "duration": 2.0, "intensity": 0.8}
                ]
            else:
                instructions = [
                    {"gesture_type": "hand", "description": "Point to your chest, then gesture to explain what you want", "duration": 2.5, "intensity": 0.8},
                    {"gesture_type": "face", "description": "Show your emotion about the situation", "duration": 2.0, "intensity": 0.7}
                ]
        
        # Add sequence order
        for i, instruction in enumerate(instructions):
            instruction["sequence_order"] = i + 1
        
        return instructions

"""
SiGML/HamNoSys Sign Synthesis Service
Professional sign synthesis with JASigning avatar support
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class HamNoSysConfig:
    """HamNoSys configuration"""
    language: str = "ASL"
    avatar_type: str = "jasigning"
    animation_speed: float = 1.0
    enable_facial_expressions: bool = True
    enable_hand_details: bool = True
    enable_body_movement: bool = True

class SiGMLSynthesis:
    """
    SiGML/HamNoSys Sign Synthesis Service
    Provides professional sign synthesis with JASigning avatar support
    """
    
    def __init__(self, config: HamNoSysConfig):
        self.config = config
        self.hamnosys_dictionary = {}
        self.sigml_templates = {}
        self.avatar_configs = {}
        
        # HamNoSys symbols mapping
        self.hamnosys_symbols = {
            # Hand shapes
            "A": "fist",
            "B": "flat_hand",
            "C": "curved_hand",
            "D": "index_point",
            "E": "thumb_up",
            "F": "ok_sign",
            "G": "index_thumb",
            "H": "flat_fingers",
            "I": "little_finger",
            "L": "thumb_index_l",
            "M": "three_fingers",
            "N": "index_middle",
            "O": "circle_hand",
            "P": "index_middle_thumb",
            "Q": "index_thumb_hook",
            "R": "index_middle_cross",
            "S": "fist_thumb",
            "T": "index_thumb_t",
            "U": "index_middle_u",
            "V": "index_middle_v",
            "W": "three_fingers_w",
            "X": "index_hook",
            "Y": "thumb_little",
            "Z": "index_z"
        }
        
        # Initialize dictionaries
        self._initialize_dictionaries()
    
    def _initialize_dictionaries(self):
        """Initialize HamNoSys and SiGML dictionaries"""
        try:
            logger.info("Initializing HamNoSys and SiGML dictionaries")
            
            # Load HamNoSys dictionary
            self.hamnosys_dictionary = {
                "hello": "A@shoulder~A@chin",
                "goodbye": "A@shoulder~A@forward",
                "thank_you": "A@chin~A@forward",
                "please": "B@chest~B@forward",
                "yes": "A@chin~A@forward",
                "no": "A@chin~A@side",
                "help": "B@chest~B@up",
                "understand": "A@forehead~A@chin",
                "learn": "A@forehead~A@chest",
                "work": "A@chest~A@forward",
                "home": "A@chest~A@chest",
                "family": "F@chest~F@forward",
                "friend": "F@chest~F@chest",
                "love": "A@chest~A@heart",
                "happy": "B@chest~B@up",
                "sad": "B@chest~B@down",
                "angry": "A@chest~A@forward",
                "tired": "A@eyes~A@down",
                "hungry": "A@mouth~A@chest",
                "thirsty": "A@mouth~A@forward",
                "swim": "B@shoulder~B@forward",
                "run": "A@chest~A@forward",
                "walk": "A@chest~A@forward",
                "sit": "A@chest~A@down",
                "stand": "A@chest~A@up",
                "come": "A@chest~A@chest",
                "go": "A@chest~A@forward",
                "stop": "B@chest~B@forward",
                "wait": "B@chest~B@chest",
                "now": "A@chest~A@forward",
                "later": "A@chest~A@side",
                "today": "A@chest~A@chest",
                "tomorrow": "A@chest~A@forward",
                "yesterday": "A@chest~A@back",
                "time": "A@chest~A@forward",
                "money": "A@chest~A@forward",
                "food": "A@mouth~A@chest",
                "water": "A@mouth~A@forward",
                "house": "B@chest~B@chest",
                "car": "A@chest~A@forward",
                "book": "B@chest~B@chest",
                "school": "A@chest~A@chest",
                "teacher": "A@chest~A@chest",
                "student": "A@chest~A@chest",
                "doctor": "A@chest~A@chest",
                "nurse": "A@chest~A@chest",
                "police": "A@chest~A@chest",
                "fire": "A@chest~A@up",
                "phone": "A@ear~A@mouth",
                "computer": "A@chest~A@chest",
                "internet": "A@chest~A@chest",
                "email": "A@chest~A@chest",
                "music": "A@ear~A@chest",
                "dance": "A@chest~A@chest",
                "sport": "A@chest~A@chest",
                "game": "A@chest~A@chest",
                "play": "A@chest~A@chest",
                "watch": "A@eyes~A@chest",
                "listen": "A@ear~A@chest",
                "speak": "A@mouth~A@forward",
                "sign": "A@chest~A@forward",
                "deaf": "A@ear~A@chest",
                "hearing": "A@ear~A@chest",
                "blind": "A@eyes~A@chest",
                "see": "A@eyes~A@chest",
                "hear": "A@ear~A@chest",
                "feel": "A@chest~A@chest",
                "touch": "A@chest~A@chest",
                "smell": "A@nose~A@chest",
                "taste": "A@mouth~A@chest"
            }
            
            # Load SiGML templates
            self.sigml_templates = {
                "basic_sign": self._create_basic_sigml_template(),
                "compound_sign": self._create_compound_sigml_template(),
                "sentence_sign": self._create_sentence_sigml_template(),
                "question_sign": self._create_question_sigml_template(),
                "emotion_sign": self._create_emotion_sigml_template()
            }
            
            # Load avatar configurations
            self.avatar_configs = {
                "jasigning": {
                    "type": "jasigning",
                    "version": "1.0",
                    "features": ["facial_expressions", "hand_details", "body_movement"],
                    "animation_speed": self.config.animation_speed,
                    "enable_facial_expressions": self.config.enable_facial_expressions,
                    "enable_hand_details": self.config.enable_hand_details,
                    "enable_body_movement": self.config.enable_body_movement
                }
            }
            
            logger.info("HamNoSys and SiGML dictionaries initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing dictionaries: {e}")
    
    def _create_basic_sigml_template(self) -> str:
        """Create basic SiGML template"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<sigml>
    <hns_sign>
        <handconfig hand="right" handshape="{handshape}" location="{location}" orientation="{orientation}"/>
        <handconfig hand="left" handshape="{left_handshape}" location="{left_location}" orientation="{left_orientation}"/>
        <movement>{movement}</movement>
        <nonmanual>{nonmanual}</nonmanual>
    </hns_sign>
</sigml>"""
    
    def _create_compound_sigml_template(self) -> str:
        """Create compound SiGML template"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<sigml>
    <hns_sign>
        <handconfig hand="right" handshape="{handshape}" location="{location}" orientation="{orientation}"/>
        <handconfig hand="left" handshape="{left_handshape}" location="{left_location}" orientation="{left_orientation}"/>
        <movement>{movement}</movement>
        <nonmanual>{nonmanual}</nonmanual>
        <transition>
            <handconfig hand="right" handshape="{transition_handshape}" location="{transition_location}" orientation="{transition_orientation}"/>
            <movement>{transition_movement}</movement>
        </transition>
    </hns_sign>
</sigml>"""
    
    def _create_sentence_sigml_template(self) -> str:
        """Create sentence SiGML template"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<sigml>
    <hns_sign>
        <handconfig hand="right" handshape="{handshape}" location="{location}" orientation="{orientation}"/>
        <handconfig hand="left" handshape="{left_handshape}" location="{left_location}" orientation="{left_orientation}"/>
        <movement>{movement}</movement>
        <nonmanual>{nonmanual}</nonmanual>
        <timing>
            <hold duration="{hold_duration}"/>
            <transition duration="{transition_duration}"/>
        </timing>
    </hns_sign>
</sigml>"""
    
    def _create_question_sigml_template(self) -> str:
        """Create question SiGML template"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<sigml>
    <hns_sign>
        <handconfig hand="right" handshape="{handshape}" location="{location}" orientation="{orientation}"/>
        <handconfig hand="left" handshape="{left_handshape}" location="{left_location}" orientation="{left_orientation}"/>
        <movement>{movement}</movement>
        <nonmanual>
            <eyebrow>raised</eyebrow>
            <head>tilt</head>
            <expression>question</expression>
        </nonmanual>
    </hns_sign>
</sigml>"""
    
    def _create_emotion_sigml_template(self) -> str:
        """Create emotion SiGML template"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<sigml>
    <hns_sign>
        <handconfig hand="right" handshape="{handshape}" location="{location}" orientation="{orientation}"/>
        <handconfig hand="left" handshape="{left_handshape}" location="{left_location}" orientation="{left_orientation}"/>
        <movement>{movement}</movement>
        <nonmanual>
            <expression>{emotion}</expression>
            <eyebrow>{eyebrow}</eyebrow>
            <head>{head}</head>
        </nonmanual>
    </hns_sign>
</sigml>"""
    
    def text_to_hamnosys(self, text: str) -> str:
        """Convert text to HamNoSys notation"""
        try:
            # Normalize text
            text_lower = text.lower().strip()
            
            # Split into words
            words = text_lower.split()
            
            # Convert each word to HamNoSys
            hamnosys_parts = []
            for word in words:
                if word in self.hamnosys_dictionary:
                    hamnosys_parts.append(self.hamnosys_dictionary[word])
                else:
                    # Generate synthetic HamNoSys for unknown words
                    hamnosys_parts.append(self._generate_synthetic_hamnosys(word))
            
            # Join with transitions
            hamnosys_notation = "~".join(hamnosys_parts)
            
            return hamnosys_notation
            
        except Exception as e:
            logger.error(f"Error converting text to HamNoSys: {e}")
            return ""
    
    def _generate_synthetic_hamnosys(self, word: str) -> str:
        """Generate synthetic HamNoSys for unknown words"""
        # Simple synthetic generation based on word characteristics
        if len(word) <= 3:
            return "A@chest~A@forward"
        elif word.startswith(('a', 'e', 'i', 'o', 'u')):
            return "A@chest~A@up"
        elif word.endswith(('ing', 'ed', 'er')):
            return "A@chest~A@forward"
        else:
            return "A@chest~A@chest"
    
    def hamnosys_to_sigml(self, hamnosys: str, sign_type: str = "basic") -> str:
        """Convert HamNoSys notation to SiGML"""
        try:
            # Parse HamNoSys notation
            parts = hamnosys.split("~")
            
            if not parts:
                return ""
            
            # Get template
            template = self.sigml_templates.get(sign_type, self.sigml_templates["basic_sign"])
            
            # Parse first part for basic sign
            first_part = parts[0]
            handshape, location, orientation = self._parse_hamnosys_part(first_part)
            
            # Generate SiGML
            sigml = template.format(
                handshape=handshape,
                location=location,
                orientation=orientation,
                left_handshape="A",
                left_location="chest",
                left_orientation="palm_in",
                movement="straight",
                nonmanual="neutral",
                transition_handshape=handshape,
                transition_location=location,
                transition_orientation=orientation,
                transition_movement="straight",
                hold_duration="1.0",
                transition_duration="0.5",
                emotion="neutral",
                eyebrow="neutral",
                head="straight"
            )
            
            return sigml
            
        except Exception as e:
            logger.error(f"Error converting HamNoSys to SiGML: {e}")
            return ""
    
    def _parse_hamnosys_part(self, part: str) -> Tuple[str, str, str]:
        """Parse HamNoSys part into components"""
        # Extract handshape (before @)
        if "@" in part:
            handshape = part.split("@")[0]
            location_part = part.split("@")[1]
        else:
            handshape = "A"
            location_part = part
        
        # Extract location and orientation
        if "~" in location_part:
            location = location_part.split("~")[0]
            orientation = location_part.split("~")[1]
        else:
            location = location_part
            orientation = "palm_in"
        
        return handshape, location, orientation
    
    def generate_sign_animation(self, text: str, duration: float = 3.0) -> Dict[str, Any]:
        """Generate complete sign animation from text"""
        try:
            # Convert text to HamNoSys
            hamnosys = self.text_to_hamnosys(text)
            
            # Convert HamNoSys to SiGML
            sigml = self.hamnosys_to_sigml(hamnosys)
            
            # Generate animation data
            animation_data = {
                "text": text,
                "hamnosys": hamnosys,
                "sigml": sigml,
                "duration": duration,
                "fps": 30,
                "total_frames": int(duration * 30),
                "keyframes": [],
                "avatar_config": self.avatar_configs.get(self.config.avatar_type, {}),
                "metadata": {
                    "language": self.config.language,
                    "avatar_type": self.config.avatar_type,
                    "animation_speed": self.config.animation_speed
                }
            }
            
            # Generate keyframes
            animation_data["keyframes"] = self._generate_keyframes(hamnosys, duration)
            
            return animation_data
            
        except Exception as e:
            logger.error(f"Error generating sign animation: {e}")
            return {"error": str(e)}
    
    def _generate_keyframes(self, hamnosys: str, duration: float) -> List[Dict[str, Any]]:
        """Generate animation keyframes from HamNoSys"""
        keyframes = []
        fps = 30
        total_frames = int(duration * fps)
        
        # Parse HamNoSys parts
        parts = hamnosys.split("~")
        
        for frame in range(total_frames):
            time = frame / total_frames
            
            # Determine current part
            part_index = int(time * len(parts))
            current_part = parts[min(part_index, len(parts) - 1)]
            
            # Parse part
            handshape, location, orientation = self._parse_hamnosys_part(current_part)
            
            # Generate keyframe
            keyframe = {
                "frame": frame,
                "timestamp": frame / fps,
                "handshape": handshape,
                "location": location,
                "orientation": orientation,
                "left_handshape": "A",
                "left_location": "chest",
                "left_orientation": "palm_in",
                "facial_expression": "neutral",
                "eyebrow_position": "neutral",
                "head_position": "straight",
                "body_position": "neutral"
            }
            
            keyframes.append(keyframe)
        
        return keyframes
    
    def export_to_jasigning(self, animation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Export animation to JASigning format"""
        try:
            jasigning_data = {
                "version": "1.0",
                "avatar": "jasigning",
                "animation": {
                    "duration": animation_data["duration"],
                    "fps": animation_data["fps"],
                    "keyframes": []
                },
                "metadata": animation_data["metadata"]
            }
            
            # Convert keyframes to JASigning format
            for keyframe in animation_data["keyframes"]:
                jasigning_keyframe = {
                    "time": keyframe["timestamp"],
                    "right_hand": {
                        "shape": keyframe["handshape"],
                        "position": keyframe["location"],
                        "orientation": keyframe["orientation"]
                    },
                    "left_hand": {
                        "shape": keyframe["left_handshape"],
                        "position": keyframe["left_location"],
                        "orientation": keyframe["left_orientation"]
                    },
                    "face": {
                        "expression": keyframe["facial_expression"],
                        "eyebrows": keyframe["eyebrow_position"],
                        "head": keyframe["head_position"]
                    },
                    "body": {
                        "position": keyframe["body_position"]
                    }
                }
                
                jasigning_data["animation"]["keyframes"].append(jasigning_keyframe)
            
            return jasigning_data
            
        except Exception as e:
            logger.error(f"Error exporting to JASigning: {e}")
            return {"error": str(e)}
    
    def get_dictionary_stats(self) -> Dict[str, Any]:
        """Get dictionary statistics"""
        return {
            "total_words": len(self.hamnosys_dictionary),
            "language": self.config.language,
            "avatar_type": self.config.avatar_type,
            "templates_available": list(self.sigml_templates.keys()),
            "hamnosys_symbols": len(self.hamnosys_symbols)
        }
    
    def add_custom_sign(self, word: str, hamnosys: str) -> bool:
        """Add custom sign to dictionary"""
        try:
            self.hamnosys_dictionary[word.lower()] = hamnosys
            logger.info(f"Added custom sign: {word} -> {hamnosys}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding custom sign: {e}")
            return False
    
    def validate_sigml(self, sigml: str) -> bool:
        """Validate SiGML syntax"""
        try:
            # Parse XML
            ET.fromstring(sigml)
            return True
            
        except ET.ParseError:
            return False
        except Exception as e:
            logger.error(f"Error validating SiGML: {e}")
            return False

# Create singleton instance
default_hamnosys_config = HamNoSysConfig()
sigml_synthesis = SiGMLSynthesis(default_hamnosys_config)

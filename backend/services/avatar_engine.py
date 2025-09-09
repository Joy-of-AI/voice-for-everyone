"""
Avatar Engine Service

This module handles the conversion of 3D pose keypoints into renderable 3D avatar 
structures and provides export functionality for Three.js scenes.

Features:
- Convert pose keypoints to 3D avatar representation
- Generate Three.js scene data
- Support for body, hands, and face rendering
- Customizable avatar appearance and animation
"""

import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
import math
import time
from dataclasses import dataclass, asdict
from services.asl_processor import PoseKeypoints, ASLAnimation

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class AvatarConfig:
    """Configuration for avatar appearance and behavior"""
    body_color: str = "#8B4513"  # Brown skin tone
    joint_color: str = "#FF6B6B"  # Red joints
    bone_color: str = "#4ECDC4"  # Teal bones
    hand_color: str = "#FFE66D"  # Yellow hands
    face_color: str = "#FF8E53"  # Orange face
    joint_size: float = 0.02
    bone_thickness: float = 0.01
    show_face_mesh: bool = True
    show_hand_details: bool = True
    animation_smoothing: bool = True
    scale_factor: float = 1.0

@dataclass
class Joint3D:
    """Represents a 3D joint in the avatar"""
    id: int
    name: str
    position: Tuple[float, float, float]
    visibility: float
    color: str
    size: float

@dataclass
class Bone3D:
    """Represents a bone connection between two joints"""
    id: int
    name: str
    start_joint: int
    end_joint: int
    color: str
    thickness: float

@dataclass
class Hand3D:
    """Represents a 3D hand with all finger joints"""
    side: str  # "left" or "right"
    joints: List[Joint3D]
    bones: List[Bone3D]
    palm_center: Tuple[float, float, float]
    fingers: Dict[str, List[int]]  # finger name -> joint indices

@dataclass
class Face3D:
    """Represents a 3D face with landmarks"""
    landmarks: List[Joint3D]
    contour: List[int]  # Indices for face contour
    eyes: Dict[str, List[int]]  # left/right eye landmark indices
    mouth: List[int]  # Mouth landmark indices
    eyebrows: Dict[str, List[int]]  # left/right eyebrow indices

@dataclass
class Avatar3D:
    """Complete 3D avatar representation"""
    frame_index: int
    timestamp: float
    body_joints: List[Joint3D]
    body_bones: List[Bone3D]
    left_hand: Optional[Hand3D]
    right_hand: Optional[Hand3D]
    face: Optional[Face3D]
    bounding_box: Dict[str, float]  # min/max x,y,z
    config: AvatarConfig

class AvatarEngine:
    """Main avatar engine for converting poses to 3D avatars"""
    
    def __init__(self, config: Optional[AvatarConfig] = None):
        """Initialize the avatar engine"""
        self.config = config or AvatarConfig()
        self.avatar_cache = {}  # Cache for performance
        
        # MediaPipe pose indices
        self.pose_indices = {
            'nose': 0, 'left_eye_inner': 1, 'left_eye': 2, 'left_eye_outer': 3,
            'right_eye_inner': 4, 'right_eye': 5, 'right_eye_outer': 6,
            'left_ear': 7, 'right_ear': 8, 'mouth_left': 9, 'mouth_right': 10,
            'left_shoulder': 11, 'right_shoulder': 12, 'left_elbow': 13, 'right_elbow': 14,
            'left_wrist': 15, 'right_wrist': 16, 'left_pinky': 17, 'right_pinky': 18,
            'left_index': 19, 'right_index': 20, 'left_thumb': 21, 'right_thumb': 22,
            'left_hip': 23, 'right_hip': 24, 'left_knee': 25, 'right_knee': 26,
            'left_ankle': 27, 'right_ankle': 28, 'left_heel': 29, 'right_heel': 30,
            'left_foot_index': 31, 'right_foot_index': 32
        }
        
        # Hand landmarks (21 points each)
        self.hand_indices = {
            'wrist': 0,
            'thumb_cmc': 1, 'thumb_mcp': 2, 'thumb_ip': 3, 'thumb_tip': 4,
            'index_mcp': 5, 'index_pip': 6, 'index_dip': 7, 'index_tip': 8,
            'middle_mcp': 9, 'middle_pip': 10, 'middle_dip': 11, 'middle_tip': 12,
            'ring_mcp': 13, 'ring_pip': 14, 'ring_dip': 15, 'ring_tip': 16,
            'pinky_mcp': 17, 'pinky_pip': 18, 'pinky_dip': 19, 'pinky_tip': 20
        }
        
        # Body bone connections
        self.body_connections = [
            # Head
            ('nose', 'left_eye'), ('nose', 'right_eye'),
            ('left_eye', 'left_ear'), ('right_eye', 'right_ear'),
            ('mouth_left', 'mouth_right'),
            
            # Torso
            ('left_shoulder', 'right_shoulder'),
            ('left_shoulder', 'left_hip'), ('right_shoulder', 'right_hip'),
            ('left_hip', 'right_hip'),
            
            # Arms
            ('left_shoulder', 'left_elbow'), ('left_elbow', 'left_wrist'),
            ('right_shoulder', 'right_elbow'), ('right_elbow', 'right_wrist'),
            
            # Legs
            ('left_hip', 'left_knee'), ('left_knee', 'left_ankle'),
            ('right_hip', 'right_knee'), ('right_knee', 'right_ankle'),
            
            # Feet
            ('left_ankle', 'left_heel'), ('left_ankle', 'left_foot_index'),
            ('right_ankle', 'right_heel'), ('right_ankle', 'right_foot_index')
        ]
        
        logger.info("Avatar Engine initialized successfully")
    
    def create_avatar_from_pose(self, pose: PoseKeypoints) -> Avatar3D:
        """Convert PoseKeypoints into Avatar3D object"""
        try:
            # Convert body keypoints
            body_joints = self._convert_body_keypoints(pose.body_keypoints)
            body_bones = self._create_body_bones(body_joints)
            
            # Convert hand keypoints
            left_hand = None
            right_hand = None
            
            if pose.left_hand_keypoints is not None and len(pose.left_hand_keypoints) > 0:
                left_hand = self._convert_hand_keypoints(pose.left_hand_keypoints, "left")
            
            if pose.right_hand_keypoints is not None and len(pose.right_hand_keypoints) > 0:
                right_hand = self._convert_hand_keypoints(pose.right_hand_keypoints, "right")
            
            # Convert face keypoints
            face = None
            if pose.face_keypoints is not None and len(pose.face_keypoints) > 0:
                face = self._convert_face_keypoints(pose.face_keypoints)
            
            # Calculate bounding box
            bounding_box = self._calculate_bounding_box(body_joints, left_hand, right_hand, face)
            
            return Avatar3D(
                frame_index=pose.frame_index,
                timestamp=pose.timestamp,
                body_joints=body_joints,
                body_bones=body_bones,
                left_hand=left_hand,
                right_hand=right_hand,
                face=face,
                bounding_box=bounding_box,
                config=self.config
            )
            
        except Exception as e:
            logger.error(f"Error creating avatar from pose: {e}")
            raise
    
    def _convert_body_keypoints(self, keypoints: np.ndarray) -> List[Joint3D]:
        """Convert body keypoints to 3D joints"""
        joints = []
        
        for name, idx in self.pose_indices.items():
            if idx < len(keypoints):
                point = keypoints[idx]
                position = (float(point[0]), float(point[1]), float(point[2]) if len(point) > 2 else 0.0)
                visibility = float(point[3]) if len(point) > 3 else 1.0
                
                joint = Joint3D(
                    id=idx,
                    name=name,
                    position=position,
                    visibility=visibility,
                    color=self.config.joint_color,
                    size=self.config.joint_size
                )
                joints.append(joint)
        
        return joints
    
    def _convert_hand_keypoints(self, keypoints: np.ndarray, hand: str) -> Hand3D:
        """Convert hand keypoints to 3D hand representation"""
        joints = []
        
        for name, idx in self.hand_indices.items():
            if idx < len(keypoints):
                point = keypoints[idx]
                position = (float(point[0]), float(point[1]), float(point[2]) if len(point) > 2 else 0.0)
                visibility = float(point[3]) if len(point) > 3 else 1.0
                
                joint = Joint3D(
                    id=idx,
                    name=f"{hand}_{name}",
                    position=position,
                    visibility=visibility,
                    color=self.config.hand_color,
                    size=self.config.joint_size * 0.8
                )
                joints.append(joint)
        
        # Create hand bones
        bones = self._create_hand_bones(joints, hand)
        
        # Calculate palm center
        wrist_pos = joints[0].position if joints else (0, 0, 0)
        palm_center = wrist_pos
        
        # Define finger joint groups
        fingers = {
            'thumb': [1, 2, 3, 4],
            'index': [5, 6, 7, 8],
            'middle': [9, 10, 11, 12],
            'ring': [13, 14, 15, 16],
            'pinky': [17, 18, 19, 20]
        }
        
        return Hand3D(
            side=hand,
            joints=joints,
            bones=bones,
            palm_center=palm_center,
            fingers=fingers
        )
    
    def _convert_face_keypoints(self, keypoints: np.ndarray) -> Face3D:
        """Convert face keypoints to 3D face representation"""
        landmarks = []
        
        # Convert face landmarks
        for i, point in enumerate(keypoints):
            position = (float(point[0]), float(point[1]), float(point[2]) if len(point) > 2 else 0.0)
            visibility = float(point[3]) if len(point) > 3 else 1.0
            
            landmark = Joint3D(
                id=i,
                name=f"face_{i}",
                position=position,
                visibility=visibility,
                color=self.config.face_color,
                size=self.config.joint_size * 0.3
            )
            landmarks.append(landmark)
        
        # Define face regions (simplified indices)
        contour = list(range(0, 17)) if len(landmarks) > 17 else []
        left_eye = list(range(36, 42)) if len(landmarks) > 42 else []
        right_eye = list(range(42, 48)) if len(landmarks) > 48 else []
        mouth = list(range(48, 68)) if len(landmarks) > 68 else []
        left_eyebrow = list(range(17, 22)) if len(landmarks) > 22 else []
        right_eyebrow = list(range(22, 27)) if len(landmarks) > 27 else []
        
        return Face3D(
            landmarks=landmarks,
            contour=contour,
            eyes={'left': left_eye, 'right': right_eye},
            mouth=mouth,
            eyebrows={'left': left_eyebrow, 'right': right_eyebrow}
        )
    
    def _create_body_bones(self, joints: List[Joint3D]) -> List[Bone3D]:
        """Create bones connecting body joints"""
        bones = []
        joint_by_name = {joint.name: joint for joint in joints}
        
        bone_id = 0
        for start_name, end_name in self.body_connections:
            if start_name in joint_by_name and end_name in joint_by_name:
                start_joint = joint_by_name[start_name]
                end_joint = joint_by_name[end_name]
                
                bone = Bone3D(
                    id=bone_id,
                    name=f"{start_name}_to_{end_name}",
                    start_joint=start_joint.id,
                    end_joint=end_joint.id,
                    color=self.config.bone_color,
                    thickness=self.config.bone_thickness
                )
                bones.append(bone)
                bone_id += 1
        
        return bones
    
    def _create_hand_bones(self, joints: List[Joint3D], hand: str) -> List[Bone3D]:
        """Create bones for hand fingers"""
        bones = []
        
        # Hand bone connections
        hand_connections = [
            # Thumb
            (0, 1), (1, 2), (2, 3), (3, 4),
            # Index
            (0, 5), (5, 6), (6, 7), (7, 8),
            # Middle
            (0, 9), (9, 10), (10, 11), (11, 12),
            # Ring
            (0, 13), (13, 14), (14, 15), (15, 16),
            # Pinky
            (0, 17), (17, 18), (18, 19), (19, 20),
            # Palm connections
            (5, 9), (9, 13), (13, 17)
        ]
        
        for bone_id, (start_idx, end_idx) in enumerate(hand_connections):
            if start_idx < len(joints) and end_idx < len(joints):
                bone = Bone3D(
                    id=bone_id,
                    name=f"{hand}_bone_{start_idx}_to_{end_idx}",
                    start_joint=start_idx,
                    end_joint=end_idx,
                    color=self.config.hand_color,
                    thickness=self.config.bone_thickness * 0.7
                )
                bones.append(bone)
        
        return bones
    
    def _calculate_bounding_box(self, body_joints: List[Joint3D], 
                              left_hand: Optional[Hand3D], 
                              right_hand: Optional[Hand3D], 
                              face: Optional[Face3D]) -> Dict[str, float]:
        """Calculate bounding box for the entire avatar"""
        all_positions = []
        
        # Collect all positions
        for joint in body_joints:
            all_positions.append(joint.position)
        
        if left_hand:
            for joint in left_hand.joints:
                all_positions.append(joint.position)
        
        if right_hand:
            for joint in right_hand.joints:
                all_positions.append(joint.position)
        
        if face:
            for landmark in face.landmarks:
                all_positions.append(landmark.position)
        
        if not all_positions:
            return {'min_x': 0, 'max_x': 1, 'min_y': 0, 'max_y': 1, 'min_z': 0, 'max_z': 1}
        
        # Calculate bounds
        positions_array = np.array(all_positions)
        min_vals = np.min(positions_array, axis=0)
        max_vals = np.max(positions_array, axis=0)
        
        return {
            'min_x': float(min_vals[0]), 'max_x': float(max_vals[0]),
            'min_y': float(min_vals[1]), 'max_y': float(max_vals[1]),
            'min_z': float(min_vals[2]) if len(min_vals) > 2 else 0.0,
            'max_z': float(max_vals[2]) if len(max_vals) > 2 else 0.0
        }
    
    def generate_animation_frames(self, animation: ASLAnimation) -> List[Dict[str, Any]]:
        """Generate a list of frame data for rendering"""
        try:
            frames_data = []
            
            for pose in animation.frames:
                avatar = self.create_avatar_from_pose(pose)
                frame_data = self._export_avatar_frame(avatar, pose.frame_index, animation.fps)
                frames_data.append(frame_data)
            
            logger.info(f"Generated {len(frames_data)} animation frames")
            return frames_data
            
        except Exception as e:
            logger.error(f"Error generating animation frames: {e}")
            raise
    
    def _export_avatar_frame(self, avatar: Avatar3D, frame_index: int, fps: int) -> Dict[str, Any]:
        """Export single avatar frame data"""
        try:
            frame_data = {
                'frame_index': frame_index,
                'timestamp': avatar.timestamp,
                'bounding_box': avatar.bounding_box,
                'body': {
                    'joints': [
                        {
                            'id': joint.id,
                            'name': joint.name,
                            'position': joint.position,
                            'visibility': joint.visibility,
                            'color': joint.color,
                            'size': joint.size
                        }
                        for joint in avatar.body_joints
                    ],
                    'bones': [
                        {
                            'id': bone.id,
                            'name': bone.name,
                            'start_joint': bone.start_joint,
                            'end_joint': bone.end_joint,
                            'color': bone.color,
                            'thickness': bone.thickness
                        }
                        for bone in avatar.body_bones
                    ]
                },
                'hands': {},
                'face': None
            }
            
            # Add hand data
            if avatar.left_hand:
                frame_data['hands']['left'] = {
                    'joints': [
                        {
                            'id': joint.id,
                            'name': joint.name,
                            'position': joint.position,
                            'visibility': joint.visibility,
                            'color': joint.color,
                            'size': joint.size
                        }
                        for joint in avatar.left_hand.joints
                    ],
                    'bones': [
                        {
                            'id': bone.id,
                            'name': bone.name,
                            'start_joint': bone.start_joint,
                            'end_joint': bone.end_joint,
                            'color': bone.color,
                            'thickness': bone.thickness
                        }
                        for bone in avatar.left_hand.bones
                    ],
                    'palm_center': avatar.left_hand.palm_center,
                    'fingers': avatar.left_hand.fingers
                }
            
            if avatar.right_hand:
                frame_data['hands']['right'] = {
                    'joints': [
                        {
                            'id': joint.id,
                            'name': joint.name,
                            'position': joint.position,
                            'visibility': joint.visibility,
                            'color': joint.color,
                            'size': joint.size
                        }
                        for joint in avatar.right_hand.joints
                    ],
                    'bones': [
                        {
                            'id': bone.id,
                            'name': bone.name,
                            'start_joint': bone.start_joint,
                            'end_joint': bone.end_joint,
                            'color': bone.color,
                            'thickness': bone.thickness
                        }
                        for bone in avatar.right_hand.bones
                    ],
                    'palm_center': avatar.right_hand.palm_center,
                    'fingers': avatar.right_hand.fingers
                }
            
            # Add face data
            if avatar.face:
                frame_data['face'] = {
                    'landmarks': [
                        {
                            'id': landmark.id,
                            'name': landmark.name,
                            'position': landmark.position,
                            'visibility': landmark.visibility,
                            'color': landmark.color,
                            'size': landmark.size
                        }
                        for landmark in avatar.face.landmarks
                    ],
                    'contour': avatar.face.contour,
                    'eyes': avatar.face.eyes,
                    'mouth': avatar.face.mouth,
                    'eyebrows': avatar.face.eyebrows
                }
            
            return frame_data
            
        except Exception as e:
            logger.error(f"Error exporting avatar frame: {e}")
            raise
    
    def generate_threejs_scene(self, animation: ASLAnimation) -> Dict[str, Any]:
        """Generate Three.js scene data for web rendering"""
        try:
            frames_data = self.generate_animation_frames(animation)
            
            # Create Three.js compatible scene structure
            scene_data = {
                'metadata': {
                    'version': '1.0',
                    'type': 'ASL_Animation',
                    'generator': 'BodyLanguageTranslator',
                    'fps': animation.fps,
                    'total_duration': animation.total_duration,
                    'total_frames': len(animation.frames),
                    'created_at': animation.created_at
                },
                'scene': {
                    'name': f"ASL_Scene_{animation.animation_id}",
                    'type': 'Scene',
                    'children': []
                },
                'animations': [
                    {
                        'name': f"ASL_Animation_{animation.animation_id}",
                        'duration': animation.total_duration,
                        'fps': animation.fps,
                        'frames': frames_data
                    }
                ],
                'materials': {
                    'body_material': {
                        'type': 'MeshBasicMaterial',
                        'color': self.config.body_color,
                        'transparent': True,
                        'opacity': 0.8
                    },
                    'joint_material': {
                        'type': 'MeshBasicMaterial',
                        'color': self.config.joint_color,
                        'transparent': True,
                        'opacity': 1.0
                    },
                    'bone_material': {
                        'type': 'LineBasicMaterial',
                        'color': self.config.bone_color,
                        'linewidth': self.config.bone_thickness * 100
                    },
                    'hand_material': {
                        'type': 'MeshBasicMaterial',
                        'color': self.config.hand_color,
                        'transparent': True,
                        'opacity': 0.9
                    },
                    'face_material': {
                        'type': 'PointsMaterial',
                        'color': self.config.face_color,
                        'size': self.config.joint_size * 0.5
                    }
                },
                'camera': {
                    'type': 'PerspectiveCamera',
                    'fov': 75,
                    'aspect': 16/9,
                    'near': 0.1,
                    'far': 1000,
                    'position': [0, 0, 3],
                    'lookAt': [0.5, 0.5, 0]
                },
                'lights': [
                    {
                        'type': 'AmbientLight',
                        'color': '#404040',
                        'intensity': 0.6
                    },
                    {
                        'type': 'DirectionalLight',
                        'color': '#ffffff',
                        'intensity': 0.8,
                        'position': [1, 1, 1]
                    }
                ],
                'gloss': {
                    'original_text': animation.gloss.original_text,
                    'gloss_sequence': animation.gloss.gloss_sequence,
                    'timing': animation.gloss.timing,
                    'metadata': animation.gloss.metadata
                }
            }
            
            logger.info(f"Generated Three.js scene with {len(frames_data)} frames")
            return scene_data
            
        except Exception as e:
            logger.error(f"Error generating Three.js scene: {e}")
            raise
    
    def export_animation_json(self, animation: ASLAnimation, output_path: str):
        """Export animation to JSON file"""
        try:
            scene_data = self.generate_threejs_scene(animation)
            
            with open(output_path, 'w') as f:
                json.dump(scene_data, f, indent=2)
            
            logger.info(f"Animation exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting animation to JSON: {e}")
            raise

# Initialize the global avatar engine instance
avatar_engine = AvatarEngine()

# Export the main functions for easy import
__all__ = ['AvatarEngine', 'AvatarConfig', 'Joint3D', 'Bone3D', 'Hand3D', 'Face3D', 'Avatar3D', 'avatar_engine']

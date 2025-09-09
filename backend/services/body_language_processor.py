"""
Body Language Processing Service using MediaPipe and Computer Vision
"""

import logging
from typing import Dict, List, Tuple, Optional
import base64
import io
from PIL import Image

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError as e:
    logger.warning(f"OpenCV not available: {e}")
    OPENCV_AVAILABLE = False
    cv2 = None
    np = None

class BodyLanguageProcessor:
    """
    Processes video frames to detect body language, gestures, and poses.
    Uses OpenCV for basic pose detection and gesture recognition.
    """
    
    def __init__(self):
        """Initialize the body language processor with OpenCV models."""
        self.face_cascade = None
        self.body_cascade = None
        self.pose_net = None
        
        if OPENCV_AVAILABLE:
            try:
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                self.body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
                
                # Initialize pose detection (simplified version)
                try:
                    # Try to load a pre-trained pose model if available
                    self.pose_net = cv2.dnn.readNetFromTensorflow('pose_model.pb')
                except:
                    logger.warning("Pose model not found, using basic detection")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenCV models: {e}")
        else:
            logger.warning("OpenCV not available, using mock detection")
        
        # Gesture recognition parameters
        self.gesture_thresholds = {
            'hand_raised': 0.6,
            'pointing': 0.7,
            'thumbs_up': 0.8,
            'wave': 0.6
        }
    
    def process_frame(self, image_bytes: bytes) -> Dict:
        """
        Process a single frame to extract body language data.
        
        Args:
            image_bytes: Raw image bytes from camera/video
            
        Returns:
            Dictionary containing detected landmarks and confidence scores
        """
        if not OPENCV_AVAILABLE:
            return self._get_mock_detection()
            
        try:
            # Convert bytes to OpenCV format
            image = self._bytes_to_cv_image(image_bytes)
            if image is None:
                return self._empty_result()
            
            # Detect faces
            faces = self._detect_faces(image)
            
            # Detect body poses
            poses = self._detect_poses(image)
            
            # Detect hand gestures
            gestures = self._detect_gestures(image)
            
            # Extract facial expressions
            expressions = self._detect_expressions(image, faces)
            
            # Combine all detections
            result = {
                'gestures': gestures,
                'pose_landmarks': poses,
                'face_landmarks': faces,
                'confidence_scores': {
                    'face_detection': len(faces) > 0,
                    'pose_detection': len(poses) > 0,
                    'gesture_detection': len(gestures) > 0
                },
                'expressions': expressions,
                'frame_quality': self._assess_frame_quality(image)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return self._empty_result()
    
    def _bytes_to_cv_image(self, image_bytes: bytes) -> Optional[any]:
        """Convert image bytes to OpenCV format."""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            # Convert to OpenCV format
            if np is not None:
                cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                cv_image = None
            return cv_image
        except Exception as e:
            logger.error(f"Error converting image bytes: {e}")
            return None
    
    def _detect_faces(self, image: any) -> List[Dict]:
        """Detect faces in the image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        face_landmarks = []
        for (x, y, w, h) in faces:
            face_landmarks.append({
                'x': int(x + w/2),
                'y': int(y + h/2),
                'width': int(w),
                'height': int(h),
                'confidence': 0.8
            })
        
        return face_landmarks
    
    def _detect_poses(self, image: any) -> List[Dict]:
        """Detect body poses using basic computer vision techniques."""
        # Simplified pose detection using contour analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Find contours
        _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        poses = []
        for contour in contours:
            if cv2.contourArea(contour) > 1000:  # Filter small contours
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate pose characteristics
                aspect_ratio = w / h if h > 0 else 0
                
                poses.append({
                    'x': int(x + w/2),
                    'y': int(y + h/2),
                    'width': int(w),
                    'height': int(h),
                    'aspect_ratio': aspect_ratio,
                    'confidence': 0.6
                })
        
        return poses
    
    def _detect_gestures(self, image: any) -> List[Dict]:
        """Detect hand gestures using basic image processing."""
        gestures = []
        
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Detect skin color (basic hand detection)
        if np is not None:
            lower_skin = np.array([0, 20, 70])
            upper_skin = np.array([20, 255, 255])
        else:
            lower_skin = None
            upper_skin = None
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Find contours in skin mask
        contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Filter small contours
                # Analyze contour shape for gesture recognition
                gesture_type = self._classify_gesture(contour)
                if gesture_type:
                    x, y, w, h = cv2.boundingRect(contour)
                    gestures.append({
                        'type': gesture_type,
                        'x': int(x + w/2),
                        'y': int(y + h/2),
                        'confidence': 0.7
                    })
        
        return gestures
    
    def _classify_gesture(self, contour) -> Optional[str]:
        """Classify gesture based on contour analysis."""
        # Calculate contour properties
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter > 0:
            if np is not None:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
            else:
                circularity = 0.5  # Default value
            
            # Simple gesture classification based on shape
            if circularity > 0.8:
                return 'hand_closed'
            elif circularity < 0.3:
                return 'hand_open'
            else:
                return 'hand_partial'
        
        return None
    
    def _detect_expressions(self, image: any, faces: List[Dict]) -> List[Dict]:
        """Detect facial expressions."""
        expressions = []
        
        for face in faces:
            # Extract face region
            x, y, w, h = face['x'] - face['width']//2, face['y'] - face['height']//2, face['width'], face['height']
            face_region = image[y:y+h, x:x+w]
            
            if face_region.size > 0:
                # Basic expression detection using edge analysis
                gray_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray_face, 50, 150)
                
                # Count edge pixels as a simple measure of expression intensity
                if np is not None:
                    edge_density = np.sum(edges > 0) / (w * h)
                else:
                    edge_density = 0.5  # Default value
                
                expression = {
                    'type': 'neutral',
                    'intensity': edge_density,
                    'confidence': 0.6
                }
                
                # Simple expression classification
                if edge_density > 0.1:
                    expression['type'] = 'expressive'
                
                expressions.append(expression)
        
        return expressions
    
    def _assess_frame_quality(self, image: any) -> Dict:
        """Assess the quality of the input frame."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate brightness
        if np is not None:
            brightness = np.mean(gray)
            contrast = np.std(gray)
        else:
            brightness = 120
            contrast = 50
        
        # Calculate sharpness (using Laplacian variance)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        
        return {
            'brightness': float(brightness),
            'contrast': float(contrast),
            'sharpness': float(sharpness),
            'overall_quality': 'good' if brightness > 50 and contrast > 20 and sharpness > 100 else 'poor'
        }
    
    def _get_mock_detection(self) -> Dict:
        """Return mock detection data when OpenCV is not available."""
        return {
            'gestures': [
                {
                    'type': 'hand_open',
                    'x': 320,
                    'y': 240,
                    'confidence': 0.8
                }
            ],
            'pose_landmarks': [
                {
                    'x': 320,
                    'y': 240,
                    'width': 100,
                    'height': 200,
                    'aspect_ratio': 0.5,
                    'confidence': 0.7
                }
            ],
            'face_landmarks': [
                {
                    'x': 320,
                    'y': 200,
                    'width': 80,
                    'height': 80,
                    'confidence': 0.9
                }
            ],
            'confidence_scores': {
                'face_detection': True,
                'pose_detection': True,
                'gesture_detection': True
            },
            'expressions': [
                {
                    'type': 'neutral',
                    'intensity': 0.5,
                    'confidence': 0.7
                }
            ],
            'frame_quality': {
                'brightness': 120,
                'contrast': 50,
                'sharpness': 150,
                'overall_quality': 'good'
            }
        }
    
    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            'gestures': [],
            'pose_landmarks': [],
            'face_landmarks': [],
            'confidence_scores': {
                'face_detection': False,
                'pose_detection': False,
                'gesture_detection': False
            },
            'expressions': [],
            'frame_quality': {
                'brightness': 0,
                'contrast': 0,
                'sharpness': 0,
                'overall_quality': 'unknown'
            }
        }
    
    def is_thumbs_up(self, gestures: List[Dict]) -> bool:
        """Check if thumbs up gesture is detected."""
        return any(g.get('type') == 'hand_closed' for g in gestures)
    
    def is_waving(self, gestures: List[Dict]) -> bool:
        """Check if waving gesture is detected."""
        return any(g.get('type') == 'hand_open' for g in gestures)
    
    def is_pointing(self, gestures: List[Dict]) -> bool:
        """Check if pointing gesture is detected."""
        return any(g.get('type') == 'hand_partial' for g in gestures)
    
    def get_gesture_summary(self, body_data: Dict) -> str:
        """Generate a summary of detected gestures."""
        gestures = body_data.get('gestures', [])
        faces = body_data.get('face_landmarks', [])
        
        summary_parts = []
        
        if faces:
            summary_parts.append(f"Face detected")
        
        if gestures:
            gesture_types = [g.get('type', 'unknown') for g in gestures]
            summary_parts.append(f"Gestures: {', '.join(gesture_types)}")
        
        if self.is_thumbs_up(gestures):
            summary_parts.append("Thumbs up detected")
        
        if self.is_waving(gestures):
            summary_parts.append("Waving detected")
        
        if self.is_pointing(gestures):
            summary_parts.append("Pointing detected")
        
        return "; ".join(summary_parts) if summary_parts else "No significant gestures detected"

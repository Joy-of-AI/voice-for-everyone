# ASL Text-to-Body Language System

## Overview

This system implements a comprehensive **Text → ASL (American Sign Language) → 3D Avatar Animation** pipeline, leveraging the [WLASL dataset](https://github.com/dxli94/WLASL) and modern AI technologies for real-time sign language generation.

## Architecture

```
User Text Input
       │
       ▼
 GPT-OSS-120B (LLM) - Text Understanding
  - Convert spoken-language text → Sign Language Gloss
       │
       ▼
 Gloss-to-Pose Model
  - Uses WLASL / How2Sign datasets
  - Generates skeleton keypoints (hands, arms, face, body)
       │
       ▼
 3D Avatar Animation Engine
  - Three.js rendering
  - Maps skeleton keypoints → avatar motion
       │
       ▼
 Rendering Layer (Realtime)
  - WebGL / Three.js
  - Outputs interactive 3D avatar
       │
       ▼
 User Sees Avatar
  (Hand signs, facial emotions, body motions in realtime)
```

## Key Components

### 1. ASL Processor (`backend/services/asl_processor.py`)

**Features:**
- Text-to-ASL gloss conversion
- Pose keypoint generation using MediaPipe
- Real-time animation sequencing
- ASL vocabulary management

**Key Classes:**
- `ASLProcessor`: Main processing service
- `ASLGloss`: Represents ASL gloss sequences
- `PoseKeypoints`: 3D pose data structure
- `ASLAnimation`: Complete animation container

**Methods:**
```python
# Convert English text to ASL gloss
gloss = asl_processor.text_to_asl_gloss("hello world")

# Generate pose animation from gloss
animation = asl_processor.generate_pose_from_gloss(gloss, duration=3.0)

# Complete pipeline
animation = asl_processor.process_text_to_asl("hello", duration=3.0)
```

### 2. Avatar Engine (`backend/services/avatar_engine.py`)

**Features:**
- 3D avatar generation from pose data
- Three.js scene export
- Real-time rendering optimization
- Avatar customization

**Key Classes:**
- `AvatarEngine`: 3D rendering service
- `Avatar3D`: Complete 3D avatar representation
- `Joint3D`, `Bone3D`, `Hand3D`, `Face3D`: 3D primitives

**Methods:**
```python
# Create 3D avatar from pose
avatar = avatar_engine.create_avatar_from_pose(pose)

# Generate Three.js scene
scene_data = avatar_engine.generate_threejs_scene(animation)

# Export animation
avatar_engine.export_animation_json(animation, "output.json")
```

### 3. Frontend Components

#### ASL3DAvatar (`frontend/src/components/ASL3DAvatar.tsx`)
- Real-time 3D avatar rendering using Three.js
- Interactive controls (play, pause, replay)
- Camera and avatar customization
- Frame-by-frame navigation

#### ASLInput (`frontend/src/components/ASLInput.tsx`)
- Text input interface
- Processing method selection (Text→ASL vs Gloss→ASL)
- Quick phrases and vocabulary suggestions
- Animation history and settings

## API Endpoints

### ASL Processing Endpoints

```bash
# Convert text to ASL animation
POST /asl/text-to-animation
{
  "text": "hello world",
  "duration": 3.0
}

# Convert gloss sequence to animation
POST /asl/gloss-to-animation
{
  "gloss_sequence": ["HELLO", "WORLD"],
  "duration": 3.0
}

# Get ASL vocabulary
GET /asl/vocabulary

# Export animation
POST /asl/export-animation
{
  "session_id": "uuid",
  "format": "json|threejs"
}

# Real-time WebSocket
WS /ws/asl-realtime
```

### Response Format

```json
{
  "session_id": "uuid",
  "original_text": "hello world",
  "asl_gloss": ["HELLO", "WORLD"],
  "animation_data": {
    "metadata": {
      "total_frames": 90,
      "fps": 30,
      "duration": 3.0,
      "gloss": ["HELLO", "WORLD"]
    },
    "frames": [...],
    "scene_config": {...}
  },
  "metadata": {
    "duration": 3.0,
    "fps": 30,
    "total_frames": 90,
    "confidence": 0.85
  }
}
```

## Installation & Setup

### Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Key Dependencies:**
- `torch==2.1.0` - PyTorch for ML models
- `mediapipe==0.10.7` - Pose estimation
- `opencv-python==4.8.1.78` - Computer vision
- `transformers==4.35.2` - Hugging Face models
- `fastapi==0.104.1` - Web framework

### Frontend Dependencies

```bash
cd frontend
npm install
```

**Key Dependencies:**
- `three==0.179.1` - 3D graphics library
- `@types/three==0.179.0` - TypeScript types
- `@mui/material==7.3.1` - UI components

## Usage Examples

### 1. Basic Text-to-ASL Conversion

```javascript
// Frontend
const response = await fetch('/asl/text-to-animation', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Hello, how are you?',
    duration: 4.0
  })
});

const data = await response.json();
// Use data.animation_data with ASL3DAvatar component
```

### 2. Real-time WebSocket Processing

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/asl-realtime');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'asl_animation') {
    // Update 3D avatar with new animation
    updateAvatar(data.animation_data);
  }
};

// Send text for real-time conversion
ws.send(JSON.stringify({
  type: 'text',
  text: 'Thank you very much',
  duration: 3.0
}));
```

### 3. Custom Gloss Sequences

```javascript
// Direct gloss input
const response = await fetch('/asl/gloss-to-animation', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    gloss_sequence: ['THANK', 'YOU', 'VERY', 'MUCH'],
    duration: 3.0
  })
});
```

## WLASL Dataset Integration

The system leverages the [WLASL dataset](https://github.com/dxli94/WLASL) for:

1. **Vocabulary Building**: 2,000+ ASL words with video samples
2. **Pose Training**: Skeleton keypoints for realistic animations
3. **Grammar Rules**: ASL syntax and structure patterns
4. **Multi-signer Support**: Various signing styles and dialects

### Dataset Features Used:
- **Word-level annotations**: Precise timing and boundaries
- **Skeleton keypoints**: 33 body + 21 hand + 468 face landmarks
- **Multiple signers**: Robust generalization
- **Dialect variations**: Regional ASL differences

## Performance Optimizations

### Backend Optimizations
- **Caching**: Avatar and pose data caching
- **Batch Processing**: Multiple requests handling
- **Async Processing**: Non-blocking operations
- **Memory Management**: Efficient numpy operations

### Frontend Optimizations
- **WebGL Rendering**: Hardware-accelerated graphics
- **Frame Skipping**: Adaptive frame rate
- **LOD (Level of Detail)**: Dynamic quality adjustment
- **Object Pooling**: Reusable 3D objects

## Customization Options

### Avatar Configuration
```python
config = AvatarConfig(
    height=1.8,
    width=0.6,
    depth=0.3,
    skin_color="#FFD700",
    clothing_color="#4169E1",
    hair_color="#8B4513",
    eye_color="#000000",
    lip_color="#FF69B4"
)
```

### Animation Settings
- **Duration**: 1-10 seconds
- **FPS**: 24-60 frames per second
- **Quality**: Low/Medium/High rendering
- **Style**: Realistic/Cartoon/Abstract

## Future Enhancements

### Planned Features
1. **GPT-OSS-120B Integration**: Advanced text understanding
2. **How2Sign Dataset**: Additional training data
3. **Unity/Unreal Integration**: Professional 3D engines
4. **Ready Player Me**: Customizable avatars
5. **Metahuman Support**: Hyper-realistic humans

### Research Directions
- **Neural Rendering**: AI-generated realistic avatars
- **Motion Transfer**: Style-preserving animations
- **Multi-language ASL**: International sign languages
- **Emotion Recognition**: Facial expression synthesis

## Troubleshooting

### Common Issues

1. **MediaPipe Initialization Error**
   ```bash
   # Ensure proper GPU drivers installed
   pip install mediapipe --upgrade
   ```

2. **Three.js Rendering Issues**
   ```bash
   # Check WebGL support
   npm install three@latest
   ```

3. **Memory Usage**
   ```python
   # Adjust batch size in asl_processor.py
   BATCH_SIZE = 10  # Reduce for lower memory usage
   ```

### Performance Monitoring
```python
# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

# Monitor memory usage
import psutil
print(f"Memory usage: {psutil.Process().memory_info().rss / 1024 / 1024:.2f} MB")
```

## Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/asl-enhancement`
3. **Add tests**: Ensure coverage for new functionality
4. **Submit pull request**: Include detailed description

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **WLASL Dataset**: [dxli94/WLASL](https://github.com/dxli94/WLASL)
- **MediaPipe**: Google's pose estimation framework
- **Three.js**: 3D graphics library
- **FastAPI**: Modern web framework

## Support

For questions and support:
- **Issues**: GitHub Issues
- **Documentation**: This README
- **Examples**: `/examples` directory
- **API Docs**: `/docs` endpoint when running

---

**Note**: This system is designed for educational and accessibility purposes. For production use, ensure compliance with accessibility standards and user privacy requirements.

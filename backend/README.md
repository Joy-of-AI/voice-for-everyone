# Body Language Translator Backend

A comprehensive AI-powered backend system for translating body language to text/audio and vice versa, designed to help people with communication disabilities.

## Features

- **Body Language Processing**: Real-time gesture detection using MediaPipe
- **AI Translation**: Context-aware translation using GPT-4
- **Audio Processing**: Speech-to-text and text-to-speech capabilities
- **Real-time Communication**: WebSocket support for live translation
- **Database Storage**: SQLite for user data and ChromaDB for vector embeddings
- **Comprehensive Testing**: Full test suite for reliability and accuracy

## Architecture

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── models/                 # Pydantic data models
│   ├── __init__.py
│   └── translation_models.py
├── services/               # Core business logic
│   ├── __init__.py
│   ├── ai_translator.py    # GPT-4 integration
│   ├── body_language_processor.py  # MediaPipe processing
│   ├── audio_processor.py  # Speech processing
│   └── database_manager.py # Database operations
├── utils/                  # Utility functions
│   ├── __init__.py
│   └── websocket_manager.py
└── test_backend.py         # Comprehensive test suite
```

## Installation

1. **Clone the repository**
   ```bash
   cd body-language-translator/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Starting the Server

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the server
python main.py
```

The server will start on `http://localhost:8000`

### API Endpoints

#### Health Check
- `GET /` - Health check endpoint

#### Translation Endpoints
- `POST /translate/body-to-text` - Convert body language video to text
- `POST /translate/text-to-body` - Convert text to body language instructions
- `POST /translate/audio-to-body` - Convert audio to body language instructions
- `POST /translate/body-to-audio` - Convert body language to audio speech

#### Real-time Communication
- `WebSocket /ws/realtime-translation` - Real-time translation via WebSocket

#### Session Management
- `GET /sessions/{session_id}` - Retrieve translation session
- `GET /sessions` - Get recent sessions
- `POST /feedback` - Submit feedback for translation

### Example Usage

#### Body Language to Text
```python
import requests

# Upload video file
files = {'video_file': open('gesture_video.mp4', 'rb')}
data = {'context': 'Greeting gesture'}
response = requests.post('http://localhost:8000/translate/body-to-text', 
                        files=files, data=data)
print(response.json())
```

#### Text to Body Language
```python
import requests

data = {
    "text": "Hello, how are you?",
    "context": "Casual greeting",
    "language": "en",
    "emotion": "friendly"
}
response = requests.post('http://localhost:8000/translate/text-to-body', 
                        json=data)
print(response.json())
```

#### Real-time WebSocket
```python
import websockets
import json

async def real_time_translation():
    uri = "ws://localhost:8000/ws/realtime-translation"
    async with websockets.connect(uri) as websocket:
        # Send video frame
        message = {
            "type": "video_frame",
            "frame": "base64_encoded_frame_data",
            "context": "conversation"
        }
        await websocket.send(json.dumps(message))
        
        # Receive translation
        response = await websocket.recv()
        print(json.loads(response))
```

## Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx pytest-cov

# Run tests
python test_backend.py

# Or use pytest directly
pytest test_backend.py -v --cov=services --cov=utils --cov=models
```

### Test Coverage

The test suite covers:
- AI Translator service
- Body Language Processor
- Audio Processor
- Database Manager
- WebSocket Manager
- Pydantic models
- Integration tests

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | Yes |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No |
| `DATABASE_URL` | SQLite database path | No |
| `CHROMA_DB_PATH` | ChromaDB storage path | No |

### Performance Tuning

#### MediaPipe Settings
```python
# In body_language_processor.py
self.pose = self.mp_pose.Pose(
    static_image_mode=False,
    model_complexity=2,  # 0, 1, or 2
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
```

#### AI Translation Settings
```python
# In ai_translator.py
self.model = "gpt-4-turbo-preview"  # Model selection
self.max_tokens = 2000              # Response length
self.temperature = 0.3              # Creativity level
```

## Database Schema

### SQLite Tables

#### translation_sessions
- `session_id` (TEXT PRIMARY KEY)
- `translation_type` (TEXT)
- `input_type` (TEXT)
- `output_type` (TEXT)
- `input_data` (TEXT JSON)
- `output_data` (TEXT JSON)
- `confidence` (REAL)
- `processing_time` (REAL)
- `timestamp` (DATETIME)
- `user_id` (TEXT)
- `context` (TEXT)

#### user_feedback
- `feedback_id` (TEXT PRIMARY KEY)
- `session_id` (TEXT)
- `rating` (INTEGER)
- `accuracy_rating` (INTEGER)
- `speed_rating` (INTEGER)
- `comments` (TEXT)
- `timestamp` (DATETIME)

### ChromaDB Collections

#### body_language_embeddings
- Stores vector embeddings for similarity search
- Metadata includes session_id, input_type, output_type, timestamp

## Error Handling

The system includes comprehensive error handling:

- **API Errors**: Proper HTTP status codes and error messages
- **AI Service Errors**: Graceful fallbacks and retry mechanisms
- **Database Errors**: Connection pooling and transaction management
- **WebSocket Errors**: Connection cleanup and reconnection logic

## Monitoring and Logging

### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General application flow
- `WARNING`: Potential issues
- `ERROR`: Error conditions

### Metrics
- Translation accuracy scores
- Processing times
- User feedback ratings
- System performance metrics

## Security Considerations

- **API Key Management**: Secure storage of OpenAI API keys
- **Input Validation**: Pydantic models for request validation
- **CORS Configuration**: Configurable cross-origin settings
- **Rate Limiting**: Built-in request rate limiting
- **Data Privacy**: User data encryption and anonymization

## Performance Optimization

### Caching
- Translation results caching
- Gesture pattern caching
- Database query optimization

### Async Processing
- Non-blocking I/O operations
- Background task processing
- WebSocket connection pooling

### Resource Management
- Memory-efficient video processing
- Database connection pooling
- Temporary file cleanup

## Deployment

### Docker Support
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- Use production-grade ASGI server (Gunicorn + Uvicorn)
- Implement proper logging and monitoring
- Set up database backups
- Configure load balancing
- Enable HTTPS/TLS

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the test examples

## Roadmap

- [ ] Multi-language support
- [ ] Advanced gesture recognition
- [ ] Mobile app integration
- [ ] Video conferencing plugins
- [ ] Machine learning model training
- [ ] Accessibility improvements

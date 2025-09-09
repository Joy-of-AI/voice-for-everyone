import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Alert,
  Paper,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Send as SendIcon,
  Translate as TranslateIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import Webcam from 'react-webcam';
import { motion } from 'framer-motion';

interface Message {
  id: string;
  type: 'translation' | 'system' | 'user';
  content: string;
  timestamp: Date;
  confidence?: number;
}

const RealTimeTranslation: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentTranslation, setCurrentTranslation] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [textInput, setTextInput] = useState('');
  const [isConnecting, setIsConnecting] = useState(true);
  const [connectionAttempts, setConnectionAttempts] = useState(0);

  const webcamRef = useRef<Webcam>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const errorTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    connectWebSocket(false);
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
      if (errorTimeoutRef.current) {
        clearTimeout(errorTimeoutRef.current);
      }
    };
  }, []);

  const connectWebSocket = (isManualRetry = false) => {
    setIsConnecting(true);
    setError(null);
    
    if (isManualRetry) {
      setConnectionAttempts(0);
    }
    
    try {
      const ws = new WebSocket('ws://localhost:8000/ws/realtime-translation');
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setIsConnecting(false);
        setConnectionAttempts(0);
        setError(null);
        addMessage('Connected to real-time translation service', 'system');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };

      ws.onclose = () => {
        setIsConnected(false);
        setIsConnecting(false);
        addMessage('Disconnected from translation service', 'system');
        
        // Only show error if we've tried multiple times and failed
        if (connectionAttempts >= 3) {
          setError('Unable to connect to translation service. Please check if the backend server is running.');
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnecting(false);
        
        // Don't show error immediately, give it time to retry
        if (connectionAttempts < 3) {
          setConnectionAttempts(prev => prev + 1);
          retryTimeoutRef.current = setTimeout(() => {
            connectWebSocket(false);
          }, 2000); // Retry after 2 seconds
        } else {
          // Only show error after multiple failed attempts
          errorTimeoutRef.current = setTimeout(() => {
            setError('WebSocket connection error. Please check if the backend server is running.');
          }, 1000);
        }
      };
    } catch (err) {
      setIsConnecting(false);
      setError('Failed to connect to translation service');
    }
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'translation':
        setCurrentTranslation(data.text);
        addMessage(data.text, 'translation', data.confidence);
        break;
      case 'gesture_detected':
        addMessage(`Gesture detected: ${data.gesture}`, 'system');
        break;
      case 'error':
        setError(data.message);
        break;
      default:
        console.log('Unknown message type:', data);
    }
  };

  const addMessage = (content: string, type: Message['type'], confidence?: number) => {
    const message: Message = {
      id: Date.now().toString(),
      type,
      content,
      timestamp: new Date(),
      confidence,
    };
    setMessages(prev => [...prev, message]);
  };

  const startRealTimeTranslation = () => {
    if (!isConnected) {
      setError('Not connected to translation service');
      return;
    }

    if (webcamRef.current) {
      const stream = webcamRef.current.video?.srcObject as MediaStream;
      if (stream) {
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(event.data);
          }
        };

        mediaRecorder.start(1000); // Send data every second
        setIsRecording(true);
        setError(null);
        addMessage('Started real-time translation', 'system');
      }
    }
  };

  const stopRealTimeTranslation = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      addMessage('Stopped real-time translation', 'system');
    }
  };

  const sendTextInput = (text: string) => {
    if (text.trim() && wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'text_input',
        text: text.trim(),
      }));
      addMessage(text.trim(), 'user');
      setTextInput('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      sendTextInput(textInput);
    }
  };

  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
        Real-Time Body Language Translation
      </Typography>

      {/* Connection Status */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 2 }}>
        <Chip
          label={
            isConnecting ? 'Connecting...' :
            isConnected ? 'Connected' : 'Disconnected'
          }
          color={
            isConnecting ? 'warning' :
            isConnected ? 'success' : 'error'
          }
          variant="outlined"
        />
        {!isConnected && !isConnecting && (
          <Button
            size="small"
            variant="outlined"
            onClick={() => connectWebSocket(true)}
            startIcon={<RefreshIcon />}
            disabled={isConnecting}
          >
            Reconnect
          </Button>
        )}
      </Box>

      {error && !isConnecting && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
        {/* Camera Feed */}
        <Box sx={{ flex: '1 1 500px', minWidth: 0 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Camera Feed
              </Typography>
              
              <Webcam
                ref={webcamRef}
                audio={false}
                width="100%"
                height="300"
                style={{ borderRadius: '8px', marginBottom: '16px' }}
              />

              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={startRealTimeTranslation}
                  disabled={!isConnected || isRecording || isConnecting}
                  startIcon={<PlayIcon />}
                >
                  Start Real-time Translation
                </Button>
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={stopRealTimeTranslation}
                  disabled={!isRecording}
                  startIcon={<StopIcon />}
                >
                  Stop Translation
                </Button>
              </Box>

              {currentTranslation && (
                <Paper sx={{ p: 2, backgroundColor: '#f8f9fa' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Current Translation:
                  </Typography>
                  <Typography variant="body1">
                    {currentTranslation}
                  </Typography>
                </Paper>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* Translation Messages */}
        <Box sx={{ flex: '1 1 500px', minWidth: 0 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Translation Messages
              </Typography>

              <Box sx={{ mb: 2 }}>
                <TextField
                  fullWidth
                  variant="outlined"
                  placeholder="Send text message"
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  InputProps={{
                    endAdornment: (
                      <Button
                        onClick={() => sendTextInput(textInput)}
                        disabled={!textInput.trim()}
                        startIcon={<SendIcon />}
                      >
                        Send
                      </Button>
                    ),
                  }}
                  sx={{ mb: 2 }}
                />
              </Box>

              <Box sx={{ height: 400, overflowY: 'auto' }}>
                <List>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <ListItem
                        sx={{
                          backgroundColor: message.type === 'translation' ? '#e3f2fd' : 
                                          message.type === 'user' ? '#f3e5f5' : '#f5f5f5',
                          borderRadius: 1,
                          mb: 1,
                        }}
                      >
                        <ListItemIcon>
                          {message.type === 'translation' && <TranslateIcon color="primary" />}
                          {message.type === 'user' && <SendIcon color="secondary" />}
                          {message.type === 'system' && <PlayIcon color="action" />}
                        </ListItemIcon>
                        <ListItemText
                          primary={message.content}
                          secondary={`${message.timestamp.toLocaleTimeString()}${
                            message.confidence ? ` • Confidence: ${(message.confidence * 100).toFixed(1)}%` : ''
                          }`}
                        />
                      </ListItem>
                    </motion.div>
                  ))}
                </List>
              </Box>

              {messages.length === 0 && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    Start real-time translation to see messages here
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
};

export default RealTimeTranslation;

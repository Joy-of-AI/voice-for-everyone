import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Paper,
  Chip,
  Alert,
} from '@mui/material';
import {
  Mic as MicIcon,
  Stop as StopIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';

interface SpeechToTextProps {
  onTextReceived: (text: string) => void;
  isListening: boolean;
  onListeningChange: (listening: boolean) => void;
}

declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

const SpeechToText: React.FC<SpeechToTextProps> = ({
  onTextReceived,
  isListening,
  onListeningChange
}) => {
  const [isSupported, setIsSupported] = useState(false);
  const [finalTranscript, setFinalTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<number>(0);
  
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Check if Speech Recognition is supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
      setIsSupported(true);
      const recognition = new SpeechRecognition();
      
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';
      recognition.maxAlternatives = 1;
      
      recognition.onstart = () => {
        onListeningChange(true);
        setError(null);
      };
      
      recognition.onresult = (event: any) => {
        let finalTranscript = '';
        let interimTranscript = '';
        let highestConfidence = 0;
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          const confidence = event.results[i][0].confidence;
          
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
            highestConfidence = Math.max(highestConfidence, confidence);
          } else {
            interimTranscript += transcript;
          }
        }
        
        setFinalTranscript(finalTranscript);
        setInterimTranscript(interimTranscript);
        setConfidence(highestConfidence);
        
        if (finalTranscript) {
          onTextReceived(finalTranscript);
        }
      };
      
      recognition.onerror = (event: any) => {
        setError(`Speech recognition error: ${event.error}`);
        onListeningChange(false);
      };
      
      recognition.onend = () => {
        onListeningChange(false);
      };
      
      recognitionRef.current = recognition;
    } else {
      setError('Speech recognition is not supported in this browser');
    }
  }, [onTextReceived, onListeningChange]);

  const startListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const clearTranscript = () => {
    setFinalTranscript('');
    setInterimTranscript('');
    setConfidence(0);
  };

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          🎤 Speech-to-Text
        </Typography>

        {!isSupported && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.
          </Alert>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={startListening}
            disabled={!isSupported || isListening}
            startIcon={<MicIcon />}
          >
            Start Listening
          </Button>
          <Button
            variant="contained"
            color="secondary"
            onClick={stopListening}
            disabled={!isSupported || !isListening}
            startIcon={<StopIcon />}
          >
            Stop Listening
          </Button>
          <Button
            variant="outlined"
            onClick={clearTranscript}
            startIcon={<ClearIcon />}
          >
            Clear
          </Button>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Chip 
            label={isListening ? 'Listening...' : 'Not Listening'} 
            color={isListening ? 'success' : 'default'}
            sx={{ mr: 1 }}
          />
          {confidence > 0 && (
            <Chip 
              label={`Confidence: ${(confidence * 100).toFixed(1)}%`} 
              color="primary"
              variant="outlined"
            />
          )}
        </Box>

        <Paper sx={{ p: 2, bgcolor: 'grey.50', minHeight: 100 }}>
          <Typography variant="subtitle2" gutterBottom>
            Final Transcript:
          </Typography>
          <Typography variant="body1" sx={{ mb: 2, minHeight: 20 }}>
            {finalTranscript || 'No speech detected yet...'}
          </Typography>
          
          {interimTranscript && (
            <>
              <Typography variant="subtitle2" gutterBottom>
                Interim Transcript:
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                {interimTranscript}
              </Typography>
            </>
          )}
        </Paper>
      </CardContent>
    </Card>
  );
};

export default SpeechToText;

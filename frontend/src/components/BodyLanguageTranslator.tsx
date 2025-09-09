import React, { useState, useCallback, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Chip,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  CameraAlt as CameraIcon,
  Stop as StopIcon,
  Upload as UploadIcon,
  Translate as TranslateIcon,
  PlayArrow as PlayIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import RealHumanVideo from './RealHumanVideo';
import SimpleHumanVideo from './SimpleHumanVideo';
import RealHumanBodyAnimation from './RealHumanBodyAnimation';
import SpeechToText from './SpeechToText';
import Webcam from 'react-webcam';
import { motion } from 'framer-motion';

interface TranslationResult {
  text: string;
  confidence: number;
  detected_gestures: string[];
}

interface BodyLanguageInstruction {
  gesture_type: string;
  description: string;
  duration: number;
  intensity: number;
  sequence_order: number;
}

const BodyLanguageTranslator: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [translationMode, setTranslationMode] = useState<'body-to-text' | 'text-to-body'>('body-to-text');
  const [inputText, setInputText] = useState('hello');  // Test phrase - should show waving animation
  const [translationResult, setTranslationResult] = useState<TranslationResult | null>(null);
  const [bodyInstructions, setBodyInstructions] = useState<BodyLanguageInstruction[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.7);
  const [language, setLanguage] = useState('en');
  const [emotion, setEmotion] = useState('neutral');
  const [context, setContext] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [useRealHumanAnimation, setUseRealHumanAnimation] = useState(true); // Use real human body animations

  const webcamRef = useRef<Webcam>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(() => {
    if (webcamRef.current) {
      const stream = webcamRef.current.video?.srcObject as MediaStream;
      if (stream) {
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        chunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            chunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = () => {
          const blob = new Blob(chunksRef.current, { type: 'video/webm' });
          processVideo(blob);
        };

        mediaRecorder.start();
        setIsRecording(true);
        setError(null);
      }
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const processVideo = useCallback(async (videoBlob: Blob) => {
    setIsProcessing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('video', videoBlob, 'recording.webm');
      formData.append('confidence_threshold', confidenceThreshold.toString());
      formData.append('language', language);
      formData.append('emotion', emotion);
      formData.append('context', context);

      const response = await fetch('http://localhost:8000/translate/body-to-text', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setTranslationResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during translation');
    } finally {
      setIsProcessing(false);
    }
  }, [confidenceThreshold, language, emotion, context]);

  const handleTextToBodyTranslation = async () => {
    if (!inputText.trim()) {
      setError('Please enter some text to translate');
      return;
    }

    setIsProcessing(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/translate/text-to-body', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          context: context,
          language: language,
          emotion: emotion,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setBodyInstructions(result.body_language_instructions || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during translation');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSpeechTextReceived = useCallback((text: string) => {
    setInputText(text);
    // Auto-translate when speech is received
    setTimeout(() => {
      if (text.trim()) {
        handleTextToBodyTranslation();
      }
    }, 1000);
  }, [handleTextToBodyTranslation]);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const blob = new Blob([file], { type: file.type });
      processVideo(blob);
    }
  };

  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
        Body Language Translator
      </Typography>

      {/* Mode Selection */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'center', gap: 2 }}>
        <Button
          variant={translationMode === 'body-to-text' ? 'contained' : 'outlined'}
          onClick={() => setTranslationMode('body-to-text')}
          startIcon={<CameraIcon />}
        >
          Body Language → Text
        </Button>
        <Button
          variant={translationMode === 'text-to-body' ? 'contained' : 'outlined'}
          onClick={() => setTranslationMode('text-to-body')}
          startIcon={<TranslateIcon />}
        >
          Text → Body Language
        </Button>
      </Box>

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
        {/* Input Section */}
        <Box sx={{ flex: '1 1 500px', minWidth: 0 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {translationMode === 'body-to-text' ? 'Camera Feed' : 'Text Input'}
              </Typography>

              {translationMode === 'body-to-text' ? (
                <Box>
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
                      onClick={startRecording}
                      disabled={isRecording}
                      startIcon={<CameraIcon />}
                    >
                      Start Recording
                    </Button>
                    <Button
                      variant="contained"
                      color="secondary"
                      onClick={stopRecording}
                      disabled={!isRecording}
                      startIcon={<StopIcon />}
                    >
                      Stop Recording
                    </Button>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <input
                      accept="video/*"
                      style={{ display: 'none' }}
                      id="video-upload"
                      type="file"
                      onChange={handleFileUpload}
                    />
                    <label htmlFor="video-upload">
                      <Button
                        variant="outlined"
                        component="span"
                        startIcon={<UploadIcon />}
                        fullWidth
                      >
                        Upload Video File
                      </Button>
                    </label>
                  </Box>

                  <Box sx={{ mb: 2 }}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={confidenceThreshold > 0.5}
                          onChange={(e) => setConfidenceThreshold(e.target.checked ? 0.8 : 0.3)}
                        />
                      }
                      label="High Confidence Mode"
                    />
                  </Box>
                </Box>
                             ) : (
                 <Box>
                   {/* Speech-to-Text Component */}
                   <SpeechToText
                     onTextReceived={handleSpeechTextReceived}
                     isListening={isListening}
                     onListeningChange={setIsListening}
                   />
                   
                   <Typography variant="h6" gutterBottom sx={{ mt: 3, mb: 2 }}>
                     Or Type Text:
                   </Typography>
                   
                   <TextField
                     fullWidth
                     multiline
                     rows={4}
                     variant="outlined"
                     label="Enter text to translate to body language"
                     value={inputText}
                     onChange={(e) => setInputText(e.target.value)}
                     sx={{ mb: 2 }}
                   />
                   
                   <TextField
                     fullWidth
                     variant="outlined"
                     label="Context (optional)"
                     value={context}
                     onChange={(e) => setContext(e.target.value)}
                     sx={{ mb: 2 }}
                   />

                                       <Button
                      variant="contained"
                      color="primary"
                      onClick={handleTextToBodyTranslation}
                      disabled={isProcessing || !inputText.trim()}
                      startIcon={<TranslateIcon />}
                      fullWidth
                      sx={{ mb: 2 }}
                    >
                      Translate to Body Language
                    </Button>

                    {/* Animation Type Toggle */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <Typography variant="body2">Animation Type:</Typography>
                      <Button
                        variant={useRealHumanAnimation ? 'contained' : 'outlined'}
                        size="small"
                        onClick={() => setUseRealHumanAnimation(true)}
                        sx={{ minWidth: 'auto' }}
                      >
                        Real Human
                      </Button>
                      <Button
                        variant={!useRealHumanAnimation ? 'contained' : 'outlined'}
                        size="small"
                        onClick={() => setUseRealHumanAnimation(false)}
                        sx={{ minWidth: 'auto' }}
                      >
                        Emoji
                      </Button>
                    </Box>
                 </Box>
               )}
            </CardContent>
          </Card>
        </Box>

        {/* Output Section */}
        <Box sx={{ flex: '1 1 500px', minWidth: 0 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {translationMode === 'body-to-text' ? 'Translation Results' : 'Body Language Instructions'}
              </Typography>

              {isProcessing && (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
                  <CircularProgress />
                  <Typography variant="body2" sx={{ ml: 2 }}>
                    Processing...
                  </Typography>
                </Box>
              )}

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              {translationMode === 'body-to-text' && translationResult && (
                <Box>
                  <Paper sx={{ p: 2, mb: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      Translated Text
                    </Typography>
                    <Typography variant="body1">
                      {translationResult.text}
                    </Typography>
                  </Paper>

                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Confidence: {(translationResult.confidence * 100).toFixed(1)}%
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {translationResult.detected_gestures.map((gesture, index) => (
                        <Chip key={index} label={gesture} size="small" />
                      ))}
                    </Box>
                  </Box>
                </Box>
              )}

                             {translationMode === 'text-to-body' && bodyInstructions.length > 0 && (
                 <Box>
                   {useRealHumanAnimation ? (
                     <RealHumanBodyAnimation 
                       instructions={bodyInstructions}
                       onComplete={() => {
                         console.log('Real human body language animation completed');
                       }}
                     />
                   ) : (
                     <SimpleHumanVideo 
                       instructions={bodyInstructions}
                       onComplete={() => {
                         console.log('Simple emoji animation completed');
                       }}
                     />
                   )}
                   {/* Debug info */}
                   <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                     <Typography variant="caption">
                       Debug: Using {useRealHumanAnimation ? 'Real Human Animation' : 'Emoji Animation'}. Instructions: {bodyInstructions.length}
                     </Typography>
                   </Box>
                 </Box>
               )}

              {!isProcessing && !translationResult && !bodyInstructions.length && !error && (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    {translationMode === 'body-to-text' 
                      ? 'Start recording or upload a video to see translation results'
                      : 'Enter text and click translate to see body language instructions'
                    }
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

export default BodyLanguageTranslator;

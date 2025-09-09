import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Paper,
  Chip,
  Button,
  LinearProgress,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Replay as ReplayIcon,
  VolumeUp as VolumeIcon,
  VolumeOff as MuteIcon,
} from '@mui/icons-material';

interface BodyLanguageInstruction {
  gesture_type: string;
  description: string;
  duration: number;
  intensity: number;
  sequence_order: number;
}

interface BodyLanguageVideoProps {
  instructions: BodyLanguageInstruction[];
  onComplete?: () => void;
}

// Gesture animation mappings
const gestureAnimations: Record<string, {
  icon: string;
  color: string;
  animation: string;
  meaning: string;
}> = {
  // Hand gestures
  "Point to your chest with index finger, then point forward": {
    icon: "👆",
    color: "#2196f3",
    animation: "pointing",
    meaning: "I want to go there"
  },
  "Hold both hands palms up, then bring them toward your chest": {
    icon: "🤲",
    color: "#ff9800",
    animation: "palms-up",
    meaning: "I need help"
  },
  "Point forward with index finger, then make walking motion with fingers": {
    icon: "🚶",
    color: "#4caf50",
    animation: "walking",
    meaning: "Let's go"
  },
  "Wave hand from side to side": {
    icon: "👋",
    color: "#9c27b0",
    animation: "waving",
    meaning: "Hello/Goodbye"
  },
  "Make writing motion with hand, then point to building location": {
    icon: "✍️",
    color: "#607d8b",
    animation: "writing",
    meaning: "School/Study"
  },
  "Place hand over heart, then nod head": {
    icon: "❤️",
    color: "#e91e63",
    animation: "heart",
    meaning: "Thank you"
  },
  "Raise hand above head, then point to yourself": {
    icon: "🆘",
    color: "#f44336",
    animation: "help",
    meaning: "I need help"
  },
  "Nod head up and down": {
    icon: "👍",
    color: "#4caf50",
    animation: "nodding",
    meaning: "Yes"
  },
  "Shake head side to side": {
    icon: "👎",
    color: "#f44336",
    animation: "shaking",
    meaning: "No"
  },
  "Smile broadly, then point to your smile": {
    icon: "😊",
    color: "#ff9800",
    animation: "smiling",
    meaning: "I'm happy"
  },
  "Frown, then point to your face": {
    icon: "😔",
    color: "#607d8b",
    animation: "frowning",
    meaning: "I'm sad"
  },
  "Slump shoulders, then yawn motion": {
    icon: "😴",
    color: "#795548",
    animation: "tired",
    meaning: "I'm tired"
  }
};

const BodyLanguageVideo: React.FC<BodyLanguageVideoProps> = ({
  instructions,
  onComplete
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showMeaning, setShowMeaning] = useState(false);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const progressRef = useRef<NodeJS.Timeout | null>(null);

  const currentInstruction = instructions[currentStep];
  const animation = gestureAnimations[currentInstruction?.description] || {
    icon: "🤔",
    color: "#666",
    animation: "default",
    meaning: "I understand"
  };

  useEffect(() => {
    if (isPlaying && currentStep < instructions.length) {
      // Start progress bar
      const duration = currentInstruction.duration * 1000; // Convert to milliseconds
      const startTime = Date.now();
      
      progressRef.current = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const newProgress = Math.min((elapsed / duration) * 100, 100);
        setProgress(newProgress);
        
        if (newProgress >= 100) {
          // Move to next step
          if (currentStep < instructions.length - 1) {
            setCurrentStep(currentStep + 1);
            setProgress(0);
            setShowMeaning(false);
          } else {
            // Animation complete
            setIsPlaying(false);
            onComplete?.();
          }
        }
      }, 50); // Update every 50ms for smooth progress
    }

    return () => {
      if (progressRef.current) {
        clearInterval(progressRef.current);
      }
    };
  }, [currentStep, isPlaying, currentInstruction, instructions.length, onComplete]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleReplay = () => {
    setCurrentStep(0);
    setProgress(0);
    setIsPlaying(true);
    setShowMeaning(false);
  };

  const handleToggleMute = () => {
    setIsMuted(!isMuted);
  };

  const getAnimationStyle = (animationType: string) => {
    const baseStyle = {
      width: 120,
      height: 120,
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: 48,
      margin: '0 auto',
      transition: 'all 0.3s ease',
      boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
    };

    switch (animationType) {
      case "pointing":
        return {
          ...baseStyle,
          backgroundColor: animation.color,
          animation: isPlaying ? 'pointing 2s infinite' : 'none',
        };
      case "waving":
        return {
          ...baseStyle,
          backgroundColor: animation.color,
          animation: isPlaying ? 'waving 1s infinite' : 'none',
        };
      case "nodding":
        return {
          ...baseStyle,
          backgroundColor: animation.color,
          animation: isPlaying ? 'nodding 1s infinite' : 'none',
        };
      case "shaking":
        return {
          ...baseStyle,
          backgroundColor: animation.color,
          animation: isPlaying ? 'shaking 1s infinite' : 'none',
        };
      case "walking":
        return {
          ...baseStyle,
          backgroundColor: animation.color,
          animation: isPlaying ? 'walking 2s infinite' : 'none',
        };
      case "heart":
        return {
          ...baseStyle,
          backgroundColor: animation.color,
          animation: isPlaying ? 'heart 2s infinite' : 'none',
        };
      case "help":
        return {
          ...baseStyle,
          backgroundColor: animation.color,
          animation: isPlaying ? 'help 2s infinite' : 'none',
        };
      default:
        return {
          ...baseStyle,
          backgroundColor: animation.color,
        };
    }
  };

  return (
    <Card sx={{ maxWidth: 600, mx: 'auto', mt: 2 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom align="center" sx={{ mb: 3 }}>
          🎬 Body Language Translation
        </Typography>

        {/* Video Display Area */}
        <Box sx={{ 
          bgcolor: 'black', 
          borderRadius: 2, 
          p: 3, 
          mb: 3,
          minHeight: 300,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative'
        }}>
          {/* Main Animation */}
          <Box sx={getAnimationStyle(animation.animation)}>
            {animation.icon}
          </Box>

          {/* Meaning Overlay */}
          {showMeaning && (
            <Box sx={{
              position: 'absolute',
              bottom: 20,
              left: '50%',
              transform: 'translateX(-50%)',
              bgcolor: 'rgba(0,0,0,0.8)',
              color: 'white',
              px: 3,
              py: 1,
              borderRadius: 2,
              fontSize: '1.2rem',
              fontWeight: 'bold'
            }}>
              {animation.meaning}
            </Box>
          )}

          {/* Step Counter */}
          <Box sx={{
            position: 'absolute',
            top: 20,
            right: 20,
            bgcolor: 'rgba(0,0,0,0.7)',
            color: 'white',
            px: 2,
            py: 1,
            borderRadius: 1,
            fontSize: '0.9rem'
          }}>
            {currentStep + 1} / {instructions.length}
          </Box>
        </Box>

        {/* Progress Bar */}
        <Box sx={{ mb: 3 }}>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            sx={{ 
              height: 8, 
              borderRadius: 4,
              bgcolor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                borderRadius: 4,
                bgcolor: animation.color
              }
            }} 
          />
          <Typography variant="caption" sx={{ mt: 1, display: 'block', textAlign: 'center' }}>
            {Math.round(progress)}% complete
          </Typography>
        </Box>

        {/* Controls */}
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mb: 2 }}>
          <IconButton onClick={handlePlayPause} sx={{ color: animation.color }}>
            {isPlaying ? <PauseIcon /> : <PlayIcon />}
          </IconButton>
          <IconButton onClick={handleReplay} sx={{ color: animation.color }}>
            <ReplayIcon />
          </IconButton>
          <IconButton onClick={handleToggleMute} sx={{ color: animation.color }}>
            {isMuted ? <MuteIcon /> : <VolumeIcon />}
          </IconButton>
        </Box>

        {/* Current Gesture Info */}
        <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
          <Typography variant="h6" gutterBottom>
            Current Gesture: {currentInstruction?.gesture_type}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {currentInstruction?.description}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
            <Chip label={`Duration: ${currentInstruction?.duration}s`} size="small" />
            <Chip label={`Intensity: ${currentInstruction?.intensity}`} size="small" />
          </Box>
        </Paper>

        {/* Show Meaning Button */}
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Button
            variant="outlined"
            onClick={() => setShowMeaning(!showMeaning)}
            sx={{ color: animation.color, borderColor: animation.color }}
          >
            {showMeaning ? 'Hide Meaning' : 'Show Meaning'}
          </Button>
        </Box>

        <style>
          {`
            @keyframes pointing {
              0%, 100% { transform: translateX(0) scale(1); }
              50% { transform: translateX(20px) scale(1.1); }
            }
            @keyframes waving {
              0%, 100% { transform: rotate(0deg) scale(1); }
              50% { transform: rotate(20deg) scale(1.1); }
            }
            @keyframes nodding {
              0%, 100% { transform: translateY(0) scale(1); }
              50% { transform: translateY(-10px) scale(1.1); }
            }
            @keyframes shaking {
              0%, 100% { transform: rotate(0deg) scale(1); }
              25% { transform: rotate(-15deg) scale(1.1); }
              75% { transform: rotate(15deg) scale(1.1); }
            }
            @keyframes walking {
              0%, 100% { transform: translateX(0) scale(1); }
              50% { transform: translateX(15px) scale(1.1); }
            }
            @keyframes heart {
              0%, 100% { transform: scale(1); }
              50% { transform: scale(1.2); }
            }
            @keyframes help {
              0%, 100% { transform: translateY(0) scale(1); }
              50% { transform: translateY(-15px) scale(1.1); }
            }
          `}
        </style>
      </CardContent>
    </Card>
  );
};

export default BodyLanguageVideo;

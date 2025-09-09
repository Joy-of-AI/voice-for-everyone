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

interface SimpleHumanVideoProps {
  instructions: BodyLanguageInstruction[];
  onComplete?: () => void;
}

  // Simple gesture to CSS animation mappings
  const gestureAnimations: Record<string, {
    animation: string;
    meaning: string;
    color: string;
    emoji: string;
  }> = {
    "Point to your chest with index finger, then point forward": {
      animation: "pointing",
      meaning: "I want to go there",
      color: "#2196f3",
      emoji: "👆"
    },
    "Hold both hands palms up, then bring them toward your chest": {
      animation: "palms_up",
      meaning: "I need help",
      color: "#ff9800",
      emoji: "🤲"
    },
    "Wave hand from side to side": {
      animation: "waving",
      meaning: "Hello/Goodbye",
      color: "#9c27b0",
      emoji: "👋"
    },
    "Make writing motion with hand, then point to building location": {
      animation: "writing",
      meaning: "School/Study",
      color: "#607d8b",
      emoji: "✍️"
    },
    "Place hand over heart, then nod head": {
      animation: "heart",
      meaning: "Thank you",
      color: "#e91e63",
      emoji: "💝"
    },
    "Raise hand above head, then point to yourself": {
      animation: "help",
      meaning: "I need help",
      color: "#f44336",
      emoji: "🙋"
    },
    "Nod head up and down": {
      animation: "nodding",
      meaning: "Yes",
      color: "#4caf50",
      emoji: "👍"
    },
    "Shake head side to side": {
      animation: "shaking",
      meaning: "No",
      color: "#f44336",
      emoji: "👎"
    },
    // Add more mappings for common phrases
    "Point to your chest, then point forward in the direction you want to go": {
      animation: "pointing",
      meaning: "I want to go there",
      color: "#2196f3",
      emoji: "👆"
    },
    "Hold both hands palms up toward the person": {
      animation: "palms_up",
      meaning: "I need help",
      color: "#ff9800",
      emoji: "🤲"
    },
    "Point to your chest, then gesture to explain what you want": {
      animation: "pointing",
      meaning: "I want this",
      color: "#2196f3",
      emoji: "👆"
    },
    "Show determined expression": {
      animation: "determined",
      meaning: "I am determined",
      color: "#4caf50",
      emoji: "💪"
    },
    "Show concerned or urgent expression": {
      animation: "urgent",
      meaning: "I need help urgently",
      color: "#f44336",
      emoji: "😰"
    },
    "Show your emotion about the situation": {
      animation: "heart",
      meaning: "I feel this way",
      color: "#e91e63",
      emoji: "💝"
    }
  };

const SimpleHumanVideo: React.FC<SimpleHumanVideoProps> = ({
  instructions,
  onComplete
}) => {
  // Add global CSS keyframes
  useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes pointing {
        0% { transform: translateX(-50px) scale(1); }
        25% { transform: translateX(0px) scale(1.2); }
        50% { transform: translateX(50px) scale(1); }
        75% { transform: translateX(0px) scale(1.1); }
        100% { transform: translateX(-50px) scale(1); }
      }
      @keyframes waving {
        0% { transform: rotate(-20deg); }
        25% { transform: rotate(20deg); }
        50% { transform: rotate(-20deg); }
        75% { transform: rotate(20deg); }
        100% { transform: rotate(-20deg); }
      }
      @keyframes nodding {
        0% { transform: rotateX(0deg); }
        25% { transform: rotateX(20deg); }
        50% { transform: rotateX(0deg); }
        75% { transform: rotateX(-20deg); }
        100% { transform: rotateX(0deg); }
      }
      @keyframes shaking {
        0% { transform: rotateY(0deg); }
        25% { transform: rotateY(20deg); }
        50% { transform: rotateY(0deg); }
        75% { transform: rotateY(-20deg); }
        100% { transform: rotateY(0deg); }
      }
      @keyframes palms_up {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(10deg); }
        100% { transform: translateY(0px) rotate(0deg); }
      }
      @keyframes heart {
        0% { transform: scale(1); }
        50% { transform: scale(1.3); }
        100% { transform: scale(1); }
      }
      @keyframes help {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-30px); }
        100% { transform: translateY(0px); }
      }
      @keyframes writing {
        0% { transform: rotate(0deg); }
        25% { transform: rotate(10deg); }
        50% { transform: rotate(-10deg); }
        75% { transform: rotate(10deg); }
        100% { transform: rotate(0deg); }
      }
             @keyframes default {
         0% { transform: scale(1); }
         50% { transform: scale(1.1); }
         100% { transform: scale(1); }
       }
       @keyframes determined {
         0% { transform: scale(1) rotate(0deg); }
         25% { transform: scale(1.1) rotate(5deg); }
         50% { transform: scale(1.2) rotate(0deg); }
         75% { transform: scale(1.1) rotate(-5deg); }
         100% { transform: scale(1) rotate(0deg); }
       }
       @keyframes urgent {
         0% { transform: scale(1); }
         25% { transform: scale(1.2); }
         50% { transform: scale(1.1); }
         75% { transform: scale(1.3); }
         100% { transform: scale(1); }
       }
    `;
    document.head.appendChild(style);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showMeaning, setShowMeaning] = useState(false);
  const progressRef = useRef<NodeJS.Timeout | null>(null);

  const currentInstruction = instructions[currentStep];
  
  // Find the best matching animation by checking if any part of the description matches
  const findBestAnimation = (description: string) => {
    const desc = description.toLowerCase();
    
    // Check for exact matches first
    if (gestureAnimations[description]) {
      return gestureAnimations[description];
    }
    
    // Check for partial matches
    for (const [key, value] of Object.entries(gestureAnimations)) {
      const keyLower = key.toLowerCase();
      
      // Check if key words match
      if (desc.includes('point') && keyLower.includes('point')) {
        return value;
      }
      if (desc.includes('wave') && keyLower.includes('wave')) {
        return value;
      }
      if (desc.includes('nod') && keyLower.includes('nod')) {
        return value;
      }
      if (desc.includes('shake') && keyLower.includes('shake')) {
        return value;
      }
      if (desc.includes('heart') && keyLower.includes('heart')) {
        return value;
      }
      if (desc.includes('help') && keyLower.includes('help')) {
        return value;
      }
      if (desc.includes('palms') && keyLower.includes('palms')) {
        return value;
      }
      if (desc.includes('emotion') || desc.includes('expression')) {
        return value; // Use heart animation for emotions
      }
      if (desc.includes('gesture') && keyLower.includes('point')) {
        return value; // Use pointing for general gestures
      }
    }
    
    return {
      animation: "default",
      meaning: "I understand",
      color: "#666",
      emoji: "🤔"
    };
  };
  
  const animation = findBestAnimation(currentInstruction?.description || '');

  // Debug logging
  console.log('SimpleHumanVideo render:', {
    currentStep,
    instructionsLength: instructions.length,
    currentInstruction,
    animation,
    isPlaying,
    description: currentInstruction?.description,
    matchedAnimation: animation.animation,
    emoji: animation.emoji,
    animationName: animation.animation
  });

  // Progress and timing logic
  useEffect(() => {
    if (isPlaying && currentStep < instructions.length) {
      const duration = currentInstruction.duration * 1000;
      const startTime = Date.now();
      
      progressRef.current = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const newProgress = Math.min((elapsed / duration) * 100, 100);
        setProgress(newProgress);
        
        if (newProgress >= 100) {
          if (currentStep < instructions.length - 1) {
            setCurrentStep(currentStep + 1);
            setProgress(0);
            setShowMeaning(false);
          } else {
            setIsPlaying(false);
            onComplete?.();
          }
        }
      }, 50);
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

  return (
    <Card sx={{ maxWidth: 800, mx: 'auto', mt: 2 }}>
      <CardContent>
        <Typography variant="h5" gutterBottom align="center" sx={{ mb: 3 }}>
          🎬 Simple Human Body Language Translation
        </Typography>

        {/* Simple Video Display Area */}
        <Box sx={{ 
          bgcolor: 'black', 
          borderRadius: 2, 
          mb: 3,
          height: 400,
          position: 'relative',
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
                     {/* Animated Emoji */}
           <Box
             sx={{
               fontSize: '8rem',
               animation: isPlaying ? `${animation.animation} ${currentInstruction?.duration}s infinite` : 'none',
               display: 'flex',
               alignItems: 'center',
               justifyContent: 'center',
               width: '100%',
               height: '100%',
               color: 'white',
               textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
             }}
           >
             {animation.emoji}
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
            <Chip label="Simple Animation" size="small" color="primary" />
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
      </CardContent>
    </Card>
  );
};

export default SimpleHumanVideo;

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Collapse,
  Paper,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Info as InfoIcon,
  Gesture as GestureIcon,
  Face as FaceIcon,
  Accessibility as BodyIcon,
} from '@mui/icons-material';

interface GestureInstruction {
  gesture_type: string;
  description: string;
  duration: number;
  intensity: number;
  sequence_order: number;
}

interface GestureVisualGuideProps {
  instruction: GestureInstruction;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

// Gesture visual mappings
const gestureVisuals: Record<string, {
  icon: React.ReactElement;
  color: string;
  animation: string;
  tips: string[];
}> = {
  // Hand gestures
  "Point to your chest with index finger, then point forward": {
    icon: <GestureIcon />,
    color: "#2196f3",
    animation: "pointing",
    tips: ["Keep your finger straight", "Make clear pointing motion", "Hold position for 2 seconds"]
  },
  "Hold both hands palms up, then bring them toward your chest": {
    icon: <GestureIcon />,
    color: "#ff9800",
    animation: "palms-up",
    tips: ["Keep palms facing up", "Move hands slowly", "Show sincerity in expression"]
  },
  "Point forward with index finger, then make walking motion with fingers": {
    icon: <GestureIcon />,
    color: "#4caf50",
    animation: "walking",
    tips: ["Point clearly in direction", "Make walking motion with fingers", "Show determination"]
  },
  "Wave hand from side to side": {
    icon: <GestureIcon />,
    color: "#9c27b0",
    animation: "waving",
    tips: ["Keep wrist relaxed", "Wave from side to side", "Make eye contact"]
  },
  "Make writing motion with hand, then point to building location": {
    icon: <GestureIcon />,
    color: "#607d8b",
    animation: "writing",
    tips: ["Pretend to hold a pen", "Make writing motion", "Point to school direction"]
  },
  "Place hand over heart, then nod head": {
    icon: <GestureIcon />,
    color: "#e91e63",
    animation: "heart",
    tips: ["Place hand gently on chest", "Nod slowly", "Show genuine gratitude"]
  },
  "Raise hand above head, then point to yourself": {
    icon: <GestureIcon />,
    color: "#f44336",
    animation: "help",
    tips: ["Raise hand high", "Point to your chest", "Show urgency if needed"]
  },
  "Nod head up and down": {
    icon: <FaceIcon />,
    color: "#4caf50",
    animation: "nodding",
    tips: ["Nod slowly and clearly", "Make eye contact", "Show agreement"]
  },
  "Shake head side to side": {
    icon: <FaceIcon />,
    color: "#f44336",
    animation: "shaking",
    tips: ["Shake head clearly", "Make eye contact", "Show disagreement"]
  },
  "Smile broadly, then point to your smile": {
    icon: <FaceIcon />,
    color: "#ff9800",
    animation: "smiling",
    tips: ["Smile genuinely", "Point to your mouth", "Show happiness"]
  },
  "Frown, then point to your face": {
    icon: <FaceIcon />,
    color: "#607d8b",
    animation: "frowning",
    tips: ["Show sad expression", "Point to your face", "Express emotion clearly"]
  },
  "Slump shoulders, then yawn motion": {
    icon: <BodyIcon />,
    color: "#795548",
    animation: "tired",
    tips: ["Relax your shoulders", "Make yawning motion", "Show tiredness"]
  }
};

const GestureVisualGuide: React.FC<GestureVisualGuideProps> = ({
  instruction,
  isExpanded = false,
  onToggleExpand
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [showVideo, setShowVideo] = useState(false);

  const visual = gestureVisuals[instruction.description] || {
    icon: <GestureIcon />,
    color: "#666",
    animation: "default",
    tips: ["Follow the description carefully", "Practice the motion", "Show confidence"]
  };

  const getAnimationStyle = (animation: string) => {
    const baseStyle = {
      width: 60,
      height: 60,
      borderRadius: '50%',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'white',
      fontSize: 24,
      margin: '0 auto',
      transition: 'all 0.3s ease',
    };

    switch (animation) {
      case "pointing":
        return {
          ...baseStyle,
          backgroundColor: visual.color,
          animation: isPlaying ? 'pointing 2s infinite' : 'none',
        };
      case "waving":
        return {
          ...baseStyle,
          backgroundColor: visual.color,
          animation: isPlaying ? 'waving 1s infinite' : 'none',
        };
      case "nodding":
        return {
          ...baseStyle,
          backgroundColor: visual.color,
          animation: isPlaying ? 'nodding 1s infinite' : 'none',
        };
      case "shaking":
        return {
          ...baseStyle,
          backgroundColor: visual.color,
          animation: isPlaying ? 'shaking 1s infinite' : 'none',
        };
      default:
        return {
          ...baseStyle,
          backgroundColor: visual.color,
        };
    }
  };

  return (
    <>
      <Paper sx={{ p: 2, mb: 2, border: `2px solid ${visual.color}20` }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="h6" sx={{ color: visual.color }}>
            Step {instruction.sequence_order}: {instruction.gesture_type}
          </Typography>
          <Box>
            <IconButton
              size="small"
              onClick={() => setIsPlaying(!isPlaying)}
              sx={{ color: visual.color }}
            >
              {isPlaying ? <PauseIcon /> : <PlayIcon />}
            </IconButton>
            <IconButton
              size="small"
              onClick={onToggleExpand}
              sx={{ color: visual.color }}
            >
              {isExpanded ? <CollapseIcon /> : <ExpandIcon />}
            </IconButton>
          </Box>
        </Box>

        <Typography variant="body2" gutterBottom>
          {instruction.description}
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <Chip label={`Duration: ${instruction.duration}s`} size="small" />
          <Chip label={`Intensity: ${instruction.intensity}`} size="small" />
        </Box>

        {/* Visual Demonstration */}
        <Box sx={{ textAlign: 'center', mb: 2 }}>
          <Box sx={getAnimationStyle(visual.animation)}>
            {visual.icon}
          </Box>
          <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
            {isPlaying ? 'Demonstrating...' : 'Click play to see animation'}
          </Typography>
        </Box>

        <Collapse in={isExpanded}>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              <InfoIcon sx={{ mr: 1, fontSize: 16 }} />
              Tips for this gesture:
            </Typography>
                         <Box sx={{ pl: 2 }}>
               {visual.tips.map((tip: string, index: number) => (
                 <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
                   • {tip}
                 </Typography>
               ))}
             </Box>
            
            <Button
              variant="outlined"
              size="small"
              onClick={() => setShowVideo(true)}
              sx={{ mt: 2 }}
            >
              Watch Video Example
            </Button>
          </Box>
        </Collapse>
      </Paper>

      {/* Video Dialog */}
      <Dialog open={showVideo} onClose={() => setShowVideo(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          Video Demonstration: {instruction.gesture_type}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Video demonstration would be shown here
            </Typography>
            <Box sx={{ 
              width: '100%', 
              height: 300, 
              bgcolor: 'grey.100', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              borderRadius: 1,
              mt: 2
            }}>
              <Typography variant="h6" color="text.secondary">
                🎥 Video Placeholder
              </Typography>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowVideo(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      <style>
        {`
          @keyframes pointing {
            0%, 100% { transform: translateX(0); }
            50% { transform: translateX(10px); }
          }
          @keyframes waving {
            0%, 100% { transform: rotate(0deg); }
            50% { transform: rotate(20deg); }
          }
          @keyframes nodding {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
          }
          @keyframes shaking {
            0%, 100% { transform: rotate(0deg); }
            25% { transform: rotate(-10deg); }
            75% { transform: rotate(10deg); }
          }
        `}
      </style>
    </>
  );
};

export default GestureVisualGuide;

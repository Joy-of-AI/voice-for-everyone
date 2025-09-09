import React, { useState, useEffect, useRef, useMemo } from 'react';
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
import * as THREE from 'three';

interface BodyLanguageInstruction {
  gesture_type: string;
  description: string;
  duration: number;
  intensity: number;
  sequence_order: number;
}

interface RealHumanVideoProps {
  instructions: BodyLanguageInstruction[];
  onComplete?: () => void;
  onError?: () => void;
}

// Gesture to 3D animation mappings
const gestureAnimations: Record<string, {
  animation: string;
  meaning: string;
  color: string;
  keyframes: { time: number; action: string; }[];
}> = {
  "Point to your chest with index finger, then point forward": {
    animation: "pointing",
    meaning: "I want to go there",
    color: "#2196f3",
    keyframes: [
      { time: 0, action: "point_to_chest" },
      { time: 1, action: "point_forward" },
      { time: 2, action: "hold_position" }
    ]
  },
  "Hold both hands palms up, then bring them toward your chest": {
    animation: "palms_up",
    meaning: "I need help",
    color: "#ff9800",
    keyframes: [
      { time: 0, action: "palms_up" },
      { time: 1, action: "bring_to_chest" },
      { time: 2.5, action: "hold_position" }
    ]
  },
  "Wave hand from side to side": {
    animation: "waving",
    meaning: "Hello/Goodbye",
    color: "#9c27b0",
    keyframes: [
      { time: 0, action: "start_wave" },
      { time: 0.5, action: "wave_left" },
      { time: 1, action: "wave_right" },
      { time: 1.5, action: "wave_left" },
      { time: 2, action: "end_wave" }
    ]
  },
  "Make writing motion with hand, then point to building location": {
    animation: "writing",
    meaning: "School/Study",
    color: "#607d8b",
    keyframes: [
      { time: 0, action: "hold_pen" },
      { time: 1, action: "writing_motion" },
      { time: 2, action: "point_to_building" },
      { time: 3, action: "hold_position" }
    ]
  },
  "Place hand over heart, then nod head": {
    animation: "heart",
    meaning: "Thank you",
    color: "#e91e63",
    keyframes: [
      { time: 0, action: "hand_to_heart" },
      { time: 1, action: "nod_head" },
      { time: 2, action: "hold_position" }
    ]
  },
  "Raise hand above head, then point to yourself": {
    animation: "help",
    meaning: "I need help",
    color: "#f44336",
    keyframes: [
      { time: 0, action: "raise_hand" },
      { time: 1, action: "point_to_self" },
      { time: 3, action: "hold_position" }
    ]
  },
  "Nod head up and down": {
    animation: "nodding",
    meaning: "Yes",
    color: "#4caf50",
    keyframes: [
      { time: 0, action: "nod_down" },
      { time: 0.5, action: "nod_up" },
      { time: 1, action: "nod_down" },
      { time: 1.5, action: "nod_up" }
    ]
  },
  "Shake head side to side": {
    animation: "shaking",
    meaning: "No",
    color: "#f44336",
    keyframes: [
      { time: 0, action: "shake_left" },
      { time: 0.5, action: "shake_right" },
      { time: 1, action: "shake_left" },
      { time: 1.5, action: "shake_right" }
    ]
  }
};

const RealHumanVideo: React.FC<RealHumanVideoProps> = ({
  instructions,
  onComplete,
  onError
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showMeaning, setShowMeaning] = useState(false);
  const [is3DReady, setIs3DReady] = useState(false);
  
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const humanModelRef = useRef<THREE.Group | null>(null);
  const progressRef = useRef<NodeJS.Timeout | null>(null);

  const currentInstruction = instructions[currentStep];
  const animation = useMemo(() => 
    gestureAnimations[currentInstruction?.description] || {
      animation: "default",
      meaning: "I understand",
      color: "#666",
      keyframes: [{ time: 0, action: "idle" }]
    }, [currentInstruction?.description]
  );

  // Initialize 3D scene
  useEffect(() => {
    if (!mountRef.current) {
      onError?.();
      return;
    }

    try {
      // Create scene
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x000000);
      sceneRef.current = scene;

      // Create camera
      const camera = new THREE.PerspectiveCamera(
        75,
        mountRef.current.clientWidth / mountRef.current.clientHeight,
        0.1,
        1000
      );
      camera.position.set(0, 1, 5);
      camera.lookAt(0, 1, 0);
      cameraRef.current = camera;

      // Create renderer
      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      rendererRef.current = renderer;

      mountRef.current.appendChild(renderer.domElement);

      // Add lighting
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
      scene.add(ambientLight);

      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
      directionalLight.position.set(10, 10, 5);
      directionalLight.castShadow = true;
      scene.add(directionalLight);

      // Create simple human model (placeholder)
      createHumanModel(scene);

      // Animation loop
      const animate = () => {
        requestAnimationFrame(animate);
        if (renderer && scene && camera) {
          renderer.render(scene, camera);
        }
      };
      animate();

      // Add some debugging
      console.log('3D Scene initialized:', {
        scene: scene.children.length,
        camera: camera.position,
        renderer: renderer.domElement
      });

      setIs3DReady(true);

      return () => {
        const currentMount = mountRef.current;
        const currentRenderer = renderer;
        if (currentMount && currentRenderer) {
          currentMount.removeChild(currentRenderer.domElement);
        }
        currentRenderer?.dispose();
      };
    } catch (error) {
      console.error('Three.js initialization failed:', error);
      onError?.();
    }
  }, [onError]);

  const createHumanModel = (scene: THREE.Scene) => {
    const humanGroup = new THREE.Group();
    
    // Create head
    const headGeometry = new THREE.SphereGeometry(0.3, 32, 32);
    const headMaterial = new THREE.MeshLambertMaterial({ color: 0xffdbac });
    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.position.y = 1.5;
    head.name = 'head';
    humanGroup.add(head);

    // Create body
    const bodyGeometry = new THREE.CylinderGeometry(0.4, 0.6, 1.2, 32);
    const bodyMaterial = new THREE.MeshLambertMaterial({ color: 0x2196f3 });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.position.y = 0.6;
    body.name = 'body';
    humanGroup.add(body);

    // Create arms
    const armGeometry = new THREE.CylinderGeometry(0.1, 0.1, 0.8, 16);
    const armMaterial = new THREE.MeshLambertMaterial({ color: 0xffdbac });
    
    const leftArm = new THREE.Mesh(armGeometry, armMaterial);
    leftArm.position.set(-0.6, 0.8, 0);
    leftArm.rotation.z = Math.PI / 4;
    leftArm.name = 'leftArm';
    humanGroup.add(leftArm);

    const rightArm = new THREE.Mesh(armGeometry, armMaterial);
    rightArm.position.set(0.6, 0.8, 0);
    rightArm.rotation.z = -Math.PI / 4;
    rightArm.name = 'rightArm';
    humanGroup.add(rightArm);

    // Create hands
    const handGeometry = new THREE.SphereGeometry(0.15, 16, 16);
    const handMaterial = new THREE.MeshLambertMaterial({ color: 0xffdbac });
    
    const leftHand = new THREE.Mesh(handGeometry, handMaterial);
    leftHand.position.set(-0.8, 0.4, 0);
    leftHand.name = 'leftHand';
    humanGroup.add(leftHand);

    const rightHand = new THREE.Mesh(handGeometry, handMaterial);
    rightHand.position.set(0.8, 0.4, 0);
    rightHand.name = 'rightHand';
    humanGroup.add(rightHand);

    // Create legs
    const legGeometry = new THREE.CylinderGeometry(0.15, 0.15, 0.8, 16);
    const legMaterial = new THREE.MeshLambertMaterial({ color: 0x333333 });
    
    const leftLeg = new THREE.Mesh(legGeometry, legMaterial);
    leftLeg.position.set(-0.2, -0.4, 0);
    leftLeg.name = 'leftLeg';
    humanGroup.add(leftLeg);

    const rightLeg = new THREE.Mesh(legGeometry, legMaterial);
    rightLeg.position.set(0.2, -0.4, 0);
    rightLeg.name = 'rightLeg';
    humanGroup.add(rightLeg);

    humanModelRef.current = humanGroup;
    scene.add(humanGroup);
    
    // Add some rotation to make it more visible
    humanGroup.rotation.y = Math.PI / 6;
  };

  // Animate human model based on gesture
  useEffect(() => {
    if (!humanModelRef.current || !is3DReady) return;

    const human = humanModelRef.current;
    const keyframes = animation.keyframes;
    
    if (isPlaying && keyframes.length > 0) {
      const currentTime = (progress / 100) * currentInstruction.duration;
      const currentKeyframe = keyframes.find((k: { time: number; action: string }) => k.time >= currentTime) || keyframes[0];
      
      // Apply animation based on keyframe
      applyGestureAnimation(human, currentKeyframe.action);
    }
  }, [progress, isPlaying, animation, is3DReady, currentInstruction]);

  const applyGestureAnimation = (human: THREE.Group, action: string) => {
    const rightArm = human.children.find(child => child.position.x > 0 && (child as THREE.Mesh).geometry instanceof THREE.CylinderGeometry) as THREE.Mesh;
    const leftArm = human.children.find(child => child.position.x < 0 && (child as THREE.Mesh).geometry instanceof THREE.CylinderGeometry) as THREE.Mesh;
    const head = human.children.find(child => (child as THREE.Mesh).geometry instanceof THREE.SphereGeometry && child.position.y > 1) as THREE.Mesh;

    if (!rightArm || !leftArm || !head) return;

    // Reset positions
    rightArm.rotation.set(0, 0, -Math.PI / 4);
    leftArm.rotation.set(0, 0, Math.PI / 4);
    head.rotation.set(0, 0, 0);

    switch (action) {
      case "point_to_chest":
        rightArm.rotation.set(0, 0, Math.PI / 2);
        break;
      case "point_forward":
        rightArm.rotation.set(0, 0, -Math.PI / 6);
        break;
      case "palms_up":
        leftArm.rotation.set(0, 0, Math.PI / 2);
        rightArm.rotation.set(0, 0, Math.PI / 2);
        break;
      case "bring_to_chest":
        leftArm.rotation.set(0, 0, Math.PI / 3);
        rightArm.rotation.set(0, 0, Math.PI / 3);
        break;
      case "start_wave":
        rightArm.rotation.set(0, 0, -Math.PI / 3);
        break;
      case "wave_left":
        rightArm.rotation.set(0, 0, -Math.PI / 4);
        break;
      case "wave_right":
        rightArm.rotation.set(0, 0, -Math.PI / 6);
        break;
      case "nod_down":
        head.rotation.x = Math.PI / 6;
        break;
      case "nod_up":
        head.rotation.x = -Math.PI / 6;
        break;
      case "shake_left":
        head.rotation.y = Math.PI / 6;
        break;
      case "shake_right":
        head.rotation.y = -Math.PI / 6;
        break;
      case "hand_to_heart":
        rightArm.rotation.set(0, 0, Math.PI / 2);
        break;
      case "raise_hand":
        rightArm.rotation.set(0, 0, -Math.PI / 2);
        break;
      case "point_to_self":
        rightArm.rotation.set(0, 0, Math.PI / 3);
        break;
    }
  };

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
          🎬 Real Human Body Language Translation
        </Typography>

        {/* 3D Video Display Area */}
        <Box sx={{ 
          bgcolor: 'black', 
          borderRadius: 2, 
          mb: 3,
          height: 400,
          position: 'relative',
          overflow: 'hidden'
        }}>
          <div 
            ref={mountRef} 
            style={{ 
              width: '100%', 
              height: '100%',
              display: is3DReady ? 'block' : 'none'
            }} 
          />

          {/* Loading overlay */}
          {!is3DReady && (
            <Box sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white'
            }}>
              <Typography variant="h6">Loading 3D Human Model...</Typography>
            </Box>
          )}

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
            <Chip label="3D Human Model" size="small" color="primary" />
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

export default RealHumanVideo;

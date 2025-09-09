import React, { useState, useEffect, useRef, useCallback } from 'react';
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
  Slider,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Replay as ReplayIcon,
  VolumeUp as VolumeIcon,
  VolumeOff as MuteIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import * as THREE from 'three';

interface BodyLanguageInstruction {
  gesture_type: string;
  description: string;
  duration: number;
  intensity: number;
  sequence_order: number;
}

interface RealHumanBodyAnimationProps {
  instructions: BodyLanguageInstruction[];
  onComplete?: () => void;
}

const RealHumanBodyAnimation: React.FC<RealHumanBodyAnimationProps> = ({
  instructions,
  onComplete
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [isMuted, setIsMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [showMeaning, setShowMeaning] = useState(false);
  const [animationSpeed, setAnimationSpeed] = useState(1.0);
  const [showSettings, setShowSettings] = useState(false);
  const progressRef = useRef<NodeJS.Timeout | null>(null);
  const mountRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const humanRef = useRef<THREE.Group | null>(null);
  const animationRef = useRef<number | null>(null);
  const mixerRef = useRef<THREE.AnimationMixer | null>(null);
  const clockRef = useRef<THREE.Clock>(new THREE.Clock());

  const currentInstruction = instructions[currentStep];

  // Reset animation when new instructions are received
  useEffect(() => {
    if (instructions.length > 0) {
      setCurrentStep(0);
      setProgress(0);
      setIsPlaying(true);
    }
  }, [instructions]);

  // Handle animation progression
  useEffect(() => {
    if (instructions.length === 0) return;

    const totalDuration = instructions.reduce((sum, instruction) => sum + instruction.duration, 0);
    const progressInterval = 100; // Update every 100ms

    if (isPlaying) {
      progressRef.current = setInterval(() => {
        setProgress(prevProgress => {
          const newProgress = prevProgress + (progressInterval / (totalDuration * 1000)) * 100;
          
          if (newProgress >= 100) {
            // Animation complete
            if (onComplete) onComplete();
            return 100;
          }
          
          // Check if we need to move to next instruction
          const currentTime = (newProgress / 100) * totalDuration;
          let accumulatedTime = 0;
          
          for (let i = 0; i < instructions.length; i++) {
            accumulatedTime += instructions[i].duration;
            if (currentTime <= accumulatedTime) {
              if (i !== currentStep) {
                setCurrentStep(i);
              }
              break;
            }
          }
          
          return newProgress;
        });
      }, progressInterval);
    }

    return () => {
      if (progressRef.current) {
        clearInterval(progressRef.current);
      }
    };
  }, [instructions, isPlaying, currentStep, onComplete]);

  // Initialize 3D scene
  useEffect(() => {
    if (!mountRef.current) return;

    // Clear any existing content
    while (mountRef.current.firstChild) {
      mountRef.current.removeChild(mountRef.current.firstChild);
    }

    // Create scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0a);
    scene.fog = new THREE.Fog(0x0a0a0a, 5, 15);
    sceneRef.current = scene;

    // Create camera
    const camera = new THREE.PerspectiveCamera(60, 640 / 480, 0.1, 1000);
    camera.position.set(0, 1.6, 3.5);
    camera.lookAt(0, 1.6, 0);

    // Create renderer
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true,
      alpha: true,
      powerPreference: "high-performance"
    });
    renderer.setSize(640, 480);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    rendererRef.current = renderer;

    // Add professional lighting
    const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
    directionalLight.position.set(5, 8, 5);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 4096;
    directionalLight.shadow.mapSize.height = 4096;
    directionalLight.shadow.camera.near = 0.5;
    directionalLight.shadow.camera.far = 50;
    directionalLight.shadow.camera.left = -10;
    directionalLight.shadow.camera.right = 10;
    directionalLight.shadow.camera.top = 10;
    directionalLight.shadow.camera.bottom = -10;
    scene.add(directionalLight);

    // Add rim light for depth
    const rimLight = new THREE.DirectionalLight(0x87ceeb, 0.3);
    rimLight.position.set(-5, 3, -5);
    scene.add(rimLight);

    // Create realistic human figure
    const human = createAdvancedHuman();
    humanRef.current = human;
    scene.add(human);

    // Add professional ground
    const groundGeometry = new THREE.PlaneGeometry(20, 20);
    const groundMaterial = new THREE.MeshLambertMaterial({ 
      color: 0x2c3e50
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Add subtle background elements
    addBackgroundElements(scene);

    mountRef.current.appendChild(renderer.domElement);

    // Animation loop
    const animate = () => {
      animationRef.current = requestAnimationFrame(animate);
      updateAdvancedAnimation();
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  const addBackgroundElements = (scene: THREE.Scene) => {
    // Add subtle grid
    const gridHelper = new THREE.GridHelper(10, 20, 0x444444, 0x222222);
    gridHelper.position.y = 0.01;
    scene.add(gridHelper);

    // Add atmospheric particles
    const particleCount = 100;
    const particles = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount * 3; i += 3) {
      positions[i] = (Math.random() - 0.5) * 20;
      positions[i + 1] = Math.random() * 10;
      positions[i + 2] = (Math.random() - 0.5) * 20;
    }
    
    particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const particleMaterial = new THREE.PointsMaterial({
      color: 0x87ceeb,
      size: 0.05,
      transparent: true,
      opacity: 0.3
    });
    
    const particleSystem = new THREE.Points(particles, particleMaterial);
    scene.add(particleSystem);
  };

  const createAdvancedHuman = (): THREE.Group => {
    const human = new THREE.Group();

    // Create advanced head with facial features
    const head = createAdvancedHead();
    human.add(head);

    // Create detailed torso with clothing
    const torso = createDetailedTorso();
    human.add(torso);

    // Create articulated arms with joints
    const arms = createArticulatedArms();
    human.add(arms);

    // Create detailed hands with fingers
    const hands = createDetailedHands();
    human.add(hands);

    // Create realistic legs
    const legs = createRealisticLegs();
    human.add(legs);

    // Create detailed feet
    const feet = createDetailedFeet();
    human.add(feet);

    return human;
  };

  const createAdvancedHead = (): THREE.Group => {
    const headGroup = new THREE.Group();

    // Main head
    const headGeometry = new THREE.SphereGeometry(0.12, 32, 32);
    const headMaterial = new THREE.MeshLambertMaterial({ 
      color: 0xffdbac
    });
    const head = new THREE.Mesh(headGeometry, headMaterial);
    head.position.y = 1.7;
    head.castShadow = true;
    headGroup.add(head);

    // Hair
    const hairGeometry = new THREE.SphereGeometry(0.13, 32, 32);
    const hairMaterial = new THREE.MeshLambertMaterial({ 
      color: 0x2c1810
    });
    const hair = new THREE.Mesh(hairGeometry, hairMaterial);
    hair.position.y = 1.75;
    hair.scale.y = 0.8;
    hair.castShadow = true;
    headGroup.add(hair);

    // Eyes with detailed features
    const eyeGeometry = new THREE.SphereGeometry(0.015, 16, 16);
    const eyeMaterial = new THREE.MeshLambertMaterial({ color: 0x000000 });
    
    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    leftEye.position.set(-0.04, 1.75, 0.1);
    headGroup.add(leftEye);
    
    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
    rightEye.position.set(0.04, 1.75, 0.1);
    headGroup.add(rightEye);

    // Eyebrows
    const eyebrowGeometry = new THREE.BoxGeometry(0.03, 0.005, 0.01);
    const eyebrowMaterial = new THREE.MeshLambertMaterial({ color: 0x2c1810 });
    
    const leftEyebrow = new THREE.Mesh(eyebrowGeometry, eyebrowMaterial);
    leftEyebrow.position.set(-0.04, 1.78, 0.11);
    headGroup.add(leftEyebrow);
    
    const rightEyebrow = new THREE.Mesh(eyebrowGeometry, eyebrowMaterial);
    rightEyebrow.position.set(0.04, 1.78, 0.11);
    headGroup.add(rightEyebrow);

    // Nose
    const noseGeometry = new THREE.ConeGeometry(0.01, 0.03, 8);
    const noseMaterial = new THREE.MeshLambertMaterial({ color: 0xffdbac });
    const nose = new THREE.Mesh(noseGeometry, noseMaterial);
    nose.position.set(0, 1.72, 0.12);
    nose.rotation.x = Math.PI / 2;
    headGroup.add(nose);

    // Mouth
    const mouthGeometry = new THREE.BoxGeometry(0.04, 0.01, 0.005);
    const mouthMaterial = new THREE.MeshLambertMaterial({ color: 0x8b0000 });
    const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial);
    mouth.position.set(0, 1.65, 0.11);
    headGroup.add(mouth);

    return headGroup;
  };

  const createDetailedTorso = (): THREE.Group => {
    const torsoGroup = new THREE.Group();

    // Main torso
    const torsoGeometry = new THREE.CylinderGeometry(0.22, 0.25, 0.5, 16);
    const torsoMaterial = new THREE.MeshLambertMaterial({ 
      color: 0x4a90e2
    });
    const torso = new THREE.Mesh(torsoGeometry, torsoMaterial);
    torso.position.y = 1.25;
    torso.castShadow = true;
    torsoGroup.add(torso);

    // Shoulders
    const shoulderGeometry = new THREE.CylinderGeometry(0.08, 0.08, 0.6, 16);
    const shoulderMaterial = new THREE.MeshLambertMaterial({ 
      color: 0xffdbac
    });
    const shoulders = new THREE.Mesh(shoulderGeometry, shoulderMaterial);
    shoulders.position.y = 1.45;
    shoulders.rotation.z = Math.PI / 2;
    shoulders.castShadow = true;
    torsoGroup.add(shoulders);

    return torsoGroup;
  };

  const createArticulatedArms = (): THREE.Group => {
    const armsGroup = new THREE.Group();

    // Upper arms
    const upperArmGeometry = new THREE.CylinderGeometry(0.04, 0.05, 0.25, 16);
    const armMaterial = new THREE.MeshLambertMaterial({ 
      color: 0xffdbac
    });

    const leftUpperArm = new THREE.Mesh(upperArmGeometry, armMaterial);
    leftUpperArm.position.set(-0.35, 1.35, 0);
    leftUpperArm.castShadow = true;
    armsGroup.add(leftUpperArm);

    const rightUpperArm = new THREE.Mesh(upperArmGeometry, armMaterial);
    rightUpperArm.position.set(0.35, 1.35, 0);
    rightUpperArm.castShadow = true;
    armsGroup.add(rightUpperArm);

    // Lower arms
    const lowerArmGeometry = new THREE.CylinderGeometry(0.035, 0.04, 0.25, 16);

    const leftLowerArm = new THREE.Mesh(lowerArmGeometry, armMaterial);
    leftLowerArm.position.set(-0.35, 1.1, 0);
    leftLowerArm.castShadow = true;
    armsGroup.add(leftLowerArm);

    const rightLowerArm = new THREE.Mesh(lowerArmGeometry, armMaterial);
    rightLowerArm.position.set(0.35, 1.1, 0);
    rightLowerArm.castShadow = true;
    armsGroup.add(rightLowerArm);

    return armsGroup;
  };

  const createDetailedHands = (): THREE.Group => {
    const handsGroup = new THREE.Group();

    // Hand geometry
    const handGeometry = new THREE.SphereGeometry(0.06, 16, 16);
    const handMaterial = new THREE.MeshLambertMaterial({ 
      color: 0xffdbac
    });

    const leftHand = new THREE.Mesh(handGeometry, handMaterial);
    leftHand.position.set(-0.35, 0.95, 0);
    leftHand.castShadow = true;
    handsGroup.add(leftHand);

    const rightHand = new THREE.Mesh(handGeometry, handMaterial);
    rightHand.position.set(0.35, 0.95, 0);
    rightHand.castShadow = true;
    handsGroup.add(rightHand);

    return handsGroup;
  };

  const createRealisticLegs = (): THREE.Group => {
    const legsGroup = new THREE.Group();

    // Upper legs
    const upperLegGeometry = new THREE.CylinderGeometry(0.07, 0.08, 0.4, 16);
    const legMaterial = new THREE.MeshLambertMaterial({ 
      color: 0x2c3e50
    });

    const leftUpperLeg = new THREE.Mesh(upperLegGeometry, legMaterial);
    leftUpperLeg.position.set(-0.12, 0.8, 0);
    leftUpperLeg.castShadow = true;
    legsGroup.add(leftUpperLeg);

    const rightUpperLeg = new THREE.Mesh(upperLegGeometry, legMaterial);
    rightUpperLeg.position.set(0.12, 0.8, 0);
    rightUpperLeg.castShadow = true;
    legsGroup.add(rightUpperLeg);

    // Lower legs
    const lowerLegGeometry = new THREE.CylinderGeometry(0.06, 0.07, 0.4, 16);

    const leftLowerLeg = new THREE.Mesh(lowerLegGeometry, legMaterial);
    leftLowerLeg.position.set(-0.12, 0.4, 0);
    leftLowerLeg.castShadow = true;
    legsGroup.add(leftLowerLeg);

    const rightLowerLeg = new THREE.Mesh(lowerLegGeometry, legMaterial);
    rightLowerLeg.position.set(0.12, 0.4, 0);
    rightLowerLeg.castShadow = true;
    legsGroup.add(rightLowerLeg);

    return legsGroup;
  };

  const createDetailedFeet = (): THREE.Group => {
    const feetGroup = new THREE.Group();

    // Foot geometry
    const footGeometry = new THREE.BoxGeometry(0.1, 0.06, 0.22);
    const footMaterial = new THREE.MeshLambertMaterial({ 
      color: 0x34495e
    });

    const leftFoot = new THREE.Mesh(footGeometry, footMaterial);
    leftFoot.position.set(-0.12, 0.2, 0.08);
    leftFoot.castShadow = true;
    feetGroup.add(leftFoot);

    const rightFoot = new THREE.Mesh(footGeometry, footMaterial);
    rightFoot.position.set(0.12, 0.2, 0.08);
    rightFoot.castShadow = true;
    feetGroup.add(rightFoot);

    return feetGroup;
  };

  const updateAdvancedAnimation = () => {
    if (!humanRef.current || !currentInstruction) return;

    const time = Date.now() * 0.001 * animationSpeed;
    const human = humanRef.current;

    // Get body parts for animation
    const head = human.children[0];
    const torso = human.children[1];
    const arms = human.children[2];
    const hands = human.children[3];
    const legs = human.children[4];
    const feet = human.children[5];

    // Apply advanced gesture-specific animations
    switch (currentInstruction.gesture_type) {
      case 'hand':
        // Hand gesture animation - pointing to chest
        const rightUpperArmHand = arms.children[1];
        const rightLowerArmHand = arms.children[3];
        const rightHandHand = hands.children[1];
        
        rightUpperArmHand.rotation.x = -0.3;
        rightUpperArmHand.rotation.z = 0.2;
        rightLowerArmHand.rotation.x = -0.5;
        rightHandHand.rotation.x = -0.7;
        rightHandHand.position.x = 0.3; // Move hand toward chest
        
        // Add subtle body movement
        torso.rotation.x = 0.05;
        break;

      case 'face':
        // Facial expression animation
        const eyebrowsFace = [head.children[2], head.children[3]];
        const mouthFace = head.children[5];
        
        // Show emotion with raised eyebrows
        eyebrowsFace.forEach(eyebrow => {
          eyebrow.rotation.z = 0.15;
        });
        
        // Slight mouth movement
        mouthFace.scale.x = 1.1;
        mouthFace.scale.y = 1.05;
        
        // Add head tilt
        head.rotation.z = 0.1;
        break;

      case 'head':
        // Head movement animation (nod/shake)
        const headAngle = Math.sin(time * 2) * 0.25;
        head.rotation.x = headAngle;
        
        // Add subtle body movement
        torso.rotation.x = headAngle * 0.1;
        break;

      case 'body':
        // Body posture animation
        const bodyAngle = Math.sin(time * 1.5) * 0.2;
        torso.rotation.x = bodyAngle;
        
        // Add arm movement
        const leftUpperArmBody = arms.children[0];
        const rightUpperArmBody = arms.children[1];
        leftUpperArmBody.rotation.x = bodyAngle * 0.5;
        rightUpperArmBody.rotation.x = -bodyAngle * 0.5;
        break;
      case 'wave':
        // Professional waving animation
        const waveAngle = Math.sin(time * 3) * 0.6;
        const rightUpperArmWave = arms.children[1];
        const rightLowerArmWave = arms.children[3];
        const rightHandWave = hands.children[1];
        
        rightUpperArmWave.rotation.z = waveAngle * 0.3;
        rightLowerArmWave.rotation.z = waveAngle * 0.7;
        rightHandWave.rotation.z = waveAngle;
        
        // Add facial expression
        const mouthWave = head.children[5];
        mouthWave.scale.x = 1 + Math.sin(time * 3) * 0.1;
        break;

      case 'point':
        // Professional pointing gesture
        const rightUpperArmPoint = arms.children[1];
        const rightLowerArmPoint = arms.children[3];
        const rightHandPoint = hands.children[1];
        
        rightUpperArmPoint.rotation.x = -0.4;
        rightUpperArmPoint.rotation.z = 0.3;
        rightLowerArmPoint.rotation.x = -0.6;
        rightHandPoint.rotation.x = -0.8;
        
        // Serious facial expression
        const eyebrowsPoint = [head.children[2], head.children[3]];
        eyebrowsPoint.forEach(eyebrow => {
          eyebrow.rotation.z = 0.1;
        });
        break;

      case 'nod':
        // Realistic nodding animation
        const nodAngle = Math.sin(time * 2) * 0.25;
        head.rotation.x = nodAngle;
        
        // Add subtle body movement
        torso.rotation.x = nodAngle * 0.1;
        break;

      case 'shake':
        // Natural head shaking
        const shakeAngle = Math.sin(time * 4) * 0.35;
        head.rotation.y = shakeAngle;
        
        // Add body sway
        torso.rotation.y = shakeAngle * 0.2;
        break;

      case 'swim':
        // Coordinated swimming motion
        const swimAngle = Math.sin(time * 2) * 0.5;
        const leftUpperArmSwim = arms.children[0];
        const leftLowerArmSwim = arms.children[2];
        const leftHandSwim = hands.children[0];
        const rightUpperArmSwim = arms.children[1];
        const rightLowerArmSwim = arms.children[3];
        const rightHandSwim = hands.children[1];
        
        leftUpperArmSwim.rotation.x = swimAngle;
        leftLowerArmSwim.rotation.x = swimAngle * 1.2;
        leftHandSwim.rotation.x = swimAngle * 1.5;
        
        rightUpperArmSwim.rotation.x = -swimAngle;
        rightLowerArmSwim.rotation.x = -swimAngle * 1.2;
        rightHandSwim.rotation.x = -swimAngle * 1.5;
        
        // Add body movement
        torso.rotation.x = swimAngle * 0.1;
        break;

      case 'greet':
        // Welcoming gesture
        const greetAngle = Math.sin(time * 1.5) * 0.4;
        const leftUpperArmGreet = arms.children[0];
        const rightUpperArmGreet = arms.children[1];
        
        leftUpperArmGreet.rotation.z = greetAngle;
        rightUpperArmGreet.rotation.z = -greetAngle;
        
        // Happy facial expression
        const mouthGreet = head.children[5];
        mouthGreet.scale.x = 1.2;
        mouthGreet.scale.y = 1.5;
        break;

      case 'think':
        // Thinking pose
        const leftUpperArmThink = arms.children[0];
        const leftLowerArmThink = arms.children[2];
        const leftHandThink = hands.children[0];
        
        leftUpperArmThink.rotation.x = -0.3;
        leftUpperArmThink.rotation.z = 0.2;
        leftLowerArmThink.rotation.x = -0.4;
        leftHandThink.position.y = 1.75;
        leftHandThink.position.z = 0.05;
        
        // Thoughtful expression
        const eyebrowsThink = [head.children[2], head.children[3]];
        eyebrowsThink.forEach(eyebrow => {
          eyebrow.rotation.z = -0.1;
        });
        break;

      default:
        // Default animation for unrecognized gesture types
        const defaultAngle = Math.sin(time * 1.5) * 0.15;
        const rightUpperArmDefault = arms.children[1];
        const rightLowerArmDefault = arms.children[3];
        
        rightUpperArmDefault.rotation.x = defaultAngle * 0.3;
        rightLowerArmDefault.rotation.x = defaultAngle * 0.5;
        
        // Add subtle head movement
        head.rotation.x = defaultAngle * 0.2;
        
        // Natural breathing
        torso.scale.y = 1 + Math.sin(time * 0.8) * 0.02;
        break;
    }
  };

  // Progress management
  useEffect(() => {
    if (isPlaying && currentInstruction) {
      const duration = currentInstruction.duration * 1000;
      const startTime = Date.now();

      const updateProgress = () => {
        const elapsed = Date.now() - startTime;
        const newProgress = Math.min((elapsed / duration) * 100, 100);
        setProgress(newProgress);

        if (newProgress >= 100) {
          if (currentStep < instructions.length - 1) {
            setCurrentStep(currentStep + 1);
            setProgress(0);
          } else {
            setIsPlaying(false);
            onComplete?.();
          }
        } else {
          progressRef.current = setTimeout(updateProgress, 16);
        }
      };

      updateProgress();
    }

    return () => {
      if (progressRef.current) {
        clearTimeout(progressRef.current);
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
  };

  const handleMute = () => {
    setIsMuted(!isMuted);
  };

  const handleSpeedChange = (event: Event, newValue: number | number[]) => {
    setAnimationSpeed(newValue as number);
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ flex: 1 }}>
            Professional 3D Body Language Animation
          </Typography>
          <Chip 
            label={`${currentStep + 1}/${instructions.length}`}
            color="primary"
            size="small"
          />
          <IconButton onClick={() => setShowSettings(!showSettings)} size="small">
            <SettingsIcon />
          </IconButton>
        </Box>

        {showSettings && (
          <Paper sx={{ p: 2, mb: 2, backgroundColor: '#f8f9fa' }}>
            <Typography variant="body2" gutterBottom>
              Animation Speed: {animationSpeed.toFixed(1)}x
            </Typography>
            <Slider
              value={animationSpeed}
              onChange={handleSpeedChange}
              min={0.5}
              max={2.0}
              step={0.1}
              marks={[
                { value: 0.5, label: '0.5x' },
                { value: 1.0, label: '1.0x' },
                { value: 2.0, label: '2.0x' }
              ]}
            />
          </Paper>
        )}

        <Box sx={{ flex: 1, position: 'relative', mb: 2 }}>
          <div 
            ref={mountRef} 
            style={{ 
              width: '100%', 
              height: '100%', 
              minHeight: '400px',
              borderRadius: '8px',
              overflow: 'hidden',
              boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
            }}
          />
        </Box>

        {currentInstruction && (
          <Paper sx={{ p: 2, mb: 2, backgroundColor: '#f5f5f5' }}>
            <Typography variant="body2" color="text.secondary">
              <strong>Current Gesture:</strong> {currentInstruction.gesture_type}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>Description:</strong> {currentInstruction.description}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>Intensity:</strong> {currentInstruction.intensity}/10
            </Typography>
          </Paper>
        )}

        <LinearProgress 
          variant="determinate" 
          value={progress} 
          sx={{ mb: 2 }}
        />

        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
          <IconButton onClick={handlePlayPause} color="primary">
            {isPlaying ? <PauseIcon /> : <PlayIcon />}
          </IconButton>
          <IconButton onClick={handleReplay} color="primary">
            <ReplayIcon />
          </IconButton>
          <IconButton onClick={handleMute} color="primary">
            {isMuted ? <MuteIcon /> : <VolumeIcon />}
          </IconButton>
        </Box>
      </CardContent>
    </Card>
  );
};

export default RealHumanBodyAnimation;

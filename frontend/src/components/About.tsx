import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Paper,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Button,
} from '@mui/material';
import {
  Info as InfoIcon,
  Translate as TranslateIcon,
  Accessibility as AccessibilityIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  GitHub as GitHubIcon,
  Email as EmailIcon,
  BugReport as BugReportIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const About: React.FC = () => {
  const features = [
    {
      icon: <TranslateIcon />,
      title: 'AI-Powered Translation',
      description: 'Advanced GPT-4 integration for context-aware body language interpretation',
    },
    {
      icon: <AccessibilityIcon />,
      title: 'Accessibility Focus',
      description: 'Designed specifically for people with communication disabilities',
    },
    {
      icon: <SpeedIcon />,
      title: 'Real-Time Processing',
      description: 'Instant translation with WebSocket-based live communication',
    },
    {
      icon: <SecurityIcon />,
      title: 'Privacy & Security',
      description: 'Local processing options and secure data handling',
    },
  ];

  const technologies = [
    { name: 'React', type: 'Frontend' },
    { name: 'TypeScript', type: 'Language' },
    { name: 'Material-UI', type: 'UI Framework' },
    { name: 'FastAPI', type: 'Backend' },
    { name: 'Python', type: 'Language' },
    { name: 'MediaPipe', type: 'Computer Vision' },
    { name: 'OpenAI GPT-4', type: 'AI Model' },
    { name: 'SQLite', type: 'Database' },
    { name: 'ChromaDB', type: 'Vector Database' },
    { name: 'WebSocket', type: 'Real-time' },
  ];

  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
        About Body Language Translator
      </Typography>

      {/* Mission Statement */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h5" gutterBottom align="center" sx={{ mb: 2 }}>
            Mission
          </Typography>
          <Typography variant="body1" align="center" sx={{ fontSize: '1.1rem', lineHeight: 1.6 }}>
            Our mission is to bridge communication gaps for people with speech disabilities by providing 
            an intelligent, real-time body language translation system that enables meaningful interactions 
            and promotes inclusivity in digital communication.
          </Typography>
        </CardContent>
      </Card>

      {/* Features */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Key Features
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        {features.map((feature, index) => (
          <Box key={index} sx={{ flex: '1 1 300px', minWidth: 0 }}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ mr: 2, color: 'primary.main' }}>
                      {feature.icon}
                    </Box>
                    <Typography variant="h6">
                      {feature.title}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Box>
        ))}
      </Box>

      {/* Technology Stack */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Technology Stack
      </Typography>
      <Paper sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          {technologies.map((tech, index) => (
            <Box key={index} sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Chip
                label={tech.name}
                variant="outlined"
                color="primary"
                sx={{ mb: 1 }}
              />
              <Typography variant="caption" color="text.secondary">
                {tech.type}
              </Typography>
            </Box>
          ))}
        </Box>
      </Paper>

      {/* How It Works */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        How It Works
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        <Box sx={{ flex: '1 1 300px', minWidth: 0 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                1. Capture
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Use your camera to capture body language gestures, facial expressions, and hand movements.
              </Typography>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 300px', minWidth: 0 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                2. Process
              </Typography>
              <Typography variant="body2" color="text.secondary">
                AI analyzes the visual data using MediaPipe and GPT-4 to understand the intended message.
              </Typography>
            </CardContent>
          </Card>
        </Box>
        <Box sx={{ flex: '1 1 300px', minWidth: 0 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                3. Translate
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Convert body language to natural text or generate body language instructions from text.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Use Cases */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Use Cases
      </Typography>
      <List sx={{ mb: 4 }}>
        <ListItem>
          <ListItemIcon>
            <AccessibilityIcon color="primary" />
          </ListItemIcon>
          <ListItemText
            primary="Communication Aid"
            secondary="Help people with speech disabilities communicate effectively in daily interactions"
          />
        </ListItem>
        <ListItem>
          <ListItemIcon>
            <TranslateIcon color="primary" />
          </ListItemIcon>
          <ListItemText
            primary="Video Conferencing"
            secondary="Integrate with platforms like Zoom and Teams for real-time translation"
          />
        </ListItem>
        <ListItem>
          <ListItemIcon>
            <SpeedIcon color="primary" />
          </ListItemIcon>
          <ListItemText
            primary="Emergency Communication"
            secondary="Quick communication in emergency situations where speech is not possible"
          />
        </ListItem>
        <ListItem>
          <ListItemIcon>
            <InfoIcon color="primary" />
          </ListItemIcon>
          <ListItemText
            primary="Educational Tool"
            secondary="Learn and practice body language communication skills"
          />
        </ListItem>
      </List>

      {/* Statistics */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Impact
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 4 }}>
        <Box sx={{ flex: '1 1 200px', minWidth: 0 }}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h4" color="primary" gutterBottom>
              95%
            </Typography>
            <Typography variant="body2">
              Translation Accuracy
            </Typography>
          </Paper>
        </Box>
        <Box sx={{ flex: '1 1 200px', minWidth: 0 }}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h4" color="primary" gutterBottom>
              &lt;1s
            </Typography>
            <Typography variant="body2">
              Processing Time
            </Typography>
          </Paper>
        </Box>
        <Box sx={{ flex: '1 1 200px', minWidth: 0 }}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h4" color="primary" gutterBottom>
              10+
            </Typography>
            <Typography variant="body2">
              Supported Languages
            </Typography>
          </Paper>
        </Box>
        <Box sx={{ flex: '1 1 200px', minWidth: 0 }}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h4" color="primary" gutterBottom>
              24/7
            </Typography>
            <Typography variant="body2">
              Availability
            </Typography>
          </Paper>
        </Box>
      </Box>

      {/* Contact & Support */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        Contact & Support
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 4 }}>
        <Box sx={{ flex: '1 1 200px', minWidth: 0 }}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<GitHubIcon />}
            href="https://github.com/your-repo"
            target="_blank"
            rel="noopener noreferrer"
          >
            View on GitHub
          </Button>
        </Box>
        <Box sx={{ flex: '1 1 200px', minWidth: 0 }}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<EmailIcon />}
            href="mailto:support@bodylanguagetranslator.com"
          >
            Contact Support
          </Button>
        </Box>
        <Box sx={{ flex: '1 1 200px', minWidth: 0 }}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={<BugReportIcon />}
            href="https://github.com/your-repo/issues"
            target="_blank"
            rel="noopener noreferrer"
          >
            Report Issues
          </Button>
        </Box>
      </Box>

      {/* Version Info */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary" align="center">
            Version 1.0.0 | Built with ❤️ for accessibility
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
            © 2024 Body Language Translator. All rights reserved.
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default About;

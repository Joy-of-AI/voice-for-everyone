import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Switch,
  FormControlLabel,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Paper,
  Alert,
  Chip,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Translate as TranslateIcon,
  VolumeUp as VolumeIcon,
  Accessibility as AccessibilityIcon,
  Speed as SpeedIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

interface SettingsData {
  language: string;
  confidenceThreshold: number;
  audioEnabled: boolean;
  audioVolume: number;
  audioSpeed: number;
  highContrast: boolean;
  largeText: boolean;
  voiceCommands: boolean;
  autoSave: boolean;
  processingSpeed: number;
  apiEndpoint: string;
}

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<SettingsData>({
    language: 'en',
    confidenceThreshold: 0.7,
    audioEnabled: true,
    audioVolume: 0.8,
    audioSpeed: 1.0,
    highContrast: false,
    largeText: false,
    voiceCommands: false,
    autoSave: true,
    processingSpeed: 1.0,
    apiEndpoint: 'http://localhost:8000',
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'success' | 'error' | null>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = () => {
    try {
      const savedSettings = localStorage.getItem('bodyLanguageTranslatorSettings');
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings);
        setSettings({ ...settings, ...parsed });
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const saveSettings = async () => {
    setIsSaving(true);
    setSaveStatus(null);

    try {
      localStorage.setItem('bodyLanguageTranslatorSettings', JSON.stringify(settings));
      
      // Test API endpoint
      const response = await fetch(`${settings.apiEndpoint}/health`);
      if (response.ok) {
        setSaveStatus('success');
      } else {
        setSaveStatus('error');
      }
    } catch (error) {
      setSaveStatus('error');
    } finally {
      setIsSaving(false);
    }
  };

  const resetSettings = () => {
    const defaultSettings: SettingsData = {
      language: 'en',
      confidenceThreshold: 0.7,
      audioEnabled: true,
      audioVolume: 0.8,
      audioSpeed: 1.0,
      highContrast: false,
      largeText: false,
      voiceCommands: false,
      autoSave: true,
      processingSpeed: 1.0,
      apiEndpoint: 'http://localhost:8000',
    };
    setSettings(defaultSettings);
    localStorage.removeItem('bodyLanguageTranslatorSettings');
  };

  const handleSettingChange = (key: keyof SettingsData, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  return (
    <Box sx={{ py: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
        Settings
      </Typography>

      {saveStatus && (
        <Alert 
          severity={saveStatus} 
          sx={{ mb: 3 }}
          onClose={() => setSaveStatus(null)}
        >
          {saveStatus === 'success' 
            ? 'Settings saved successfully!' 
            : 'Failed to save settings. Please check your API endpoint.'
          }
        </Alert>
      )}

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
        {/* Translation Settings */}
        <Box sx={{ flex: '1 1 400px', minWidth: 0 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TranslateIcon color="primary" />
                Translation Settings
              </Typography>

              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Language</InputLabel>
                <Select
                  value={settings.language}
                  label="Language"
                  onChange={(e) => handleSettingChange('language', e.target.value)}
                >
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="es">Spanish</MenuItem>
                  <MenuItem value="fr">French</MenuItem>
                  <MenuItem value="de">German</MenuItem>
                  <MenuItem value="it">Italian</MenuItem>
                  <MenuItem value="pt">Portuguese</MenuItem>
                  <MenuItem value="ru">Russian</MenuItem>
                  <MenuItem value="ja">Japanese</MenuItem>
                  <MenuItem value="ko">Korean</MenuItem>
                  <MenuItem value="zh">Chinese</MenuItem>
                </Select>
              </FormControl>

              <Box sx={{ mb: 2 }}>
                <Typography gutterBottom>
                  Confidence Threshold: {(settings.confidenceThreshold * 100).toFixed(0)}%
                </Typography>
                <Slider
                  value={settings.confidenceThreshold}
                  onChange={(_, value) => handleSettingChange('confidenceThreshold', value)}
                  min={0.1}
                  max={1.0}
                  step={0.1}
                  marks
                  valueLabelDisplay="auto"
                />
              </Box>

              <TextField
                fullWidth
                label="API Endpoint"
                value={settings.apiEndpoint}
                onChange={(e) => handleSettingChange('apiEndpoint', e.target.value)}
                sx={{ mb: 2 }}
              />
            </CardContent>
          </Card>
        </Box>

        {/* Audio Settings */}
        <Box sx={{ flex: '1 1 400px', minWidth: 0 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <VolumeIcon color="primary" />
                Audio Settings
              </Typography>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.audioEnabled}
                    onChange={(e) => handleSettingChange('audioEnabled', e.target.checked)}
                  />
                }
                label="Enable Audio Output"
                sx={{ mb: 2 }}
              />

              <Box sx={{ mb: 2 }}>
                <Typography gutterBottom>
                  Volume: {(settings.audioVolume * 100).toFixed(0)}%
                </Typography>
                <Slider
                  value={settings.audioVolume}
                  onChange={(_, value) => handleSettingChange('audioVolume', value)}
                  min={0}
                  max={1}
                  step={0.1}
                  marks
                  valueLabelDisplay="auto"
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography gutterBottom>
                  Speed: {settings.audioSpeed}x
                </Typography>
                <Slider
                  value={settings.audioSpeed}
                  onChange={(_, value) => handleSettingChange('audioSpeed', value)}
                  min={0.5}
                  max={2.0}
                  step={0.1}
                  marks
                  valueLabelDisplay="auto"
                />
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* Accessibility Settings */}
        <Box sx={{ flex: '1 1 400px', minWidth: 0 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AccessibilityIcon color="primary" />
                Accessibility Settings
              </Typography>

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.highContrast}
                    onChange={(e) => handleSettingChange('highContrast', e.target.checked)}
                  />
                }
                label="High Contrast Mode"
                sx={{ mb: 2 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.largeText}
                    onChange={(e) => handleSettingChange('largeText', e.target.checked)}
                  />
                }
                label="Large Text"
                sx={{ mb: 2 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.voiceCommands}
                    onChange={(e) => handleSettingChange('voiceCommands', e.target.checked)}
                  />
                }
                label="Voice Commands"
                sx={{ mb: 2 }}
              />

              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoSave}
                    onChange={(e) => handleSettingChange('autoSave', e.target.checked)}
                  />
                }
                label="Auto-save Sessions"
                sx={{ mb: 2 }}
              />
            </CardContent>
          </Card>
        </Box>

        {/* General Settings */}
        <Box sx={{ flex: '1 1 400px', minWidth: 0 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                General Settings
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={saveSettings}
                  disabled={isSaving}
                  startIcon={<SaveIcon />}
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  {isSaving ? 'Saving...' : 'Save Settings'}
                </Button>

                <Button
                  variant="outlined"
                  onClick={resetSettings}
                  startIcon={<RefreshIcon />}
                  fullWidth
                >
                  Reset to Defaults
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Performance Settings */}
      <Box sx={{ mt: 3 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SpeedIcon color="primary" />
              Performance Settings
            </Typography>

            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              <Box sx={{ flex: '1 1 200px', minWidth: 0 }}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>    
                  <Typography variant="subtitle2" gutterBottom>
                    Processing Speed
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {settings.processingSpeed}x
                  </Typography>
                  <Slider
                    value={settings.processingSpeed}
                    onChange={(_, value) => handleSettingChange('processingSpeed', value)}
                    min={0.5}
                    max={2.0}
                    step={0.1}
                    sx={{ mt: 1 }}
                  />
                </Paper>
              </Box>
              <Box sx={{ flex: '1 1 200px', minWidth: 0 }}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>    
                  <Typography variant="subtitle2" gutterBottom>
                    Confidence Threshold
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {(settings.confidenceThreshold * 100).toFixed(0)}%
                  </Typography>
                  <Chip 
                    label={settings.confidenceThreshold > 0.8 ? 'High' : settings.confidenceThreshold > 0.6 ? 'Medium' : 'Low'}
                    color={settings.confidenceThreshold > 0.8 ? 'success' : settings.confidenceThreshold > 0.6 ? 'warning' : 'error'}
                    sx={{ mt: 1 }}
                  />
                </Paper>
              </Box>
              <Box sx={{ flex: '1 1 200px', minWidth: 0 }}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>    
                  <Typography variant="subtitle2" gutterBottom>
                    Audio Status
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {settings.audioEnabled ? 'ON' : 'OFF'}
                  </Typography>
                  <Chip 
                    label={settings.audioEnabled ? 'Enabled' : 'Disabled'}
                    color={settings.audioEnabled ? 'success' : 'error'}
                    sx={{ mt: 1 }}
                  />
                </Paper>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default Settings;

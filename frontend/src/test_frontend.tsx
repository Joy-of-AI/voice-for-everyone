/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import '@testing-library/jest-dom';

// Import components to test
import Header from './components/Header';
import BodyLanguageTranslator from './components/BodyLanguageTranslator';
import RealTimeTranslation from './components/RealTimeTranslation';
import Settings from './components/Settings';
import History from './components/History';
import About from './components/About';

// Create theme for testing
const theme = createTheme();

// Mock WebSocket
const mockWebSocket = {
  send: jest.fn(),
  close: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  readyState: 1, // OPEN
};

// Mock WebSocket constructor
global.WebSocket = jest.fn(() => mockWebSocket) as any;

// Mock react-webcam
jest.mock('react-webcam', () => {
  return function DummyWebcam() {
    return <div data-testid="webcam">Webcam Component</div>;
  };
});

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    tr: ({ children, ...props }: any) => <tr {...props}>{children}</tr>,
  },
}));

// Helper function to render components with providers
const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </ThemeProvider>
  );
};

describe('Header Component', () => {
  test('renders header with navigation links', () => {
    renderWithProviders(<Header />);
    
    expect(screen.getByText('Body Language Translator')).toBeInTheDocument();
    expect(screen.getByText('Translator')).toBeInTheDocument();
    expect(screen.getByText('Real-time')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByText('History')).toBeInTheDocument();
    expect(screen.getByText('About')).toBeInTheDocument();
  });

  test('shows connection status', () => {
    renderWithProviders(<Header />);
    
    expect(screen.getByText('Connected')).toBeInTheDocument();
  });
});

describe('BodyLanguageTranslator Component', () => {
  test('renders translator component', () => {
    renderWithProviders(<BodyLanguageTranslator />);
    
    expect(screen.getByText('Body Language Translator')).toBeInTheDocument();
    expect(screen.getByText('Body Language → Text')).toBeInTheDocument();
    expect(screen.getByText('Text → Body Language')).toBeInTheDocument();
  });

  test('switches between translation modes', () => {
    renderWithProviders(<BodyLanguageTranslator />);
    
    const textToBodyButton = screen.getByText('Text → Body Language');
    fireEvent.click(textToBodyButton);
    
    expect(screen.getByText('Text Input')).toBeInTheDocument();
  });

  test('shows webcam when in body-to-text mode', () => {
    renderWithProviders(<BodyLanguageTranslator />);
    
    expect(screen.getByTestId('webcam')).toBeInTheDocument();
  });

  test('handles text input for text-to-body translation', () => {
    renderWithProviders(<BodyLanguageTranslator />);
    
    // Switch to text-to-body mode
    const textToBodyButton = screen.getByText('Text → Body Language');
    fireEvent.click(textToBodyButton);
    
    const textInput = screen.getByLabelText(/Enter text to translate to body language/i);
    fireEvent.change(textInput, { target: { value: 'Hello world' } });
    
    expect(textInput).toHaveValue('Hello world');
  });
});

describe('RealTimeTranslation Component', () => {
  test('renders real-time translation component', () => {
    renderWithProviders(<RealTimeTranslation />);
    
    expect(screen.getByText('Real-Time Body Language Translation')).toBeInTheDocument();
    expect(screen.getByText('Connected')).toBeInTheDocument();
  });

  test('shows camera feed', () => {
    renderWithProviders(<RealTimeTranslation />);
    
    expect(screen.getByTestId('webcam')).toBeInTheDocument();
  });

  test('displays start/stop buttons', () => {
    renderWithProviders(<RealTimeTranslation />);
    
    expect(screen.getByText('Start Real-time Translation')).toBeInTheDocument();
    expect(screen.getByText('Stop Translation')).toBeInTheDocument();
  });

  test('shows translation messages section', () => {
    renderWithProviders(<RealTimeTranslation />);
    
    expect(screen.getByText('Translation Messages')).toBeInTheDocument();
  });

  test('handles text input for sending messages', () => {
    renderWithProviders(<RealTimeTranslation />);
    
    const textInput = screen.getByPlaceholderText('Send text message');
    fireEvent.change(textInput, { target: { value: 'Test message' } });
    
    expect(textInput).toHaveValue('Test message');
  });
});

describe('Settings Component', () => {
  test('renders settings component', () => {
    renderWithProviders(<Settings />);
    
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByText('Translation Settings')).toBeInTheDocument();
    expect(screen.getByText('Audio Settings')).toBeInTheDocument();
    expect(screen.getByText('Accessibility Settings')).toBeInTheDocument();
  });

  test('shows language selection', () => {
    renderWithProviders(<Settings />);
    
    expect(screen.getByLabelText('Language')).toBeInTheDocument();
  });

  test('shows confidence threshold slider', () => {
    renderWithProviders(<Settings />);
    
    expect(screen.getByText(/Confidence Threshold/)).toBeInTheDocument();
  });

  test('shows audio volume control', () => {
    renderWithProviders(<Settings />);
    
    expect(screen.getByText(/Volume/)).toBeInTheDocument();
  });

  test('shows accessibility options', () => {
    renderWithProviders(<Settings />);
    
    expect(screen.getByText('High Contrast Mode')).toBeInTheDocument();
    expect(screen.getByText('Large Text')).toBeInTheDocument();
    expect(screen.getByText('Voice Commands')).toBeInTheDocument();
  });

  test('handles save settings', async () => {
    renderWithProviders(<Settings />);
    
    const saveButton = screen.getByText('Save Settings');
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(saveButton).toHaveTextContent('Saving...');
    });
  });
});

describe('History Component', () => {
  test('renders history component', () => {
    renderWithProviders(<History />);
    
    expect(screen.getByText('Translation History')).toBeInTheDocument();
  });

  test('shows search functionality', () => {
    renderWithProviders(<History />);
    
    const searchInput = screen.getByPlaceholderText('Search sessions...');
    expect(searchInput).toBeInTheDocument();
  });

  test('shows filter options', () => {
    renderWithProviders(<History />);
    
    expect(screen.getByLabelText('Filter by type')).toBeInTheDocument();
  });

  test('displays sessions table', () => {
    renderWithProviders(<History />);
    
    expect(screen.getByText('Date & Time')).toBeInTheDocument();
    expect(screen.getByText('Type')).toBeInTheDocument();
    expect(screen.getByText('Input')).toBeInTheDocument();
    expect(screen.getByText('Output')).toBeInTheDocument();
    expect(screen.getByText('Confidence')).toBeInTheDocument();
    expect(screen.getByText('Status')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();
  });

  test('shows refresh button', () => {
    renderWithProviders(<History />);
    
    expect(screen.getByText('Refresh')).toBeInTheDocument();
  });
});

describe('About Component', () => {
  test('renders about component', () => {
    renderWithProviders(<About />);
    
    expect(screen.getByText('About Body Language Translator')).toBeInTheDocument();
  });

  test('shows mission statement', () => {
    renderWithProviders(<About />);
    
    expect(screen.getByText('Mission')).toBeInTheDocument();
  });

  test('displays key features', () => {
    renderWithProviders(<About />);
    
    expect(screen.getByText('Key Features')).toBeInTheDocument();
    expect(screen.getByText('AI-Powered Translation')).toBeInTheDocument();
    expect(screen.getByText('Accessibility Focus')).toBeInTheDocument();
    expect(screen.getByText('Real-Time Processing')).toBeInTheDocument();
    expect(screen.getByText('Privacy & Security')).toBeInTheDocument();
  });

  test('shows technology stack', () => {
    renderWithProviders(<About />);
    
    expect(screen.getByText('Technology Stack')).toBeInTheDocument();
  });

  test('displays how it works section', () => {
    renderWithProviders(<About />);
    
    expect(screen.getByText('How It Works')).toBeInTheDocument();
    expect(screen.getByText('1. Capture')).toBeInTheDocument();
    expect(screen.getByText('2. Process')).toBeInTheDocument();
    expect(screen.getByText('3. Translate')).toBeInTheDocument();
  });

  test('shows use cases', () => {
    renderWithProviders(<About />);
    
    expect(screen.getByText('Use Cases')).toBeInTheDocument();
  });

  test('displays impact statistics', () => {
    renderWithProviders(<About />);
    
    expect(screen.getByText('Impact')).toBeInTheDocument();
    expect(screen.getByText('95%')).toBeInTheDocument();
    expect(screen.getByText('<1s')).toBeInTheDocument();
    expect(screen.getByText('10+')).toBeInTheDocument();
    expect(screen.getByText('24/7')).toBeInTheDocument();
  });

  test('shows contact information', () => {
    renderWithProviders(<About />);
    
    expect(screen.getByText('Contact & Support')).toBeInTheDocument();
    expect(screen.getByText('View on GitHub')).toBeInTheDocument();
    expect(screen.getByText('Contact Support')).toBeInTheDocument();
    expect(screen.getByText('Report Issues')).toBeInTheDocument();
  });
});

describe('Integration Tests', () => {
  test('components render without crashing', () => {
    const components = [
      <Header key="header" />,
      <BodyLanguageTranslator key="translator" />,
      <RealTimeTranslation key="realtime" />,
      <Settings key="settings" />,
      <History key="history" />,
      <About key="about" />,
    ];

    components.forEach(component => {
      expect(() => renderWithProviders(component)).not.toThrow();
    });
  });

  test('navigation works between components', () => {
    renderWithProviders(<Header />);
    
    const translatorLink = screen.getByText('Translator');
    const realtimeLink = screen.getByText('Real-time');
    const settingsLink = screen.getByText('Settings');
    const historyLink = screen.getByText('History');
    const aboutLink = screen.getByText('About');
    
    expect(translatorLink).toBeInTheDocument();
    expect(realtimeLink).toBeInTheDocument();
    expect(settingsLink).toBeInTheDocument();
    expect(historyLink).toBeInTheDocument();
    expect(aboutLink).toBeInTheDocument();
  });

  test('WebSocket connection handling', () => {
    renderWithProviders(<RealTimeTranslation />);
    
    // Simulate WebSocket connection
    expect(mockWebSocket.addEventListener).toHaveBeenCalled();
  });

  test('localStorage integration for settings', () => {
    const mockLocalStorage = {
      getItem: jest.fn(),
      setItem: jest.fn(),
      removeItem: jest.fn(),
    };
    Object.defineProperty(window, 'localStorage', {
      value: mockLocalStorage,
      writable: true,
    });

    renderWithProviders(<Settings />);
    
    expect(mockLocalStorage.getItem).toHaveBeenCalledWith('bodyLanguageTranslatorSettings');
  });

  test('file upload handling', () => {
    renderWithProviders(<BodyLanguageTranslator />);
    
    const fileInput = screen.getByLabelText(/Upload Video File/i);
    expect(fileInput).toBeInTheDocument();
  });

  test('error handling displays error messages', () => {
    renderWithProviders(<BodyLanguageTranslator />);
    
    // Switch to text-to-body mode and try to translate without input
    const textToBodyButton = screen.getByText('Text → Body Language');
    fireEvent.click(textToBodyButton);
    
    const translateButton = screen.getByText('Translate to Body Language');
    fireEvent.click(translateButton);
    
    // Should show error message
    expect(screen.getByText('Please enter some text to translate')).toBeInTheDocument();
  });
});

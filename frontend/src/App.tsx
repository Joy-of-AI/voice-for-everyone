import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Container } from '@mui/material';

// Import components
import Header from './components/Header';
import BodyLanguageTranslator from './components/BodyLanguageTranslator';
import RealTimeTranslation from './components/RealTimeTranslation';
import Settings from './components/Settings';
import History from './components/History';
import About from './components/About';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
          <Header />
          <Container maxWidth="xl" sx={{ py: 3 }}>
            <Routes>
              <Route path="/" element={<BodyLanguageTranslator />} />
              <Route path="/realtime" element={<RealTimeTranslation />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/history" element={<History />} />
              <Route path="/about" element={<About />} />
            </Routes>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;

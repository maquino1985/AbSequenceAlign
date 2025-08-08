
import { useState, useMemo } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container, Box } from '@mui/material';
import { ModuleProvider } from './modules/shared/context/ModuleContext';
import { MODULES } from './modules/moduleRegistry';
import { useModuleContext } from './modules/shared/context/ModuleContext';
import { ModernNavigation } from './components/ModernNavigation';

// Create theme function that accepts mode
const createAppTheme = (mode: 'light' | 'dark') => createTheme({
  palette: {
    mode,
    primary: {
      main: mode === 'dark' ? '#90caf9' : '#1976d2',
      dark: mode === 'dark' ? '#42a5f5' : '#1565c0',
      light: mode === 'dark' ? '#e3f2fd' : '#42a5f5',
    },
    secondary: {
      main: mode === 'dark' ? '#f48fb1' : '#dc004e',
    },
    background: {
      default: mode === 'dark' ? '#121212' : '#f8fafc',
      paper: mode === 'dark' ? '#1e1e1e' : '#ffffff',
    },
    text: {
      primary: mode === 'dark' ? '#ffffff' : '#1a202c',
      secondary: mode === 'dark' ? '#b0b0b0' : '#4a5568',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 700,
      letterSpacing: '-0.025em',
    },
    h6: {
      fontWeight: 600,
      letterSpacing: '-0.0125em',
    },
    body1: {
      letterSpacing: '-0.0125em',
    },
    body2: {
      letterSpacing: '-0.0125em',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: mode === 'dark' 
            ? '0 4px 20px rgba(0,0,0,0.3)' 
            : '0 4px 20px rgba(0,0,0,0.08)',
          borderRadius: 16,
          border: mode === 'dark' ? '1px solid rgba(255,255,255,0.1)' : 'none',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 10,
          fontWeight: 600,
          padding: '10px 24px',
        },
        contained: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
            transform: 'translateY(-1px)',
          },
          transition: 'all 0.2s ease-in-out',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
          },

        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: mode === 'dark' ? '#1e1e1e' : '#ffffff',
          color: mode === 'dark' ? '#ffffff' : '#1a202c',
          boxShadow: mode === 'dark' 
            ? '0 1px 3px rgba(0,0,0,0.4)' 
            : '0 1px 3px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

const AppContent: React.FC = () => {
  const { getCurrentModule } = useModuleContext();
  const currentModule = getCurrentModule();
  
  if (!currentModule) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome to AbSequenceAlign
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Please select a module from the navigation bar to begin.
        </Typography>
      </Container>
    );
  }

  const ModuleComponent = currentModule.component;
  
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <ModuleComponent />
    </Container>
  );
};

function App() {
  const [darkMode, setDarkMode] = useState(false);
  
  const theme = useMemo(() => createAppTheme(darkMode ? 'dark' : 'light'), [darkMode]);
  
  const handleThemeToggle = () => {
    setDarkMode(!darkMode);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ModuleProvider modules={MODULES} defaultModule="antibody-annotation">
        <Box sx={{ flexGrow: 1, minHeight: '100vh' }}>
          <ModernNavigation darkMode={darkMode} onThemeToggle={handleThemeToggle} />
          <AppContent />
        </Box>
      </ModuleProvider>
    </ThemeProvider>
  );
}

export default App;

import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import InvoiceList from './components/InvoiceList';
import InvoiceDetail from './components/InvoiceDetail';
import Container from '@mui/material/Container';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import { checkBackendHealth } from './services/api';
import './App.css';

// Création d'un thème personnalisé
const theme = createTheme({
  palette: {
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
    fontFamily: [
      'Roboto',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

function App() {
  const [backendStatus, setBackendStatus] = useState({
    checked: false,
    online: false,
    error: null
  });

  useEffect(() => {
    const checkBackend = async () => {
      try {
        await checkBackendHealth();
        setBackendStatus({
          checked: true,
          online: true,
          error: null
        });
      } catch (error) {
        setBackendStatus({
          checked: true,
          online: false,
          error: 'Impossible de se connecter au serveur backend'
        });
      }
    };

    checkBackend();
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div className="App">
          <Navbar />
          <Container component="main" sx={{ pt: 3, pb: 6 }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/invoices" element={<InvoiceList />} />
              <Route path="/invoices/:id" element={<InvoiceDetail />} />
            </Routes>
          </Container>
          
          {/* Alerte en cas de problème de connexion au backend */}
          <Snackbar 
            open={backendStatus.checked && !backendStatus.online} 
            anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
          >
            <Alert severity="error" variant="filled">
              {backendStatus.error || 'Erreur de connexion au serveur'}. Vérifiez que le backend est démarré.
            </Alert>
          </Snackbar>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
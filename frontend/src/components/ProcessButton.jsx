import React, { useState } from 'react';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { processInvoices } from '../services/api';

const ProcessButton = ({ onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info'
  });

  const handleProcess = async () => {
    setLoading(true);
    try {
      const result = await processInvoices();
      setSnackbar({
        open: true,
        message: `${result.processed} factures traitées avec succès !`,
        severity: 'success'
      });
      if (onSuccess) onSuccess();
    } catch (error) {
      setSnackbar({
        open: true,
        message: `Erreur: ${error.message}`,
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar({
      ...snackbar,
      open: false
    });
  };

  return (
    <>
      <Button
        variant="contained"
        color="primary"
        startIcon={loading ? <CircularProgress size={24} color="inherit" /> : <PlayArrowIcon />}
        onClick={handleProcess}
        disabled={loading}
      >
        {loading ? 'Traitement...' : 'Traiter les factures'}
      </Button>
      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={6000} 
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default ProcessButton;
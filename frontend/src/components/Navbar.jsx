import React from 'react';
import { Link } from 'react-router-dom';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import ReceiptIcon from '@mui/icons-material/Receipt';

const Navbar = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <ReceiptIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          OCR Factures
        </Typography>
        <Box>
          <Link to="/" style={{ color: 'white', textDecoration: 'none', marginRight: '20px' }}>
            Tableau de bord
          </Link>
          <Link to="/invoices" style={{ color: 'white', textDecoration: 'none' }}>
            Factures
          </Link>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
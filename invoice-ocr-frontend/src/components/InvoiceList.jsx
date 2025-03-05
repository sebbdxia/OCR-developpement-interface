import React, { useState, useEffect } from 'react';
import { getInvoices } from '../services/api';
import InvoiceCard from './InvoiceCard';
import ProcessButton from './ProcessButton';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import SearchIcon from '@mui/icons-material/Search';
import Grid from '@mui/material/Grid';

const InvoiceList = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const data = await getInvoices();
      setInvoices(data.invoices || []);
      setError(null);
    } catch (error) {
      setError('Erreur lors du chargement des factures');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  // Filtrer les factures en fonction du terme de recherche
  const filteredInvoices = invoices.filter(invoice => {
    const searchLower = searchTerm.toLowerCase();
    return (
      (invoice.invoiceNumber && invoice.invoiceNumber.toLowerCase().includes(searchLower)) ||
      (invoice.recipient && invoice.recipient.toLowerCase().includes(searchLower)) ||
      (invoice.totalAmount && invoice.totalAmount.toString().includes(searchTerm))
    );
  });

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Liste des factures
        </Typography>
        <ProcessButton onSuccess={fetchInvoices} />
      </Box>

      <TextField
        fullWidth
        margin="normal"
        variant="outlined"
        placeholder="Rechercher par numéro, destinataire ou montant..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
        sx={{ mb: 3 }}
      />

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : filteredInvoices.length === 0 ? (
        <Alert severity="info">
          {searchTerm 
            ? "Aucune facture ne correspond à votre recherche" 
            : "Aucune facture n'a été traitée. Cliquez sur 'Traiter les factures' pour commencer."}
        </Alert>
      ) : (
        <Grid container spacing={2}>
          {filteredInvoices.map(invoice => (
            <Grid item xs={12} key={invoice._id}>
              <InvoiceCard invoice={invoice} />
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default InvoiceList;
import React, { useState, useEffect } from 'react';
import { getInvoices } from '../services/api';
import ProcessButton from './ProcessButton';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import { Link } from 'react-router-dom';
import ReceiptIcon from '@mui/icons-material/Receipt';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import AssessmentIcon from '@mui/icons-material/Assessment';
import ErrorIcon from '@mui/icons-material/Error';
import Divider from '@mui/material/Divider';

const Dashboard = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalInvoices: 0,
    totalAmount: 0,
    averageQuality: 0,
    lowQualityCount: 0
  });

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const data = await getInvoices();
      const invoicesList = data.invoices || [];
      setInvoices(invoicesList);
      
      // Calculer les statistiques
      const totalAmount = invoicesList.reduce((sum, invoice) => 
        sum + (invoice.totalAmount || 0), 0);
      
      const qualityScores = invoicesList
        .filter(inv => inv.qualityMetrics?.overallScore !== undefined)
        .map(inv => inv.qualityMetrics.overallScore);
      
      const averageQuality = qualityScores.length > 0 
        ? qualityScores.reduce((sum, score) => sum + score, 0) / qualityScores.length 
        : 0;
      
      const lowQualityCount = invoicesList.filter(inv => 
        inv.qualityMetrics?.overallScore !== undefined && 
        inv.qualityMetrics.overallScore < 0.7
      ).length;
      
      setStats({
        totalInvoices: invoicesList.length,
        totalAmount,
        averageQuality,
        lowQualityCount
      });
      
      setError(null);
    } catch (error) {
      setError('Erreur lors du chargement des données');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  // Récupérer les 5 dernières factures traitées
  const recentInvoices = [...invoices]
    .sort((a, b) => new Date(b.processingDate) - new Date(a.processingDate))
    .slice(0, 5);

  if (loading) {
    return (
      <Container sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  // Format de date pour l'affichage
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Tableau de bord OCR Factures
        </Typography>
        <ProcessButton onSuccess={fetchInvoices} />
      </Box>

      {invoices.length === 0 ? (
        <Alert severity="info" sx={{ my: 3 }}>
          Aucune facture n'a été traitée. Cliquez sur 'Traiter les factures' pour commencer.
        </Alert>
      ) : (
        <>
          {/* Statistiques */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper 
                sx={{ 
                  p: 3, 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <ReceiptIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h4" component="div">
                  {stats.totalInvoices}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Factures traitées
                </Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Paper 
                sx={{ 
                  p: 3, 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <AttachMoneyIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h4" component="div">
                  {stats.totalAmount.toFixed(2)}€
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Montant total
                </Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Paper 
                sx={{ 
                  p: 3, 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <Box sx={{ position: 'relative', display: 'inline-flex', mb: 1 }}>
                  <CircularProgress 
                    variant="determinate" 
                    value={stats.averageQuality * 100} 
                    size={60}
                    color={stats.averageQuality >= 0.7 ? "success" : "warning"}
                  />
                  <Box
                    sx={{
                      top: 0,
                      left: 0,
                      bottom: 0,
                      right: 0,
                      position: 'absolute',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography variant="caption" component="div" color="text.secondary">
                      {`${(stats.averageQuality * 100).toFixed(0)}%`}
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Qualité moyenne OCR
                </Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Paper 
                sx={{ 
                  p: 3, 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <ErrorIcon color="error" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h4" component="div">
                  {stats.lowQualityCount}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Factures à réviser
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          {/* Factures récentes */}
          <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 4 }}>
            Factures récentes
          </Typography>
          
          <Paper sx={{ mb: 4 }}>
            <Box sx={{ p: 2 }}>
              {recentInvoices.length > 0 ? (
                <Box>
                  {recentInvoices.map((invoice, index) => (
                    <Box key={invoice._id} sx={{ py: 1 }}>
                      <Grid container alignItems="center">
                        <Grid item xs={4} sm={3}>
                          <Typography variant="body2">
                            {invoice.invoiceNumber || 'Numéro inconnu'}
                          </Typography>
                        </Grid>
                        <Grid item xs={3} sm={3}>
                          <Typography variant="body2" color="text.secondary">
                            {invoice.recipient || 'Non spécifié'}
                          </Typography>
                        </Grid>
                        <Grid item xs={3} sm={3}>
                          <Typography variant="body2" color="text.secondary">
                            {invoice.totalAmount 
                              ? `${invoice.totalAmount.toFixed(2)} ${invoice.currency || '€'}` 
                              : 'N/A'}
                          </Typography>
                        </Grid>
                        <Grid item xs={2} sm={2}>
                          <CircularProgress 
                            variant="determinate" 
                            value={(invoice.qualityMetrics?.overall
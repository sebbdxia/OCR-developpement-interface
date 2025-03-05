import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getInvoiceById } from '../services/api';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Grid from '@mui/material/Grid';
import Divider from '@mui/material/Divider';
import Chip from '@mui/material/Chip';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import LinearProgress from '@mui/material/LinearProgress';

const InvoiceDetail = () => {
  const { id } = useParams();
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInvoice = async () => {
      setLoading(true);
      try {
        const data = await getInvoiceById(id);
        setInvoice(data.invoice);
        setError(null);
      } catch (error) {
        setError('Erreur lors du chargement de la facture');
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchInvoice();
  }, [id]);

  // Format de date pour l'affichage
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <Container sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error || !invoice) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">
          {error || "La facture n'a pas pu être chargée"}
        </Alert>
        <Button 
          component={Link} 
          to="/invoices" 
          startIcon={<ArrowBackIcon />}
          sx={{ mt: 2 }}
        >
          Retour à la liste
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Button 
        component={Link} 
        to="/invoices" 
        startIcon={<ArrowBackIcon />}
        sx={{ mb: 2 }}
      >
        Retour à la liste
      </Button>

      <Typography variant="h4" component="h1" gutterBottom>
        Facture {invoice.invoiceNumber || 'Sans numéro'}
      </Typography>

      <Grid container spacing={3}>
        {/* Informations principales */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Informations générales
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Typography variant="subtitle2">Numéro:</Typography>
              </Grid>
              <Grid item xs={8}>
                <Typography>{invoice.invoiceNumber || 'Non spécifié'}</Typography>
              </Grid>

              <Grid item xs={4}>
                <Typography variant="subtitle2">Date:</Typography>
              </Grid>
              <Grid item xs={8}>
                <Typography>{formatDate(invoice.date)}</Typography>
              </Grid>

              <Grid item xs={4}>
                <Typography variant="subtitle2">Destinataire:</Typography>
              </Grid>
              <Grid item xs={8}>
                <Typography>{invoice.recipient || 'Non spécifié'}</Typography>
              </Grid>

              <Grid item xs={4}>
                <Typography variant="subtitle2">Adresse:</Typography>
              </Grid>
              <Grid item xs={8}>
                <Typography>{invoice.address || 'Non spécifiée'}</Typography>
              </Grid>

              <Grid item xs={4}>
                <Typography variant="subtitle2">Montant total:</Typography>
              </Grid>
              <Grid item xs={8}>
                <Typography>
                  {invoice.totalAmount 
                    ? `${invoice.totalAmount.toFixed(2)} ${invoice.currency || ''}` 
                    : 'Non spécifié'}
                </Typography>
              </Grid>

              <Grid item xs={4}>
                <Typography variant="subtitle2">Date de traitement:</Typography>
              </Grid>
              <Grid item xs={8}>
                <Typography>{formatDate(invoice.processingDate)}</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Métriques de qualité */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Métriques de qualité
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {invoice.qualityMetrics ? (
              <>
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="subtitle2">Score global:</Typography>
                    <Chip 
                      icon={invoice.qualityMetrics.overallScore >= 0.7 ? <CheckCircleIcon /> : <ErrorIcon />}
                      label={`${(invoice.qualityMetrics.overallScore * 100).toFixed(0)}%`}
                      color={invoice.qualityMetrics.overallScore >= 0.7 ? 'success' : invoice.qualityMetrics.overallScore >= 0.5 ? 'warning' : 'error'}
                    />
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={invoice.qualityMetrics.overallScore * 100} 
                    color={invoice.qualityMetrics.overallScore >= 0.7 ? 'success' : invoice.qualityMetrics.overallScore >= 0.5 ? 'warning' : 'error'}
                  />
                </Box>

                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" gutterBottom>Complétude:</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={invoice.qualityMetrics.completeness * 100} 
                    color="primary"
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="caption">
                    {(invoice.qualityMetrics.completeness * 100).toFixed(0)}% des champs obligatoires ont été extraits
                  </Typography>
                </Box>

                <Box>
                  <Typography variant="subtitle2" gutterBottom>Cohérence:</Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={invoice.qualityMetrics.consistency * 100} 
                    color="primary"
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="caption">
                    {(invoice.qualityMetrics.consistency * 100).toFixed(0)}% de cohérence entre les données extraites
                  </Typography>
                </Box>
              </>
            ) : (
              <Alert severity="warning">Aucune métrique de qualité disponible</Alert>
            )}
          </Paper>
        </Grid>

        {/* Éléments de la facture */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Éléments de la facture
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {invoice.items && invoice.items.length > 0 ? (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Description</TableCell>
                      <TableCell align="right">Quantité</TableCell>
                      <TableCell align="right">Prix unitaire</TableCell>
                      <TableCell align="right">Montant</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {invoice.items.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>{item.description || 'Non spécifié'}</TableCell>
                        <TableCell align="right">{item.quantity || '1'}</TableCell>
                        <TableCell align="right">
                          {item.unitPrice ? `${item.unitPrice.toFixed(2)} ${invoice.currency || ''}` : 'N/A'}
                        </TableCell>
                        <TableCell align="right">
                          {item.amount ? `${item.amount.toFixed(2)} ${invoice.currency || ''}` : 'N/A'}
                        </TableCell>
                      </TableRow>
                    ))}
                    <TableRow>
                      <TableCell colSpan={3} align="right" sx={{ fontWeight: 'bold' }}>Total</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                        {invoice.totalAmount 
                          ? `${invoice.totalAmount.toFixed(2)} ${invoice.currency || ''}` 
                          : 'Non spécifié'}
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Alert severity="info">Aucun élément n'a été identifié dans cette facture</Alert>
            )}
          </Paper>
        </Grid>

        {/* Texte brut OCR */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Texte OCR brut
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box 
              sx={{ 
                p: 2, 
                backgroundColor: 'grey.100', 
                borderRadius: 1,
                maxHeight: '250px',
                overflow: 'auto',
                fontFamily: 'monospace',
                whiteSpace: 'pre-wrap',
                fontSize: '0.875rem'
              }}
            >
              {invoice.rawText || 'Aucun texte OCR disponible'}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default InvoiceDetail;
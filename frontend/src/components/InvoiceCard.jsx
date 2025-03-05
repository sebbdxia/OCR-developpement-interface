import React from 'react';
import { Link } from 'react-router-dom';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Chip from '@mui/material/Chip';
import Grid from '@mui/material/Grid';
import VisibilityIcon from '@mui/icons-material/Visibility';

const InvoiceCard = ({ invoice }) => {
  // Format de date pour l'affichage
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  // Déterminer la couleur du chip basée sur le score de qualité
  const getQualityColor = (score) => {
    if (!score && score !== 0) return 'default';
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  return (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>
        <Grid container spacing={2}>
          <Grid item xs={12} md={8}>
            <Typography variant="h6" gutterBottom>
              {invoice.invoiceNumber || 'Numéro inconnu'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>Destinataire:</strong> {invoice.recipient || 'Non spécifié'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>Date:</strong> {formatDate(invoice.date)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              <strong>Montant:</strong> {invoice.totalAmount ? `${invoice.totalAmount.toFixed(2)} ${invoice.currency || ''}` : 'Non spécifié'}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4} sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', justifyContent: 'center' }}>
            <Chip 
              label={`Qualité: ${invoice.qualityMetrics?.overallScore ? (invoice.qualityMetrics.overallScore * 100).toFixed(0) + '%' : 'N/A'}`}
              color={getQualityColor(invoice.qualityMetrics?.overallScore)}
              sx={{ mb: 1 }}
            />
            <Typography variant="caption" color="text.secondary">
              Traité le {formatDate(invoice.processingDate)}
            </Typography>
          </Grid>
        </Grid>
      </CardContent>
      <CardActions>
        <Button 
          component={Link} 
          to={`/invoices/${invoice._id}`} 
          size="small" 
          startIcon={<VisibilityIcon />}
        >
          Voir détails
        </Button>
      </CardActions>
    </Card>
  );
};

export default InvoiceCard;
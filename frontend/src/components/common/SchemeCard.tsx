import React from 'react';
import { Card, CardContent, CardActions, Typography, Button, Chip, Box } from '@mui/material';
import { Scheme } from '../../types/scheme';

interface SchemeCardProps {
  scheme: Scheme;
}

const SchemeCard: React.FC<SchemeCardProps> = ({ scheme }) => {
  return (
    <Card sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      transition: 'transform 0.2s',
      '&:hover': {
        transform: 'translateY(-4px)',
        boxShadow: 4
      }
    }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          {scheme.scheme_name}
        </Typography>
        
        <Box sx={{ mb: 2 }}>
          <Chip 
            label={`Age: ${scheme.min_age ?? 'N/A'} - ${scheme.max_age ?? 'N/A'}`} 
            size="small" 
            sx={{ mr: 1, mb: 1 }}
          />
          <Chip 
            label={`Income Limit: ${scheme.income_limit ?? 'N/A'}`} 
            size="small" 
            sx={{ mr: 1, mb: 1 }}
          />
        </Box>

        <Typography variant="body2" color="text.secondary" paragraph>
          {scheme.scheme_description}
        </Typography>

        <Typography variant="subtitle2" gutterBottom>
          Benefits:
        </Typography>
        <Typography variant="body2" paragraph>
          {scheme.benefits ?? 'N/A'}
        </Typography>
      </CardContent>
      
      <CardActions>
        {scheme.application_link && (
          <Button 
            size="small" 
            color="primary" 
            href={scheme.application_link}
            target="_blank"
            rel="noopener noreferrer"
          >
            Apply Now
          </Button>
        )}
        <Button size="small" color="primary">
          Learn More
        </Button>
      </CardActions>
    </Card>
  );
};

export default SchemeCard;

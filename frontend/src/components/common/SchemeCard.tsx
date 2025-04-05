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
          href={scheme.application_link} 
          target="_blank" 
          rel="noopener noreferrer"
          className="inline-block text-white px-4 py-2 rounded-full text-sm shadow-md transition duration-300"
          >
            Apply Now
          </Button>
        )}
        <button
          className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-full text-sm shadow-md transition duration-300 ml-3"
          >
          Learn More
        </button>
      </CardActions>
    </Card>
  );
};

export default SchemeCard;

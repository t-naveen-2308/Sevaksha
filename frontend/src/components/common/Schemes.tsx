import React, { useEffect, useState } from 'react';
import { Container, Grid, Typography, CircularProgress, Box } from '@mui/material';
import createAxios from '../../utils/createAxios';
import SchemeCard from './SchemeCard';
import { Scheme } from '../../types/scheme';

const Schemes: React.FC = () => {
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchSchemes = async () => {
      try {
        const axiosInstance = createAxios("main");
        const response = await axiosInstance.get<Scheme[]>("/schemes");
        setSchemes(response.data);
      } catch (error) {
        console.error("Failed to fetch schemes:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchSchemes();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom textAlign="center" mb={4}>
        Welfare Schemes
      </Typography>
      
      {schemes.length > 0 ? (
        <Grid container spacing={3}>
          {schemes.map((scheme) => (
            <Grid 
              item 
              xs={12} 
              sm={6} 
              md={4} 
              key={scheme.scheme_id}
              sx={{
              transform: 'scale(1)',
              transition: 'transform 0.2s ease-in-out',
              '&:hover': {
                transform: 'scale(1.03)',
                zIndex: 1
              },
              display: 'flex',
              justifyContent: 'center'
              }}
            >
              <Box sx={{ width: '100%', maxWidth: 345 }}>
              <SchemeCard scheme={scheme} />
              </Box>
            </Grid>
          ))}
        </Grid>
      ) : (
        <Typography variant="h6" textAlign="center">
          No schemes found.
        </Typography>
      )}
    </Container>
  );
};

export default Schemes;

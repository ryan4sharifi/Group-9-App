// Add more functionality/Analytics once we have reports in the DB 
// total hours volunteered, most active volunteers, Viewing Indivual events Etc.
import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Stack,
  Button,
  Box,
} from '@mui/material';
// import axios from 'axios'; 

type ReportData = {
  totalVolunteers: number;
  totalEvents: number;
  totalMatches: number;
};

const ReportPage: React.FC = () => {
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    
    // WHEN BACKEND IS READY:Replace the mock fetch below with an axios call to backend
    
    const timer = setTimeout(() => {
      try {
        // FAKE/MOCK DATA FOR NOW
        const mockData: ReportData = {
          totalVolunteers: 42,
          totalEvents: 15,
          totalMatches: 60,
        };
        setReport(mockData);
      } catch (err) {
        setError('Failed to load mock report data.');
      } finally {
        setLoading(false);
      }
    }, 1000); // Simulated delay

    return () => clearTimeout(timer);
  }, []);

 
  // WHEN BACKEND EXPORT ENDPOINTS ARE READY:Replace these alerts with real axios or window.open calls
  
  const handleExportCSV = () => {
    // Example: window.open('http://localhost:8000/report/export/csv', '_blank');
    alert("Exporting CSV (mock)");
  };

  const handleExportPDF = () => {
    // Example: window.open('http://localhost:8000/report/export/pdf', '_blank');
    alert("Exporting PDF (mock)");
  };

  if (loading) return <CircularProgress sx={{ display: 'block', mx: 'auto', mt: 6 }} />;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        Volunteer & Event Reports
      </Typography>

      
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={3}
        justifyContent="center"
        alignItems="stretch"
        sx={{ mb: 6 }}
      >
        <Box flex={1}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6">Total Volunteers</Typography>
            <Typography variant="h4" color="primary">
              {report?.totalVolunteers ?? 0}
            </Typography>
          </Paper>
        </Box>
        <Box flex={1}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6">Total Events</Typography>
            <Typography variant="h4" color="primary">
              {report?.totalEvents ?? 0}
            </Typography>
          </Paper>
        </Box>
        <Box flex={1}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h6">Total Matches</Typography>
            <Typography variant="h4" color="primary">
              {report?.totalMatches ?? 0}
            </Typography>
          </Paper>
        </Box>
      </Stack>

      {/* Export buttons */}
      <Stack direction="row" spacing={2} justifyContent="center">
        <Button variant="contained" color="primary" onClick={handleExportCSV}>
          Export CSV
        </Button>
        <Button variant="contained" color="secondary" onClick={handleExportPDF}>
          Export PDF
        </Button>
      </Stack>
    </Container>
  );
};

export default ReportPage;

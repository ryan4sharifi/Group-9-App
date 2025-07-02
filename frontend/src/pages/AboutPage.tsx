import React from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Stack,
  Divider,
} from '@mui/material';
import VolunteerActivismIcon from '@mui/icons-material/VolunteerActivism';
import GroupIcon from '@mui/icons-material/Group';
import InsightsIcon from '@mui/icons-material/Insights';

const AboutPage: React.FC = () => {
  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        About Our Volunteer Platform
      </Typography>

      <Typography variant="h6" color="text.secondary" paragraph align="center">
        Empowering communities through meaningful volunteer engagement.
      </Typography>

      <Box sx={{ my: 4 }}>
        <Typography variant="h5" gutterBottom>
          Our Mission
        </Typography>
        <Typography variant="body1">
          We aim to simplify the process of connecting volunteers with impactful events. Our platform streamlines registration, matching, notifications, and reporting, ensuring every volunteer and organizer has the necessary tools to succeed.
        </Typography>
      </Box>

      <Divider sx={{ my: 4 }} />

      <Typography variant="h5" gutterBottom>
        What You Can Do
      </Typography>

      <Stack spacing={3} sx={{ mt: 2 }}>
        <Paper elevation={2} sx={{ p: 3 }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <VolunteerActivismIcon color="primary" fontSize="large" />
            <Box>
              <Typography variant="h6">For Volunteers</Typography>
              <Typography variant="body2" color="text.secondary">
                Create your profile, list your skills, set preferences, and get matched with events tailored to your availability and interests.
              </Typography>
            </Box>
          </Stack>
        </Paper>

        <Paper elevation={2} sx={{ p: 3 }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <GroupIcon color="primary" fontSize="large" />
            <Box>
              <Typography variant="h6">For Administrators</Typography>
              <Typography variant="body2" color="text.secondary">
                Organize events, view volunteer profiles, send notifications, and generate detailed reports for tracking and analysis.
              </Typography>
            </Box>
          </Stack>
        </Paper>

        <Paper elevation={2} sx={{ p: 3 }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <InsightsIcon color="primary" fontSize="large" />
            <Box>
              <Typography variant="h6">Real-Time Insights</Typography>
              <Typography variant="body2" color="text.secondary">
                Use built-in analytics and reporting tools to monitor participation, event success, and volunteer impact.
              </Typography>
            </Box>
          </Stack>
        </Paper>
      </Stack>
    </Container>
  );
};

export default AboutPage;

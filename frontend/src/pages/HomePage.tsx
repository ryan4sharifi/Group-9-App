import React from 'react';
import { Box, Container, Typography, Button, Paper, useTheme, Stack } from '@mui/material';
import {
  PeopleAlt,
  Event,
  Assignment,
  Notifications,
  BarChart,
  History,
  EventAvailable
} from '@mui/icons-material';

import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  const theme = useTheme();

  const featureCards = [
    {
      icon: <PeopleAlt fontSize="large" color="primary" />,
      title: "Volunteer Management",
      description: "Register, track, and manage volunteers effortlessly",
      link: "/profile"
    },
    {
      icon: <Event fontSize="large" color="primary" />,
      title: "Event Coordination",
      description: "Organize and schedule volunteer events with ease",
      link: "/events"
    },
    {
      icon: <Assignment fontSize="large" color="primary" />,
      title: "Task Assignment",
      description: "Assign and monitor tasks for better productivity",
      link: "/match"
    },
    {
      icon: <Notifications fontSize="large" color="primary" />,
      title: "Notifications",
      description: "Stay updated with real-time notifications and alerts",
      link: "/notifications"
    },
    {
      icon: <BarChart fontSize="large" color="primary" />,
      title: "Analytics & Reporting",
      description: "Deep insights into volunteer activities and program success",
      link: "/report"
    },
    {
      icon: <History fontSize="large" color="primary" />,
      title: "History",
      description: "View past volunteer activities and contributions",
      link: "/history"
    },
    {
      icon: <EventAvailable fontSize="large" color="primary" />, 
      title: "Matched Events",
      description: "Find events that match your skills and interests",
      link: "/match"
    }
  ];

  return (
    <Container maxWidth="lg">
      <Box sx={{
        textAlign: 'center',
        py: 8,
        background: `linear-gradient(rgba(255,255,255,0.8), rgba(255,255,255,0.8)), url('/images/volunteers-bg.jpg')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        borderRadius: 2,
        mb: 6
      }}>
        <Typography variant="h2" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
          Volunteer Management Platform
        </Typography>
        <Typography
          variant="h5"
          paragraph
          sx={{
            color: theme.palette.mode === 'dark' ? '#5e5efbff ' : 'text.secondary',
            maxWidth: '800px',
            mx: 'auto',
            mb: 4
          }}
        >
          Streamline your volunteer operations, maximize impact, and build stronger communities together.
        </Typography>


        <Button
          variant="contained"
          size="large"
          component={Link}
          to="/register"
          sx={{ mr: 2 }}
        >
          Get Started
        </Button>
        <Button
          variant="outlined"
          size="large"
          component={Link}
          to="/about"
          sx={{
            backgroundColor: theme.palette.mode === 'dark' ? '#333' : 'transparent',
            color: theme.palette.mode === 'dark' ? '#fff' : 'inherit',
            borderColor: theme.palette.mode === 'dark' ? '#888' : 'inherit',
            '&:hover': {
              backgroundColor: theme.palette.mode === 'dark' ? '#444' : theme.palette.action.hover,
              borderColor: theme.palette.primary.main
            }
          }}
        >
          Learn More
        </Button>

      </Box>

      <Typography variant="h4" component="h2" gutterBottom sx={{ mb: 4, textAlign: 'center' }}>
        Simplify Your Volunteer Program
      </Typography>

      <Box sx={{
              display: 'flex',
        flexWrap: 'wrap',
        gap: 3,
        mb: 8,
        justifyContent: 'center'
            }}>
        {featureCards.map((card, index) => (
          <Paper
            elevation={3}
            key={index}
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              textAlign: 'center',
              transition: 'transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out',
              '&:hover': {
                transform: 'translateY(-5px)',
                boxShadow: theme.shadows[10],
              },
              width: {
                xs: '100%',
                sm: 'calc(50% - 12px)',
                md: 'calc(25% - 18px)'
              },
              minHeight: '240px',
              justifyContent: 'space-between'
            }}
        >
            <Stack spacing={2} alignItems="center">
              <Box>{card.icon}</Box>
              <Typography variant="h6" component="h3">{card.title}</Typography>
              <Typography variant="body2" color="text.secondary">
                {card.description}
              </Typography>
            </Stack>
            <Button component={Link} to={card.link} size="small" sx={{ mt: 2 }}>
              Explore
        </Button>
          </Paper>
        ))}
      </Box>

      <Box
        sx={{
          bgcolor: theme.palette.mode === 'dark' ? 'grey.800' : 'primary.light',
          p: 4,
          borderRadius: 2,
          color: theme.palette.mode === 'dark' ? 'grey.100' : 'white',
          textAlign: 'center',
          mb: 6
        }}
      >

        <Typography variant="h5" component="p" gutterBottom>
          Ready to transform your volunteer management?
        </Typography>
        <Button
          variant="contained"
          color="secondary"
          size="large"
          component={Link}
          to="/contact"
          sx={{ mt: 2 }}
        >
          Contact Us Today
        </Button>
      </Box>
    </Container>
  );
};

export default HomePage;
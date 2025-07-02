// Depending on backend requirements, we can just leave this as is or add more functionality later.
import React, { useState } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  Stack,
  Paper
} from '@mui/material';

const ContactPage: React.FC = () => {
  const [form, setForm] = useState({
    name: '',
    email: '',
    message: ''
  });

  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
  const name = e.target.name;       
  const value = e.target.value;     

  // Create a copy of the existing form state
  const updatedForm = {
    name: form.name,
    email: form.email,
    message: form.message,
  };

  // Update the field that changed
  if (name === "name") {
    updatedForm.name = value;
  } else if (name === "email") {
    updatedForm.email = value;
  } else if (name === "message") {
    updatedForm.message = value;
  }

  
  setForm(updatedForm);
};


  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Simple frontend validation
    if (!form.name || !form.email || !form.message) {
      setError('Please fill in all fields.');
      return;
    }

    // RESET error and simulate submit
    setError(null);
    setSubmitted(true);

    // Simulate API call delay
    setTimeout(() => {
      setForm({ name: '', email: '', message: '' });
    }, 1000);
  };

  return (
    <Container maxWidth="sm" sx={{ py: 6 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        Contact Us
      </Typography>
      <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 4 }}>
        Have questions or feedback? We'd love to hear from you!
      </Typography>

      <Paper elevation={3} sx={{ p: 4 }}>
        <form onSubmit={handleSubmit}>
          <Stack spacing={3}>
            <TextField
              label="Your Name"
              name="name"
              value={form.name}
              onChange={handleChange}
              fullWidth
            />
            <TextField
              label="Your Email"
              name="email"
              value={form.email}
              onChange={handleChange}
              fullWidth
              type="email"
            />
            <TextField
              label="Your Message"
              name="message"
              value={form.message}
              onChange={handleChange}
              fullWidth
              multiline
              minRows={4}
            />

            {error && <Alert severity="error">{error}</Alert>}
            {submitted && !error && (
              <Alert severity="success">Message sent! We'll get back to you soon.</Alert>
            )}

            <Box textAlign="center">
              <Button type="submit" variant="contained" color="primary">
                Send Message
              </Button>
            </Box>
          </Stack>
        </form>
      </Paper>
    </Container>
  );
};

export default ContactPage;

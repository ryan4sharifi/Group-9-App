import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

interface FormWrapperProps {
  title?: string;
  children: React.ReactNode;
  width?: number | string;
}

const FormWrapper: React.FC<FormWrapperProps> = ({
  title,
  children,
  width = 400,
}) => {
  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      bgcolor="#f5f5f5"
    >
      <Paper elevation={3} sx={{ padding: 4, width }}>
        {title && (
          <Typography variant="h5" component="h1" gutterBottom textAlign="center">
            {title}
          </Typography>
        )}
        {children}
      </Paper>
    </Box>
  );
};

export default FormWrapper;
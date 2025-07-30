import React from 'react';
import { Button, CircularProgress, SxProps, Theme } from '@mui/material';

interface SubmitButtonProps {
  label: string;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  fullWidth?: boolean;
  loading?: boolean;
  disabled?: boolean;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  variant?: 'text' | 'outlined' | 'contained';
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  sx?: SxProps<Theme>;
}

const SubmitButton: React.FC<SubmitButtonProps> = ({
  label,
  onClick,
  type = 'submit',
  fullWidth = true,
  loading = false,
  disabled = false,
  startIcon,
  endIcon,
  variant = 'contained',
  color = 'primary',
  sx,
}) => {
  return (
    <Button
      variant={variant}
      color={color}
      onClick={onClick}
      type={type}
      fullWidth={fullWidth}
      disabled={disabled || loading}
      startIcon={startIcon}
      endIcon={endIcon}
      sx={{ mt: 2, ...sx }}
    >
      {loading ? <CircularProgress size={24} color="inherit" /> : label}
    </Button>
  );
};

export default SubmitButton;
// src/components/inputs/InputField.tsx

import React from 'react';
import { TextField } from '@mui/material';

interface InputFieldProps {
  label: string;
  name: string;
  value: string | undefined; // <-- CHANGE 1: Allow value to be undefined
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string;
  required?: boolean;
  fullWidth?: boolean;
  error?: boolean;
  helperText?: string;
  disabled?: boolean;
  placeholder?: string;
  multiline?: boolean;
  rows?: number;
}

const InputField: React.FC<InputFieldProps> = ({
  label,
  name,
  value,
  onChange,
  type = 'text',
  required = false,
  fullWidth = true,
  error = false,
  helperText = '',
  disabled = false,
  placeholder = '',
  multiline = false,
  rows = 1,
}) => {
  return (
    <TextField
      label={label}
      name={name}
      // <-- CHANGE 2: Coalesce value with an empty string to satisfy TextField's prop type
      value={value || ''} 
      onChange={onChange}
      type={type}
      required={required}
      fullWidth={fullWidth}
      error={error}
      helperText={helperText}
      disabled={disabled}
      placeholder={placeholder}
      variant="outlined"
      margin="normal"
      InputLabelProps={{ shrink: type === 'date' || !!value }}
      multiline={multiline}
      rows={multiline ? rows : undefined}
    />
  );
};

export default InputField;
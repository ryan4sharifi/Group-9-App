import React from 'react';
import { Autocomplete, TextField } from '@mui/material'; // Ensure TextField is imported

interface MultiInputFieldProps {
  label: string;
  name: string;
  value: string[];
  onChange: (name: string, value: string[]) => void;
  placeholder?: string;
  options?: string[]; 
  error?: boolean; 
  helperText?: string; 
  required?: boolean; 
}

const MultiInputField: React.FC<MultiInputFieldProps> = ({
  label,
  name,
  value,
  onChange,
  placeholder = '',
  options = [],
  error = false, 
  helperText = '', 
  required = false, 
}) => {
  return (
    <Autocomplete
      multiple
      freeSolo // Allows users to enter options not present in the suggestions list
      options={options} // Provide your list of skill suggestions here
      value={value}
      onChange={(_, newValue) => {
        // Filter out any empty strings that might result from user input (e.g., hitting enter on an empty field)
        const filteredNewValue = newValue.filter(item => item.trim() !== '');
        onChange(name, filteredNewValue);
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          placeholder={placeholder}
          margin="normal"
          fullWidth
        
          error={error}
          helperText={helperText}
          required={required}
          
        />
      )}
    />
  );
};

export default MultiInputField;
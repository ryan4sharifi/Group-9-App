import React from 'react';
import { Autocomplete, TextField } from '@mui/material';

interface MultiInputFieldProps {
  label: string;
  name: string;
  value: string[];
  onChange: (name: string, value: string[]) => void;
  placeholder?: string;
  options?: string[];
}

const MultiInputField: React.FC<MultiInputFieldProps> = ({
  label,
  name,
  value,
  onChange,
  placeholder = '',
  options = [],
}) => {
  return (
    <Autocomplete
      multiple
      freeSolo
      options={options}
      value={value}
      onChange={(_, newValue) => onChange(name, newValue)}
      renderInput={(params) => (
        <TextField {...params} label={label} placeholder={placeholder} margin="normal" />
      )}
    />
  );
};

export default MultiInputField;
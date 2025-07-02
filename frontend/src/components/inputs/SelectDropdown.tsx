import React from 'react';
import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
  FormHelperText,
} from '@mui/material';

interface Option {
  label: string;
  value: string;
}

interface SelectDropdownProps {
  label: string;
  name: string;
  value: string;
  options: Option[];
  onChange: (event: SelectChangeEvent) => void;
  required?: boolean;
  error?: boolean;
  helperText?: string;
  fullWidth?: boolean;
}

const SelectDropdown: React.FC<SelectDropdownProps> = ({
  label,
  name,
  value,
  options,
  onChange,
  required = false,
  error = false,
  helperText = '',
  fullWidth = true,
}) => {
  return (
    <FormControl fullWidth={fullWidth} required={required} error={error} margin="normal">
      <InputLabel>{label}</InputLabel>
      <Select name={name} value={value} onChange={onChange} label={label}>
        {options.map((opt) => (
          <MenuItem key={opt.value} value={opt.value}>
            {opt.label}
          </MenuItem>
        ))}
      </Select>
      {helperText && <FormHelperText>{helperText}</FormHelperText>}
    </FormControl>
  );
};

export default SelectDropdown;
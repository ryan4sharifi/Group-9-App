import React from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  ListItemText,
  OutlinedInput,
  FormHelperText,
  SelectChangeEvent,
} from '@mui/material';

interface Option {
  label: string;
  value: string;
}

interface MultiSelectProps {
  label: string;
  name: string;
  value: string[];
  onChange: (event: SelectChangeEvent<string[]>) => void;
  options: Option[];
  required?: boolean;
  error?: boolean;
  helperText?: string;
  fullWidth?: boolean;
}

const MultiSelect: React.FC<MultiSelectProps> = ({
  label,
  name,
  value,
  onChange,
  options,
  required = false,
  error = false,
  helperText = '',
  fullWidth = true,
}) => {
  return (
    <FormControl fullWidth={fullWidth} required={required} error={error} margin="normal">
      <InputLabel>{label}</InputLabel>
      <Select
        multiple
        name={name}
        value={value}
        onChange={onChange}
        input={<OutlinedInput label={label} />}
        renderValue={(selected) => selected.join(', ')}
      >
        {options.map((option) => (
          <MenuItem key={option.value} value={option.value}>
            <Checkbox checked={value.includes(option.value)} />
            <ListItemText primary={option.label} />
          </MenuItem>
        ))}
      </Select>
      {helperText && <FormHelperText>{helperText}</FormHelperText>}
    </FormControl>
  );
};

export default MultiSelect;
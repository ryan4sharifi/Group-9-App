import React from 'react';
import { TextField } from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

interface DatePickerFieldProps {
  label: string;
  value: Date | null;
  onChange: (date: Date | null) => void;
  required?: boolean;
  disablePast?: boolean;
  fullWidth?: boolean;
  helperText?: string;
}

const DatePickerField: React.FC<DatePickerFieldProps> = ({
  label,
  value,
  onChange,
  required = false,
  disablePast = false,
  fullWidth = true,
  helperText = '',
}) => {
  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <DatePicker
        label={label}
        value={value}
        onChange={onChange}
        disablePast={disablePast}
        slotProps={{
          textField: {
            required,
            fullWidth,
            helperText,
          } as any,
        }}
      />
    </LocalizationProvider>
  );
};

export default DatePickerField;
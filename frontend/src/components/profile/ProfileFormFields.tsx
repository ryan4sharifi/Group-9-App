// frontend/src/components/profile/ProfileFormFields.tsx
import React from 'react';
import { Box, Autocomplete, TextField } from '@mui/material';
import InputField from '../inputs/InputField';
import MultiInputField from '../inputs/MultiInputField';
import DatePickerField from '../inputs/DatePickerField';

import usStates from '../../data/usStates.json';
import { FieldConfig, FormData, FormErrors, FormHandlers } from '../../interfaces/profile';


interface ProfileFormFieldsProps extends FormHandlers {
    fields: FieldConfig[];
    formData: FormData;
    errors: FormErrors;
    isMobile: boolean;
}

const ProfileFormFields: React.FC<ProfileFormFieldsProps> = ({
    fields,
    formData,
    errors,
    handleChange,
    handleArrayChange,
    handleStateChange,
    handleDateChange,
    isMobile,
}) => {
    return (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
            {fields.map((fieldConfig) => {
                // Fix for TS7053: Cast formData and errors for dynamic indexing
                const fieldName = fieldConfig.name as keyof FormData; // Use keyof FormData for type safety
                const value = formData[fieldName];
                const error = errors[fieldName]; // errors now has index signature

                const label = fieldConfig.label;

                let boxWidth = '100%';
                if (fieldConfig.component !== 'multiInput' && fieldConfig.component !== 'autocomplete' && !fieldConfig.multiline && !isMobile) {
                    boxWidth = 'calc(50% - 12px)';
                } else if (isMobile) {
                    boxWidth = '100%';
                } else {
                    boxWidth = '100%';
                }

                let fieldComponent;

                switch (fieldConfig.component) {
                    case 'input':
                        fieldComponent = (
                            <InputField
                                name={fieldName as string} // name prop typically expects string
                                label={label}
                                value={(value ?? "") as string} // Ensure value is string
                                onChange={handleChange}
                                fullWidth
                                error={!!error}
                                helperText={error}
                                type={fieldConfig.type || 'text'}
                                multiline={fieldConfig.multiline}
                                rows={fieldConfig.rows}
                                required={fieldConfig.required}
                            />
                        );
                        break;
                    case 'multiInput':
                        fieldComponent = (
                            <MultiInputField
                                label={label}
                                name={fieldName as string} // name prop typically expects string
                                value={(value as string[]) || []} // Ensure value is string array
                                onChange={handleArrayChange}
                                error={!!error}
                                helperText={error}
                                required={fieldConfig.required}
                                // Fix for TS2322: MultiInputField's options prop typically expects string[] for skill suggestions
                                // If you have predefined skills to suggest, pass them as string[]
                                options={fieldConfig.options ? fieldConfig.options.map(opt => opt.value) : undefined}
                                // OR if MultiInputField can take {label, value} objects for options, adjust its interface
                                // For now, assuming it expects string[] for options
                            />
                        );
                        break;
                    case 'autocomplete': // Used for state dropdown
                        fieldComponent = (
                            <Autocomplete
                                options={fieldConfig.options || []}
                                getOptionLabel={(option: any) => option.label || option.value || ''} // Ensure label extraction
                                // Ensure value is correctly mapped to an option object for Autocomplete
                                value={usStates.find(state => state.value === value) || null}
                                onChange={handleStateChange}
                                renderInput={(params) => (
                                    <TextField
                                        {...params}
                                        label={label}
                                        margin="normal"
                                        fullWidth
                                        error={!!error}
                                        helperText={error}
                                        required={fieldConfig.required}
                                    />
                                )}
                            />
                        );
                        break;
                    case 'datePicker':
                        fieldComponent = (
                            <DatePickerField
                                label={label}
                                value={value ? new Date(value as string) : null} // Ensure value is Date object or null
                                onChange={handleDateChange}
                                error={!!error}
                                helperText={error}
                                required={fieldConfig.required}
                                // Example: disablePast can be configured in FieldConfig if needed, or default from DatePickerField
                                // disablePast={fieldConfig.name === 'availability' ? false : true}
                            />
                        );
                        break;
                    default:
                        fieldComponent = null;
                }

                return (
                    <Box key={fieldName} sx={{ width: boxWidth }}>
                        {fieldComponent}
                    </Box>
                );
            })}
        </Box>
    );
};

export default ProfileFormFields;
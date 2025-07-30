// frontend/src/components/profile/VolunteerDetailsForm.tsx
import React from 'react';
import ProfileFormFields from './ProfileFormFields'; // Path relative to this component
import { FieldConfig, FormData, FormErrors, FormHandlers } from '../../interfaces/profile'; // Import interfaces
import usStates from '../../data/usStates.json'; // Ensure this path is correct

interface VolunteerDetailsFormProps extends FormHandlers {
    formData: FormData;
    errors: FormErrors;
    isMobile: boolean;
}

const VolunteerDetailsForm: React.FC<VolunteerDetailsFormProps> = ({
    formData,
    errors,
    handleChange,
    handleArrayChange,
    handleStateChange,
    handleDateChange, // Pass this down
    isMobile,
}) => {
    // Define field configurations for Volunteers
    const volunteerFieldsConfig: FieldConfig[] = [
        { name: 'full_name', label: 'Full Name', component: 'input', type: 'text', required: true },
        { name: 'address1', label: 'Address Line 1', component: 'input', type: 'text' },
        { name: 'address2', label: 'Address Line 2', component: 'input', type: 'text' },
        { name: 'city', label: 'City', component: 'input', type: 'text' },
        { name: 'state', label: 'State', component: 'autocomplete', options: usStates },
        { name: 'zip_code', label: 'Zip Code', component: 'input', type: 'text' },
        { name: 'skills', label: 'Your Skills', component: 'multiInput', required: true },
        { name: 'availability', label: 'Availability', component: 'datePicker' }, // Use datePicker component
        { name: 'preferences', label: 'Preferences', component: 'input', type: 'text', multiline: true, rows: 3 },
    ];

    return (
        <ProfileFormFields
            fields={volunteerFieldsConfig}
            formData={formData}
            errors={errors}
            handleChange={handleChange}
            handleArrayChange={handleArrayChange}
            handleStateChange={handleStateChange}
            handleDateChange={handleDateChange} // Pass handleDateChange
            isMobile={isMobile}
        />
    );
};

export default VolunteerDetailsForm;
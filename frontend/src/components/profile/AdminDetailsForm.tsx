// frontend/src/components/profile/AdminDetailsForm.tsx
import React from 'react';
import ProfileFormFields from './ProfileFormFields'; // Path relative to this component
import { FieldConfig, FormData, FormErrors, FormHandlers } from '../../interfaces/profile'; // Import interfaces

interface AdminDetailsFormProps extends FormHandlers {
    formData: FormData;
    errors: FormErrors;
    isMobile: boolean;
}

const AdminDetailsForm: React.FC<AdminDetailsFormProps> = ({
    formData,
    errors,
    handleChange,
    handleArrayChange, // Admin might not have array fields, but keep for handler consistency
    handleStateChange, // Admin might not have state field, but keep for handler consistency
    handleDateChange, // Admin might not have date field, but keep for handler consistency
    isMobile,
}) => {
    // Define field configurations for Admins
    const adminFieldsConfig: FieldConfig[] = [
        { name: 'full_name', label: 'Full Name', component: 'input', type: 'text', required: true },
        { name: 'preferences', label: 'Preferences', component: 'input', type: 'text', multiline: true, rows: 3 },
        // Add any admin-specific fields here if they exist in FormData
        // Example: { name: 'office_location', label: 'Office Location', component: 'input', type: 'text' },
    ];

    return (
        <ProfileFormFields
            fields={adminFieldsConfig}
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

export default AdminDetailsForm;
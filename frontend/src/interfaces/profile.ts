// frontend/src/interfaces/profile.ts

// Type for the main form data
export interface FormData {
    full_name?: string;
    address1?: string;
    address2?: string;
    city?: string;
    state?: string;
    zip_code?: string;
    email?: string; // Read-only, but part of fetched data
    preferences?: string;
    skills: string[];
    availability?: string;
}

// Type for validation errors
export interface FormErrors {
    full_name?: string;
    address1?: string;
    address2?: string;
    city?: string;
    state?: string;
    zip_code?: string;
    email?: string;
    preferences?: string;
    skills?: string;
    availability?: string;
    // Add an index signature to allow dynamic access in ProfileFormFields
    [key: string]: string | undefined;
}

// Type for a single field's configuration for dynamic rendering
export interface FieldConfig {
    name: keyof FormData; // The key from FormData
    label: string;
    component: 'input' | 'multiInput' | 'autocomplete' | 'datePicker'; // Type of custom input component
    type?: string; // HTML input type (e.g., 'text', 'email', 'password', 'date') for InputField
    options?: { label: string; value: string }[]; // For autocomplete/dropdowns (like states)
    required?: boolean; // For visual indication and client-side validation
    multiline?: boolean; // For textareas
    rows?: number; // For textareas
}

// Type for common handlers to pass down to form field components
export interface FormHandlers {
    handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    handleArrayChange: (name: string, values: string[]) => void;
    handleStateChange: (event: React.SyntheticEvent, value: { label: string; value: string } | null) => void;
    handleDateChange: (date: Date | null) => void; // If using DatePickerField
}
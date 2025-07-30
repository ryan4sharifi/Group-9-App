// frontend/src/components/common/ProfileActions.tsx
import React from 'react';
import { Box, useMediaQuery } from '@mui/material'; // Removed 'Button'
import { Save as SaveIcon, Delete as DeleteIcon } from '@mui/icons-material';
import SubmitButton from '../buttons/SubmitButton';

interface ProfileActionsProps {
    isSaving: boolean;
    onSave: () => void;
    onDelete: () => void;
}

const ProfileActions: React.FC<ProfileActionsProps> = ({ isSaving, onSave, onDelete }) => {
    const isMobile = useMediaQuery('(max-width:600px)');

    return (
        <Box mt={4} display="flex" gap={2} flexDirection={isMobile ? 'column' : 'row'} justifyContent="space-between">
            <SubmitButton
                label="Save Profile"
                onClick={onSave}
                disabled={isSaving}
                startIcon={<SaveIcon />}
                sx={{ flex: 3, py: 1.2 }}
            />
            <SubmitButton
                label="Delete Profile"
                onClick={onDelete}
                variant="outlined"
                color="error"
                startIcon={<DeleteIcon />}
                disabled={isSaving}
                sx={{ flex: 1, py: 1.2 }}
            />
        </Box>
    );
};

export default ProfileActions;
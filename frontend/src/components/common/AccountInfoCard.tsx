// frontend/src/components/common/AccountInfoCard.tsx
import React from 'react';
import { Box, Typography, Paper, Divider, useTheme, useMediaQuery } from "@mui/material";
import { BusinessCenter as BusinessIcon } from "@mui/icons-material";

interface AccountInfoCardProps {
    email?: string;
    lastUpdated: string;
    userRole?: string | null; // <--- CHANGED: Allow null
}

const AccountInfoCard: React.FC<AccountInfoCardProps> = ({ email, lastUpdated, userRole }) => {
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

    return (
        <Paper elevation={2} sx={{ p: 3, borderRadius: 2, background: theme.palette.mode === 'dark' ? theme.palette.grey[800] : theme.palette.grey[50] }}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
                <BusinessIcon color="primary" />
                <Typography variant="h6" color="text.primary">Account Information</Typography>
            </Box>
            <Divider sx={{ mb: 2 }} />
            <Box sx={{ display: 'flex', flexDirection: isMobile ? 'column' : 'row', gap: isMobile ? 2 : 4, justifyContent: 'space-between' }}>
                <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle2" color="text.secondary">Email Address</Typography>
                    <Typography variant="body1" fontWeight="medium" mb={1}>{email || "Not available"}</Typography>
                </Box>
                <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle2" color="text.secondary">Last Updated</Typography>
                    <Typography variant="body1" fontWeight="medium">{lastUpdated}</Typography>
                </Box>
                <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle2" color="text.secondary">Role</Typography>
                    <Typography variant="body1" fontWeight="medium">{userRole || "Not available"}</Typography>
                </Box>
            </Box>
        </Paper>
    );
};

export default AccountInfoCard;
// src/pages/NotificationPage.tsx
import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import {
  Container,
  Typography,
  CircularProgress,
  Alert,
  Box,
  Stack,
  Paper,
  IconButton,
  Tooltip,
  Chip,
  Snackbar, // Added Snackbar for consistent feedback
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import DoneIcon from "@mui/icons-material/Done";
import { useUser } from "../context/UserContext";

interface Notification {
  id: string;
  user_id: string;
  message: string;
  created_at: string;
  is_read: boolean;
  event_id?: string; // Added as per your schema (is_nullable: YES)
}

const NotificationPage: React.FC = () => {
  const { userId } = useUser();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState({ success: "", error: "" }); // Combined status for Snackbar
  const [snackbarOpen, setSnackbarOpen] = useState(false); // Snackbar control

  const fetchNotifications = useCallback(async () => {
    setLoading(true);
    setStatus({ success: "", error: "" }); // Clear previous status
    try {
      if (!userId) {
        setStatus({ success: "", error: "User ID is missing. Please log in." });
        return;
      }
      const res = await axios.get(`http://localhost:8000/api/notifications/${userId}`);
      // Ensure data structure matches Notification interface, including event_id if present
      setNotifications(res.data.notifications || []);
    } catch (err) {
      console.error("Failed to load notifications:", err);
      setStatus({ success: "", error: "Failed to load notifications." });
    } finally {
      setLoading(false);
      setSnackbarOpen(true); // Open Snackbar even for fetch errors
    }
  }, [userId]);

  const markAsRead = async (id: string) => {
    setStatus({ success: "", error: "" }); // Clear previous status
    try {
      await axios.put(`http://localhost:8000/api/notifications/${id}/read`);
      setNotifications(prev =>
        prev.map(n => (n.id === id ? { ...n, is_read: true } : n))
      );
      setStatus({ success: "Notification marked as read.", error: "" });
    } catch (err) {
      console.error("Failed to mark as read:", err);
      setStatus({ success: "", error: "Failed to mark as read." });
    } finally {
      setSnackbarOpen(true);
    }
  };

  const handleDelete = async (id: string) => {
    setStatus({ success: "", error: "" }); // Clear previous status
    try {
      await axios.delete(`http://localhost:8000/api/notifications/${id}`);
      setNotifications(prev => prev.filter(n => n.id !== id));
      setStatus({ success: "Notification deleted successfully.", error: "" });
    } catch (err) {
      console.error("Failed to delete notification:", err);
      setStatus({ success: "", error: "Failed to delete notification." });
    } finally {
      setSnackbarOpen(true);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchNotifications();
    } else {
      setLoading(false);
      setStatus({ success: "", error: "User not logged in." });
      setSnackbarOpen(true);
    }
  }, [fetchNotifications, userId]);

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" mb={3}>Notifications</Typography>

      {loading ? (
        <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
        </Box>
      ) : (
        <>
        {notifications.length === 0 ? (
          <Paper sx={{ p: 3, textAlign: "center", bgcolor: "background.default", boxShadow: 1, borderRadius: 2 }}>
            <Typography variant="body1" color="text.secondary">
              No notifications found.
            </Typography>
          </Paper>
        ) : (
          <Stack spacing={2}>
            {notifications.map(notification => (
              <Paper
                key={notification.id}
                elevation={3}
                sx={{
                  p: 2,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  borderRadius: 2,
                  // Visually distinguish unread notifications
                  bgcolor: notification.is_read ? 'background.paper' : theme => theme.palette.action.selected,
                }}
              >
                <Box>
                  <Typography variant="body1" fontWeight={notification.is_read ? 'normal' : 'bold'}>
                    {notification.message}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {new Date(notification.created_at).toLocaleString()}
                  </Typography>
                  {notification.event_id && (
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                        Event ID: {notification.event_id}
                    </Typography>
                  )}
                  <Chip
                    label={notification.is_read ? "Read" : "Unread"}
                    size="small"
                    color={notification.is_read ? "success" : "warning"}
                    sx={{ mt: 1, pointerEvents: "none" }}
                  />
                </Box>
                <Box>
                  {!notification.is_read && (
                    <Tooltip title="Mark as Read">
                      <IconButton onClick={() => markAsRead(notification.id)}>
                        <DoneIcon />
                      </IconButton>
                    </Tooltip>
                  )}
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(notification.id)}>
                      <DeleteIcon color="error" /> {/* Added color for delete icon */}
                    </IconButton>
                  </Tooltip>
                </Box>
              </Paper>
            ))}
          </Stack>
        )}
        </>
      )}

      {/* Snackbar for all success/error messages */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      >
        <Alert
          onClose={() => setSnackbarOpen(false)}
          severity={status.error ? "error" : "success"}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {status.error || status.success}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default NotificationPage;
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
}

const NotificationPage: React.FC = () => {
  const { userId } = useUser();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchNotifications = useCallback(async () => {
    try {
      const res = await axios.get(`http://localhost:8000/api/notifications/${userId}`);
      setNotifications(res.data.notifications);
    } catch {
      setError("Failed to load notifications.");
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const markAsRead = async (id: string) => {
    try {
      await axios.put(`http://localhost:8000/api/notifications/${id}/read`);
      setNotifications(prev =>
        prev.map(n => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch {
      setError("Failed to mark as read.");
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await axios.delete(`http://localhost:8000/api/notifications/${id}`);
      setNotifications(prev => prev.filter(n => n.id !== id));
    } catch {
      setError("Failed to delete notification.");
    }
  };

  useEffect(() => {
    if (userId) fetchNotifications();
  }, [fetchNotifications, userId]);

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" mb={3}>Notifications</Typography>

      {loading ? (
        <Box display="flex" justifyContent="center"><CircularProgress /></Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : notifications.length === 0 ? (
        <Typography>No notifications found.</Typography>
      ) : (
        <Stack spacing={2}>
          {notifications.map(notification => (
            <Paper
              key={notification.id}
              elevation={3}
              sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
            >
              <Box>
                <Typography variant="body1">{notification.message}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {new Date(notification.created_at).toLocaleString()}
                </Typography>
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
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </Paper>
          ))}
        </Stack>
      )}
    </Container>
  );
};

export default NotificationPage;
// src/pages/HistoryPage.tsx
import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import {
  Container,
  Typography,
  CircularProgress,
  Alert,
  Stack,
  IconButton,
  Menu,
  MenuItem,
  Box,
  Paper,
  Chip,
  Snackbar,
} from "@mui/material";
import { MoreVert as MoreIcon } from "@mui/icons-material";
import { useUser } from "../context/UserContext";

interface HistoryItem {
  id: string;
  status: string;
  user_id: string;
  event_id: string;
  events: {
    name: string;
    description: string;
    location: string;
    event_date: string;
    urgency: string;
  };
  signed_up_at: string;
}

const HistoryPage: React.FC = () => {
  const { userId } = useUser();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState({ success: "", error: "" });
  const [snackbarOpen, setSnackbarOpen] = useState(false);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setStatus({ success: "", error: "" });
    try {
      if (!userId) {
        setStatus({ success: "", error: "User ID is missing. Please log in." });
        return;
      }
      const res = await axios.get(`http://localhost:8000/api/history/${userId}`);
      setHistory(res.data.history);
    } catch (err) {
      console.error("Failed to load volunteer history:", err);
      setStatus({ success: "", error: "Failed to load volunteer history." });
    } finally {
      setLoading(false);
      setSnackbarOpen(true);
    }
  }, [userId]); // Dependency: userId

  useEffect(() => {
    if (userId) {
      fetchHistory();
    } else {
      setLoading(false);
      setStatus({ success: "", error: "User not logged in." });
      setSnackbarOpen(true);
    }
  }, [fetchHistory, userId]); // Added fetchHistory to dependencies


  const handleUpdate = async (logId: string, newStatus: string, eventId: string) => {
    setStatus({ success: "", error: "" });
    try {
      if (!userId) throw new Error("User ID is missing for update.");

      await axios.put(`http://localhost:8000/api/history/${logId}`, {
        user_id: userId,
        event_id: eventId,
        status: newStatus,
      });
      setStatus({ success: `Status updated to ${newStatus}.`, error: "" });
      fetchHistory();
    } catch (err) {
      console.error("Failed to update log:", err);
      setStatus({ success: "", error: "Failed to update log." });
    } finally {
      setSnackbarOpen(true);
    }
  };

  const handleDelete = async (logId: string) => {
    setStatus({ success: "", error: "" });
    try {
      await axios.delete(`http://localhost:8000/api/history/${logId}`);
      setStatus({ success: "Event deleted successfully.", error: "" });
      fetchHistory();
    } catch (err) {
      console.error("Delete failed:", err);
      setStatus({ success: "", error: "Delete failed" });
    } finally {
      setSnackbarOpen(true);
    }
  };

  const getStatusChipColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'attended':
        return 'success';
      case 'signed up':
        return 'info';
      case 'missed':
        return 'error';
      case 'cancelled':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" mb={3}>My Event History</Typography>

      {loading ? (
        <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
        </Box>
      ) : (
        <>
        {history.length === 0 ? (
          <Paper sx={{ p: 3, textAlign: "center", bgcolor: "background.default", boxShadow: 1, borderRadius: 2 }}>
            <Typography variant="body1" color="text.secondary">
              No participation history yet.
            </Typography>
          </Paper>
        ) : (
          <Stack spacing={2}>
            {history.map((item) => (
              <Paper
                key={item.id}
                elevation={3}
                sx={{ p: 2, display: "flex", flexDirection: 'column',
                    justifyContent: "space-between", alignItems: "flex-start",
                    borderRadius: 2
                }}
              >
                <Box sx={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="h6">{item.events.name}</Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {new Date(item.events.event_date).toLocaleDateString()} — {item.events.location}
                    </Typography>
                  </Box>
                  <HistoryMenu
                    logId={item.id}
                    currentStatus={item.status}
                    onUpdate={handleUpdate}
                    onDelete={handleDelete}
                    eventId={item.event_id}
                  />
                </Box>
                <Typography variant="body2" sx={{ mb: 1, color: 'text.primary' }}>{item.events.description}</Typography>
                <Box display="flex" alignItems="center" gap={1}>
                    <Chip label={`Status: ${item.status}`} color={getStatusChipColor(item.status) as any} size="small" />
                    <Typography variant="caption" color="text.secondary">
                        Signed Up: {new Date(item.signed_up_at).toLocaleDateString()}
                    </Typography>
                </Box>
              </Paper>
            ))}
          </Stack>
        )}
        </>
      )}

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

// ... HistoryMenu component (remains unchanged)
const HistoryMenu = ({
  logId,
  currentStatus,
  onUpdate,
  onDelete,
  eventId,
}: {
  logId: string;
  currentStatus: string;
  onUpdate: (logId: string, newStatus: string, eventId: string) => void;
  onDelete: (logId: string) => void;
  eventId: string;
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const handleClose = () => setAnchorEl(null);
  const statuses = ["Attended", "Signed Up", "Missed"];

  return (
    <>
      <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} size="small">
        <MoreIcon fontSize="small" />
      </IconButton>
      <Menu anchorEl={anchorEl} open={open} onClose={handleClose}>
        {statuses.map((status) => (
          <MenuItem
            key={status}
            disabled={status === currentStatus}
            onClick={() => {
              handleClose();
              onUpdate(logId, status, eventId);
            }}
          >
            Mark as {status}
          </MenuItem>
        ))}
        <MenuItem
          onClick={() => {
            handleClose();
            onDelete(logId);
          }}
          sx={{ color: "red" }}
        >
          Delete Log
        </MenuItem>
      </Menu>
    </>
  );
};

export default HistoryPage;
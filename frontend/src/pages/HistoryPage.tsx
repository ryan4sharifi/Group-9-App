// src/pages/HistoryPage.tsx
import React, { useEffect, useState } from "react";
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
  Snackbar, // Added Snackbar
} from "@mui/material";
import { MoreVert as MoreIcon } from "@mui/icons-material";
import { useUser } from "../context/UserContext";

interface HistoryItem {
  id: string;
  status: string;
  user_id: string; // Added user_id based on schema
  event_id: string;
  events: {
    name: string;
    description: string;
    location: string;
    event_date: string; // Stored as string, convert to Date for display
    urgency: string;
  };
  signed_up_at: string; // Added based on schema
}

const HistoryPage: React.FC = () => {
  const { userId } = useUser();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState({ success: "", error: "" }); // Combined status for Snackbar
  const [snackbarOpen, setSnackbarOpen] = useState(false); // Snackbar control

  const fetchHistory = async () => {
    setLoading(true);
    setStatus({ success: "", error: "" }); // Clear previous status
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
      setSnackbarOpen(true); // Open Snackbar even for fetch errors
    }
  };

  useEffect(() => {
    if (userId) {
      fetchHistory();
    } else {
      setLoading(false);
      setStatus({ success: "", error: "User not logged in." });
      setSnackbarOpen(true);
    }
  }, [userId]);

  const handleUpdate = async (logId: string, newStatus: string, eventId: string) => {
    setStatus({ success: "", error: "" }); // Clear previous status
    try {
      if (!userId) throw new Error("User ID is missing for update.");

      await axios.put(`http://localhost:8000/api/history/${logId}`, {
        user_id: userId,
        event_id: eventId, // Ensure eventId is passed correctly
        status: newStatus,
      });
      setStatus({ success: `Status updated to ${newStatus}.`, error: "" });
      fetchHistory(); // Re-fetch to show updated status
    } catch (err) {
      console.error("Failed to update log:", err);
      setStatus({ success: "", error: "Failed to update log." });
    } finally {
      setSnackbarOpen(true);
    }
  };

  const handleDelete = async (logId: string) => {
    setStatus({ success: "", error: "" }); // Clear previous status
    try {
      await axios.delete(`http://localhost:8000/api/history/${logId}`);
      setStatus({ success: "Log deleted successfully.", error: "" });
      fetchHistory(); // Re-fetch to show updated list
    } catch (err) {
      console.error("Failed to delete log:", err);
      setStatus({ success: "", error: "Failed to delete log." });
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
      case 'cancelled': // If you introduce a 'cancelled' status
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
                sx={{ p: 2, display: "flex", flexDirection: 'column', // Allow content to stack vertically
                    justifyContent: "space-between", alignItems: "flex-start", // Align items to start
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
                    // Pass eventId to HistoryMenu so it can be relayed back for update
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

// Updated HistoryMenu to accept eventId
const HistoryMenu = ({
  logId,
  currentStatus,
  onUpdate,
  onDelete,
  eventId, // Added eventId prop
}: {
  logId: string;
  currentStatus: string;
  onUpdate: (logId: string, newStatus: string, eventId: string) => void; // Updated signature
  onDelete: (logId: string) => void;
  eventId: string; // Event ID is needed for the update call
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
              onUpdate(logId, status, eventId); // Pass eventId here
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
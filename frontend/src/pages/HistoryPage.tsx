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
} from "@mui/material";
import { MoreVert as MoreIcon } from "@mui/icons-material";
import { useUser } from "../context/UserContext";

interface HistoryItem {
  id: string;
  status: string;
  event_id: string;
  events: {
    name: string;
    description: string;
    location: string;
    event_date: string;
    urgency: string;
  };
}

const HistoryPage: React.FC = () => {
  const { userId } = useUser();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`http://localhost:8000/api/history/${userId}`);
      setHistory(res.data.history);
    } catch {
      setError("Failed to load volunteer history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) fetchHistory();
  }, [userId]);

  const handleUpdate = async (logId: string, newStatus: string) => {
    try {
      await axios.put(`http://localhost:8000/api/history/${logId}`, {
        user_id: userId,
        event_id: history.find((h) => h.id === logId)?.event_id,
        status: newStatus,
      });
      fetchHistory();
    } catch {
      setError("Failed to update log.");
    }
  };

  const handleDelete = async (logId: string) => {
    try {
      await axios.delete(`http://localhost:8000/api/history/${logId}`);
      fetchHistory();
    } catch {
      setError("Failed to delete log.");
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" mb={3}>My Event History</Typography>

      {loading ? (
        <CircularProgress />
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : history.length === 0 ? (
        <Typography>No participation history yet.</Typography>
      ) : (
        <Stack spacing={2}>
          {history.map((item) => (
            <Paper
              key={item.id}
              elevation={3}
              sx={{ p: 2, display: "flex", justifyContent: "space-between", alignItems: "center" }}
            >
              <Box>
                <Typography variant="h6">{item.events.name}</Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {new Date(item.events.event_date).toLocaleDateString()} — {item.events.location}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>{item.events.description}</Typography>
                <Chip label={`Status: ${item.status}`} color="info" size="small" 
                sx={{ pointerEvents: "none" }}/>
              </Box>
              <HistoryMenu
                logId={item.id}
                currentStatus={item.status}
                onUpdate={handleUpdate}
                onDelete={handleDelete}
              />
            </Paper>
          ))}
        </Stack>
      )}
    </Container>
  );
};

const HistoryMenu = ({
  logId,
  currentStatus,
  onUpdate,
  onDelete,
}: {
  logId: string;
  currentStatus: string;
  onUpdate: (logId: string, newStatus: string) => void;
  onDelete: (logId: string) => void;
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
              onUpdate(logId, status);
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
// src/pages/ReportPage.tsx
import React, { useState, useCallback, useRef } from "react"; // Added useRef
import axios from "axios";
import {
  Container,
  Typography,
  Box,
  Button,
  CircularProgress,
  Alert,
  Paper,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  // Link, // Removed as it's not used in this file
} from "@mui/material";
import DescriptionIcon from "@mui/icons-material/Description"; // For PDF
import CsvFileIcon from "@mui/icons-material/DescriptionOutlined"; // For CSV
import { useUser } from "../context/UserContext";

// Import jsPDF and html2canvas for PDF generation
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

// Type definitions for reports - UPDATED FOR NESTED DATA
interface VolunteerReportItem {
  id: string; // volunteer_history ID
  status: string;
  signed_up_at: string;
  user_credentials: { // Data structure from backend is user_credentials, then nested user_profiles
    id: string;
    email: string;
    user_profiles: { // user_profiles is nested inside user_credentials
      full_name?: string;
      // Add other profile fields you want to display if available in the backend response
    };
  };
  events: { // events is directly under volunteer_history
    id: string;
    name: string;
    location: string;
    event_date: string;
    // Add other event fields you want to display if available in the backend response
  };
}

interface EventSummaryItem {
  event_id: string;
  name: string;
  date: string;
  location: string;
  volunteer_count: number;
}

const ReportPage: React.FC = () => {
  const { role } = useUser();
  const [reportType, setReportType] = useState<"volunteers" | "events" | null>(null);
  const [volunteerReport, setVolunteerReport] = useState<VolunteerReportItem[] | null>(null);
  const [eventSummaryReport, setEventSummaryReport] = useState<EventSummaryItem[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Refs for the tables, so html2canvas can target them
  const volunteersTableRef = useRef<HTMLTableElement>(null);
  const eventsTableRef = useRef<HTMLTableElement>(null);

  const fetchVolunteerReport = useCallback(async () => {
    setLoading(true);
    setError(null);
    setVolunteerReport(null);
    setReportType("volunteers");
    try {
      const response = await axios.get("http://localhost:8000/api/reports/volunteers");
      setVolunteerReport(response.data.report);
    } catch (err) {
      console.error("Error fetching volunteer report:", err);
      setError("Failed to fetch volunteer participation report.");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchEventSummaryReport = useCallback(async () => {
    setLoading(true);
    setError(null);
    setEventSummaryReport(null);
    setReportType("events");
    try {
      const response = await axios.get("http://localhost:8000/api/reports/events");
      setEventSummaryReport(response.data.event_summary);
    } catch (err) {
      console.error("Error fetching event summary report:", err);
      setError("Failed to fetch event participation summary.");
    } finally {
      setLoading(false);
    }
  }, []);

  // --- UPDATED generatePdf FUNCTION FOR HTML2CANVAS ---
  const generatePdf = async (data: any[], type: 'volunteers' | 'events') => {
    if (!data || data.length === 0) {
      alert("No data to export to PDF.");
      return;
    }

    const input = type === 'volunteers' ? volunteersTableRef.current : eventsTableRef.current;
    if (!input) {
      console.error("Table reference not found for PDF generation.");
      setError("Could not generate PDF: table content not found.");
      return;
    }

    // Temporarily create a clone of the table for PDF to ensure accurate capture
    // Sometimes elements captured by html2canvas appear cut off if overflowed/not fully visible
    const originalParent = input.parentNode;
    const clonedInput = input.cloneNode(true) as HTMLElement; // Clone the entire table
    clonedInput.style.width = 'fit-content'; // Ensure width is not constrained
    clonedInput.style.maxWidth = 'initial'; // Prevent max-width issues
    clonedInput.style.position = 'absolute';
    clonedInput.style.left = '-9999px'; // Move off-screen
    document.body.appendChild(clonedInput);

    try {
      const canvas = await html2canvas(clonedInput, {
        scale: 2, // Higher scale for better resolution
        useCORS: true, // If you have images from different origin, might need this
        logging: false, // Set to true for debugging html2canvas issues
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4'); // 'p' for portrait, 'mm' for millimeters, 'a4' for A4 size
      const imgWidth = 210 - 20; // A4 width (210mm) - 20mm margin (10mm left + 10mm right)
      const pageHeight = 297; // A4 height (297mm)
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;
      let position = 10; // Start position after title

      // Add title to PDF
      pdf.setFontSize(18);
      pdf.text(`Volunteer Portal - ${type === 'volunteers' ? 'Volunteer Participation Report' : 'Event Participation Summary'}`, 10, 10);
      pdf.setFontSize(10);
      pdf.text(`Generated on: ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}`, 10, 18);
      pdf.line(10, 20, 200, 20); // Draw a line


      // Add captured image of the table
      pdf.addImage(imgData, 'PNG', 10, position + 15, imgWidth, imgHeight); // Adjust Y-position
      heightLeft -= pageHeight;

      while (heightLeft >= 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
        heightLeft -= pageHeight;
      }

      pdf.save(`${type}_report_${new Date().toISOString().split('T')[0]}.pdf`);

    } catch (err) {
      console.error("Error generating PDF:", err);
      setError("Failed to generate PDF. Please try again.");
    } finally {
      if (clonedInput && originalParent) {
        document.body.removeChild(clonedInput); // Clean up the cloned element
      }
    }
  };
  // --- END UPDATED generatePdf FUNCTION ---

  // --- UPDATED generateCsv FUNCTION FOR NESTED DATA ---
  const generateCsv = (data: any[], type: 'volunteers' | 'events') => {
    if (!data || data.length === 0) {
      alert("No data to export to CSV.");
      return;
    }

    let csvContent = "";
    if (type === 'volunteers') {
      const headers = ["Volunteer Name", "Volunteer Email", "Event Name", "Event Location", "Event Date", "Participation Status", "Signed Up At"];
      csvContent = headers.join(",") + "\n";
      data.forEach((item: VolunteerReportItem) => {
        const row = [
          `"${item.user_credentials?.user_profiles?.full_name || 'N/A'}"`, // UPDATED PATH
          `"${item.user_credentials?.email || 'N/A'}"`, // UPDATED PATH
          `"${item.events?.name || 'N/A'}"`,
          `"${item.events?.location || 'N/A'}"`,
          `"${item.events?.event_date ? new Date(item.events.event_date).toLocaleDateString() : 'N/A'}"`,
          `"${item.status}"`,
          `"${new Date(item.signed_up_at).toLocaleString()}"`
        ];
        csvContent += row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(",") + "\n"; // Escaping quotes for CSV
      });
    } else if (type === 'events') {
      const headers = ["Event ID", "Event Name", "Event Date", "Event Location", "Volunteer Count"];
      csvContent = headers.join(",") + "\n";
      data.forEach((item: EventSummaryItem) => {
        const row = [
          `"${item.event_id}"`,
          `"${item.name}"`,
          `"${item.date ? new Date(item.date).toLocaleDateString() : 'N/A'}"`,
          `"${item.location}"`,
          item.volunteer_count.toString()
        ];
        csvContent += row.map(cell => `"${cell.replace(/"/g, '""')}"`).join(",") + "\n"; // Escaping quotes for CSV
      });
    }

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute("href", url);
      link.setAttribute("download", `${type}_report_${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } else {
      alert("Your browser does not support downloading files directly.");
    }
  };
  // --- END UPDATED generateCsv FUNCTION ---


  if (role !== "admin") {
    return (
      <Container maxWidth="md" sx={{ py: 4, textAlign: 'center' }}>
        <Alert severity="warning">
          You do not have permission to view this page. Only administrators can access reports.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight="bold" color="primary.main" mb={3}>
        Reporting Module
      </Typography>

      <Paper elevation={3} sx={{ p: 3, mb: 4, borderRadius: 2 }}>
        <Typography variant="h6" mb={2}>Generate Reports:</Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            onClick={fetchVolunteerReport}
            disabled={loading}
          >
            Volunteer Participation Report
          </Button>
          <Button
            variant="contained"
            onClick={fetchEventSummaryReport}
            disabled={loading}
          >
            Event Participation Summary
          </Button>
        </Box>
      </Paper>

      {loading && (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
      )}

      {/* Render the tables for display */}
      {reportType === "volunteers" && volunteerReport && (
        <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h5" fontWeight="medium">Volunteer Participation</Typography>
            <Box>
              <Button
                variant="outlined"
                startIcon={<DescriptionIcon />}
                onClick={() => generatePdf(volunteerReport, 'volunteers')}
                sx={{ mr: 1 }}
              >
                PDF
              </Button>
              <Button
                variant="outlined"
                startIcon={<CsvFileIcon />}
                onClick={() => generateCsv(volunteerReport, 'volunteers')}
              >
                CSV
              </Button>
            </Box>
          </Box>
          <Divider sx={{ mb: 2 }} />
          {volunteerReport.length === 0 ? (
            <Typography variant="body1" color="text.secondary">No volunteer participation data available.</Typography>
          ) : (
            <TableContainer>
              <Table size="small" ref={volunteersTableRef}> {/* Added ref here */}
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Volunteer Name</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Email</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Event Name</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Location</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Date</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {volunteerReport.map((item) => (
                    <TableRow key={item.id}>
                      {/* --- UPDATED DATA PATHS FOR DISPLAY --- */}
                      <TableCell>{item.user_credentials?.user_profiles?.full_name || 'N/A'}</TableCell>
                      <TableCell>{item.user_credentials?.email || 'N/A'}</TableCell>
                      <TableCell>{item.events?.name || 'N/A'}</TableCell>
                      <TableCell>{item.events?.location || 'N/A'}</TableCell>
                      <TableCell>{item.events?.event_date ? new Date(item.events.event_date).toLocaleDateString() : 'N/A'}</TableCell>
                      <TableCell>{item.status}</TableCell>
                      {/* --- END UPDATED DATA PATHS --- */}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>
      )}

      {reportType === "events" && eventSummaryReport && (
        <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h5" fontWeight="medium">Event Participation Summary</Typography>
            <Box>
              <Button
                variant="outlined"
                startIcon={<DescriptionIcon />}
                onClick={() => generatePdf(eventSummaryReport, 'events')}
                sx={{ mr: 1 }}
              >
                PDF
              </Button>
              <Button
                variant="outlined"
                startIcon={<CsvFileIcon />}
                onClick={() => generateCsv(eventSummaryReport, 'events')}
              >
                CSV
              </Button>
            </Box>
          </Box>
          <Divider sx={{ mb: 2 }} />
          {eventSummaryReport.length === 0 ? (
            <Typography variant="body1" color="text.secondary">No event summary data available.</Typography>
          ) : (
            <TableContainer>
              <Table size="small" ref={eventsTableRef}> {/* Added ref here */}
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Event Name</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Date</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Location</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Volunteers</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {eventSummaryReport.map((item) => (
                    <TableRow key={item.event_id}>
                      <TableCell>{item.name}</TableCell>
                      <TableCell>{item.date ? new Date(item.date).toLocaleDateString() : 'N/A'}</TableCell>
                      <TableCell>{item.location}</TableCell>
                      <TableCell>{item.volunteer_count}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Paper>
      )}
    </Container>
  );
};

export default ReportPage;

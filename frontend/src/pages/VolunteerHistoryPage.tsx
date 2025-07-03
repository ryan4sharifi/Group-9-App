import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  TextField,
  CircularProgress,
  Alert,
  Container,
  Chip,
  InputAdornment,
  TablePagination,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  type SelectChangeEvent,
} from '@mui/material';
import { Search, FilterList } from '@mui/icons-material';
import { useUser } from '../context/UserContext';

interface Event {
  event_name: string;
  event_description: string;
  location: string;
  event_date: string;
  required_skills?: string;
  urgency?: string;
}

interface HistoryItem {
  id: string;
  events: Event;
  status: 'Completed' | 'Confirmed' | 'Cancelled';
  participation_date?: string;
}

type Order = 'asc' | 'desc';
type OrderBy = keyof Event | 'status';

const VolunteerHistoryPage: React.FC = () => {
  const { userId } = useUser();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [orderBy, setOrderBy] = useState<OrderBy>('event_date');
  const [order, setOrder] = useState<Order>('desc');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    if (userId) {
      fetchHistory();
    } else {
      setLoading(false);
    }
  }, [userId]);

  const fetchHistory = async () => {
    try {
      // Replace with actual API call
      // const response = await axios.get(`http://localhost:8000/api/history/${userId}`);
      // setHistory(response.data.history || []);
      
      // Mock data for demonstration
      const mockHistory: HistoryItem[] = [
        {
          id: '1',
          events: {
            event_name: 'Annual Charity Gala',
            event_description: 'Fundraising event for local charities with dinner and auction',
            location: 'Grand Ballroom, Downtown Hotel',
            event_date: '2024-12-15',
            required_skills: 'Communication, Event Management',
            urgency: 'High'
          },
          status: 'Completed',
          participation_date: '2024-12-15'
        },
        {
          id: '2',
          events: {
            event_name: 'Community Clean-up',
            event_description: 'Neighborhood cleanup initiative to beautify local parks',
            location: 'Central Park',
            event_date: '2024-11-20',
            required_skills: 'Physical Labor',
            urgency: 'Medium'
          },
          status: 'Completed',
          participation_date: '2024-11-20'
        },
        {
          id: '3',
          events: {
            event_name: 'Food Bank Volunteering',
            event_description: 'Sorting and distributing food to families in need',
            location: 'City Food Bank',
            event_date: '2025-01-10',
            required_skills: 'Organization, Teamwork',
            urgency: 'High'
          },
          status: 'Confirmed',
        },
        {
          id: '4',
          events: {
            event_name: 'Youth Mentorship Program',
            event_description: 'Mentoring local youth in career development',
            location: 'Community Center',
            event_date: '2024-10-05',
            required_skills: 'Mentoring, Communication',
            urgency: 'Low'
          },
          status: 'Cancelled',
        },
      ];
      setHistory(mockHistory);
    } catch (err) {
      setError('Failed to fetch volunteer history.');
    } finally {
      setLoading(false);
    }
  };

  const handleSortRequest = (property: OrderBy) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleStatusFilterChange = (event: SelectChangeEvent<string>) => {
    setStatusFilter(event.target.value);
    setPage(0); // Reset to first page when filtering
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Completed':
        return 'success';
      case 'Confirmed':
        return 'primary';
      case 'Cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'High':
        return 'error';
      case 'Medium':
        return 'warning';
      case 'Low':
        return 'success';
      default:
        return 'default';
    }
  };

  const sortedAndFilteredHistory = history
    .filter((item) => {
      const matchesSearch = item.events.event_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           item.events.event_description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           item.events.location.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      let aValue: any;
      let bValue: any;

      if (orderBy === 'status') {
        aValue = a.status;
        bValue = b.status;
      } else {
        aValue = a.events[orderBy as keyof Event];
        bValue = b.events[orderBy as keyof Event];
      }

      if (orderBy === 'event_date') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      }

      if (aValue < bValue) {
        return order === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return order === 'asc' ? 1 : -1;
      }
      return 0;
    });

  // Pagination
  const paginatedHistory = sortedAndFilteredHistory.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Volunteer History
      </Typography>
      
      <Paper sx={{ p: 3 }}>
        {/* Search and Filter Controls */}
        <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
          <TextField
            label="Search Events"
            variant="outlined"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            sx={{ minWidth: 300, flexGrow: 1 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
          
          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Status Filter</InputLabel>
            <Select
              value={statusFilter}
              label="Status Filter"
              onChange={handleStatusFilterChange}
              startAdornment={<FilterList />}
            >
              <MenuItem value="all">All Status</MenuItem>
              <MenuItem value="Completed">Completed</MenuItem>
              <MenuItem value="Confirmed">Confirmed</MenuItem>
              <MenuItem value="Cancelled">Cancelled</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {/* Results Summary */}
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Showing {paginatedHistory.length} of {sortedAndFilteredHistory.length} events
        </Typography>

        {/* Data Table */}
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'event_name'}
                    direction={orderBy === 'event_name' ? order : 'asc'}
                    onClick={() => handleSortRequest('event_name')}
                  >
                    Event Name
                  </TableSortLabel>
                </TableCell>
                <TableCell>Event Description</TableCell>
                <TableCell>Location</TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'event_date'}
                    direction={orderBy === 'event_date' ? order : 'asc'}
                    onClick={() => handleSortRequest('event_date')}
                  >
                    Event Date
                  </TableSortLabel>
                </TableCell>
                <TableCell>Required Skills</TableCell>
                <TableCell>Urgency</TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'status'}
                    direction={orderBy === 'status' ? order : 'asc'}
                    onClick={() => handleSortRequest('status')}
                  >
                    Status
                  </TableSortLabel>
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {paginatedHistory.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                      {searchTerm || statusFilter !== 'all' 
                        ? 'No events match your search criteria' 
                        : 'No volunteer history found'}
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                paginatedHistory.map((item) => (
                  <TableRow key={item.id} hover>
                    <TableCell>
                      <Typography variant="subtitle2" fontWeight="medium">
                        {item.events.event_name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ maxWidth: 250 }}>
                        {item.events.event_description}
                      </Typography>
                    </TableCell>
                    <TableCell>{item.events.location}</TableCell>
                    <TableCell>
                      {new Date(item.events.event_date).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {item.events.required_skills || 'Not specified'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {item.events.urgency && (
                        <Chip
                          label={item.events.urgency}
                          size="small"
                          color={getUrgencyColor(item.events.urgency) as any}
                          variant="outlined"
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={item.status}
                        size="small"
                        color={getStatusColor(item.status) as any}
                      />
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Pagination */}
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={sortedAndFilteredHistory.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Container>
  );
};

export default VolunteerHistoryPage;
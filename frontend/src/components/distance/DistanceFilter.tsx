import React from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Slider,
  Switch,
  FormControlLabel,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';

interface DistanceFilterProps {
  maxDistance: number;
  sortBy: 'distance' | 'date' | 'name';
  sortOrder: 'asc' | 'desc';
  showNearbyOnly: boolean;
  onMaxDistanceChange: (distance: number) => void;
  onSortByChange: (sortBy: 'distance' | 'date' | 'name') => void;
  onSortOrderChange: (order: 'asc' | 'desc') => void;
  onShowNearbyOnlyChange: (show: boolean) => void;
  nearbyEventsCount?: number;
  totalEventsCount?: number;
}

const DISTANCE_MARKS = [
  { value: 16.1, label: '10 mi' },
  { value: 32.2, label: '20 mi' },
  { value: 48.3, label: '30 mi' },
  { value: 64.4, label: '40 mi' },
  { value: 80.5, label: '50 mi' },
];

const DistanceFilter: React.FC<DistanceFilterProps> = ({
  maxDistance,
  sortBy,
  sortOrder,
  showNearbyOnly,
  onMaxDistanceChange,
  onSortByChange,
  onSortOrderChange,
  onShowNearbyOnlyChange,
  nearbyEventsCount,
  totalEventsCount,
}) => {
  const handleDistanceChange = (event: Event, newValue: number | number[]) => {
    onMaxDistanceChange(newValue as number);
  };

  return (
    <Paper elevation={1} sx={{ mb: 2 }}>
      <Accordion defaultExpanded={false}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center" gap={1} sx={{ width: '100%' }}>
            <FilterIcon fontSize="small" />
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              Distance & Sorting Options
            </Typography>
            {nearbyEventsCount !== undefined && totalEventsCount !== undefined && (
              <Typography variant="body2" color="text.secondary">
                ({nearbyEventsCount} of {totalEventsCount} events)
              </Typography>
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails sx={{ p: 3 }}>
          <Box display="flex" flexDirection="column" gap={3}>
            {/* Show Nearby Only Toggle */}
            <FormControlLabel
              control={
                <Switch
                  checked={showNearbyOnly}
                  onChange={(e) => onShowNearbyOnlyChange(e.target.checked)}
                  color="primary"
                />
              }
              label={`Show only events within ${Math.round(maxDistance * 0.621371)} mi`}
            />

            {/* Distance Slider */}
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Maximum Distance: {Math.round(maxDistance * 0.621371)} mi ({maxDistance} km)
              </Typography>
              <Box sx={{ px: 2, mt: 3, mb: 4 }}>
                <Slider
                  value={maxDistance}
                  onChange={handleDistanceChange}
                  min={1}
                  max={80.5}
                  marks={DISTANCE_MARKS}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => `${Math.round(value * 0.621371)}mi`}
                  sx={{ 
                    '& .MuiSlider-markLabel': {
                      fontSize: '0.75rem',
                      marginTop: 1,
                    },
                    '& .MuiSlider-valueLabel': {
                      fontSize: '0.75rem',
                      backgroundColor: 'primary.main',
                    },
                    '& .MuiSlider-mark': {
                      backgroundColor: 'grey.400',
                      height: 8,
                      width: 2,
                    },
                  }}
                />
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 1 }}>
                Drag to adjust maximum distance
              </Typography>
            </Box>

            {/* Sort Options */}
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Sort & Order
              </Typography>
              <Box display="flex" gap={2} flexWrap="wrap">
                <FormControl size="small" sx={{ minWidth: 140 }}>
                  <InputLabel>Sort By</InputLabel>
                  <Select
                    value={sortBy}
                    label="Sort By"
                    onChange={(e) => onSortByChange(e.target.value as any)}
                  >
                    <MenuItem value="distance">Distance</MenuItem>
                    <MenuItem value="date">Event Date</MenuItem>
                    <MenuItem value="name">Event Name</MenuItem>
                  </Select>
                </FormControl>

                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Order</InputLabel>
                  <Select
                    value={sortOrder}
                    label="Order"
                    onChange={(e) => onSortOrderChange(e.target.value as any)}
                  >
                    <MenuItem value="asc">
                      {sortBy === 'distance' ? 'Nearest First' : 'Ascending'}
                    </MenuItem>
                    <MenuItem value="desc">
                      {sortBy === 'distance' ? 'Farthest First' : 'Descending'}
                    </MenuItem>
                  </Select>
                </FormControl>
              </Box>
            </Box>

            {/* Filter Summary */}
            <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1, border: '1px solid', borderColor: 'grey.200' }}>
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
                Active Filters: 
                {showNearbyOnly && ` Within ${Math.round(maxDistance * 0.621371)}mi (${maxDistance}km)`}
                {showNearbyOnly && sortBy && ' • '}
                {` Sort: ${sortBy} (${sortOrder === 'asc' ? 
                  (sortBy === 'distance' ? 'nearest first' : 'ascending') : 
                  (sortBy === 'distance' ? 'farthest first' : 'descending')
                })`}
              </Typography>
            </Box>
          </Box>
        </AccordionDetails>
      </Accordion>
    </Paper>
  );
};

export default DistanceFilter;

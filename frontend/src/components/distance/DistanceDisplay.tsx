import React from 'react';
import { 
  Chip, 
  Box, 
  Typography, 
  Tooltip,
  CircularProgress 
} from '@mui/material';
import {
  DirectionsCar as CarIcon,
  AccessTime as TimeIcon,
  Place as PlaceIcon,
} from '@mui/icons-material';
import { getDistanceUrgencyColor, formatDistanceBoth } from '../../utils/distance';

interface DistanceDisplayProps {
  distance_text?: string;
  duration_text?: string;
  distance_value?: number;
  duration_value?: number;
  cached?: boolean;
  urgency?: 'low' | 'medium' | 'high';
  loading?: boolean;
  variant?: 'chip' | 'inline' | 'detailed' | 'compact';
  size?: 'small' | 'medium';
  showBothUnits?: boolean;
}

const DistanceDisplay: React.FC<DistanceDisplayProps> = ({
  distance_text,
  duration_text,
  distance_value,
  duration_value,
  cached = false,
  urgency = 'medium',
  loading = false,
  variant = 'chip',
  size = 'small',
  showBothUnits = true,
}) => {
  if (loading) {
    return (
      <Box display="flex" alignItems="center" gap={1}>
        <CircularProgress size={16} />
        <Typography variant="caption" color="text.secondary">
          Calculating distance...
        </Typography>
      </Box>
    );
  }

  if (!distance_text || !duration_text) {
    return (
      <Typography variant="caption" color="text.secondary">
        Distance unavailable
      </Typography>
    );
  }

  const color = getDistanceUrgencyColor(distance_value, urgency);
  
  // Format distance with both units if requested and distance_value is available
  const displayDistance = showBothUnits && distance_value 
    ? formatDistanceBoth(distance_value)
    : distance_text;
  
  const tooltipContent = (
    <Box>
      <Typography variant="body2">
        <strong>Distance:</strong> {showBothUnits && distance_value ? formatDistanceBoth(distance_value) : distance_text}
      </Typography>
      <Typography variant="body2">
        <strong>Travel Time:</strong> {duration_text}
      </Typography>
      {cached && (
        <Typography variant="caption" color="text.secondary">
          Cached result
        </Typography>
      )}
    </Box>
  );

  if (variant === 'chip') {
    return (
      <Tooltip title={tooltipContent} arrow>
        <Chip
          icon={<CarIcon />}
          label={displayDistance}
          size={size}
          color={color}
          variant="outlined"
        />
      </Tooltip>
    );
  }

  if (variant === 'compact') {
    return (
      <Tooltip title={tooltipContent} arrow>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <PlaceIcon fontSize="small" color="action" sx={{ fontSize: 14 }} />
          {displayDistance}
        </Typography>
      </Tooltip>
    );
  }

  if (variant === 'inline') {
    return (
      <Tooltip title={tooltipContent} arrow>
        <Box display="flex" alignItems="center" gap={0.5}>
          <PlaceIcon fontSize="small" color="action" />
          <Typography variant="caption" color="text.secondary">
            {displayDistance}
          </Typography>
          <TimeIcon fontSize="small" color="action" />
          <Typography variant="caption" color="text.secondary">
            {duration_text}
          </Typography>
        </Box>
      </Tooltip>
    );
  }

  if (variant === 'detailed') {
    return (
      <Box>
        <Box display="flex" alignItems="center" gap={1} mb={0.5}>
          <CarIcon fontSize="small" color={color === 'error' ? 'error' : 'action'} />
          <Typography 
            variant="body2" 
            color={color === 'error' ? 'error' : 'text.primary'}
            fontWeight="medium"
          >
            {displayDistance}
          </Typography>
        </Box>
        <Box display="flex" alignItems="center" gap={1}>
          <TimeIcon fontSize="small" color="action" />
          <Typography variant="body2" color="text.secondary">
            {duration_text}
          </Typography>
          {cached && (
            <Chip 
              label="Cached" 
              size="small" 
              variant="outlined" 
              color="default" 
            />
          )}
        </Box>
      </Box>
    );
  }

  return null;
};

export default DistanceDisplay;

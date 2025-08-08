import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Box,
  Typography
} from '@mui/material';
import type { Region } from '../../types/sequence';

interface FeatureTableProps {
  regions: Region[];
  selectedRegions: string[];
  onRegionSelect: (regionId: string) => void;
}

export const FeatureTable: React.FC<FeatureTableProps> = ({
  regions,
  selectedRegions,
  onRegionSelect
}) => {
  if (regions.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="body1" color="text.secondary">
          No regions to display. Annotate sequences to see features.
        </Typography>
      </Box>
    );
  }

  return (
    <TableContainer component={Paper} variant="outlined">
      <Table>
        <TableHead>
          <TableRow>
            <TableCell><strong>Region</strong></TableCell>
            <TableCell><strong>Type</strong></TableCell>
            <TableCell><strong>Start</strong></TableCell>
            <TableCell><strong>Stop</strong></TableCell>
            <TableCell><strong>Length</strong></TableCell>
            <TableCell><strong>Sequence</strong></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {regions.map((region) => (
            <TableRow
              key={region.id}
              hover
              sx={{
                cursor: 'pointer',
                backgroundColor: selectedRegions.includes(region.id) 
                  ? 'rgba(25, 118, 210, 0.08)' 
                  : 'inherit',
                '&:hover': {
                  backgroundColor: selectedRegions.includes(region.id)
                    ? 'rgba(25, 118, 210, 0.12)'
                    : 'rgba(0, 0, 0, 0.04)'
                }
              }}
              onClick={() => onRegionSelect(region.id)}
            >
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      borderRadius: '50%',
                      backgroundColor: region.color
                    }}
                  />
                  {region.name}
                </Box>
              </TableCell>
              <TableCell>
                <Chip
                  label={region.type}
                  size="small"
                  color={region.type === 'CDR' ? 'primary' : 'default'}
                  variant="outlined"
                />
              </TableCell>
              <TableCell>{region.start}</TableCell>
              <TableCell>{region.stop}</TableCell>
              <TableCell>{region.sequence.length}</TableCell>
              <TableCell>
                <Box
                  sx={{
                    fontFamily: 'monospace',
                    fontSize: '0.75rem',
                    maxWidth: 200,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}
                  title={region.sequence}
                >
                  {region.sequence}
                </Box>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

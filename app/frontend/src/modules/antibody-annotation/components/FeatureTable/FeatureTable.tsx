import React from 'react';
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
  Chip
} from '@mui/material';
import type { Region } from '../../../../types/sequence';
import { FeatureType } from '../../../../types/sequence';

const getChipColor = (type: string) => {
  switch (type) {
    case FeatureType.CDR:
      return 'primary';
    case FeatureType.CONSTANT:
      return 'secondary';
    case FeatureType.LINKER:
      return 'info';
    default:
      return 'default';
  }
};

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
    <TableContainer component={Paper} variant="outlined" data-testid="feature-table">
      <Table>
        <TableHead>
          <TableRow>
            <TableCell><strong>Region</strong></TableCell>
            <TableCell><strong>Type</strong></TableCell>
            <TableCell><strong>Start</strong></TableCell>
            <TableCell><strong>Stop</strong></TableCell>
            <TableCell><strong>Length</strong></TableCell>
            <TableCell><strong>Details</strong></TableCell>
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
                  color={getChipColor(region.type)}
                  variant="outlined"
                  sx={region.type === 'LINKER' ? { fontStyle: 'italic' } : undefined}
                />
              </TableCell>
              <TableCell>{region.start}</TableCell>
              <TableCell>{region.stop}</TableCell>
              <TableCell>{region.sequence.length}</TableCell>
              <TableCell>
                {region.details && (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                    {region.details.isotype && (
                      <Chip
                        label={`Isotype: ${region.details.isotype}`}
                        size="small"
                        color="secondary"
                        variant="outlined"
                      />
                    )}
                    {region.details.domain_type && (
                      <Chip
                        label={`Domain: ${region.details.domain_type}`}
                        size="small"
                        color="info"
                        variant="outlined"
                      />
                    )}
                    {region.details.preceding_linker && (
                      <Chip
                        label={`Linker: ${region.details.preceding_linker.sequence.length} aa`}
                        size="small"
                        color="info"
                        variant="outlined"
                        sx={{ fontStyle: 'italic' }}
                      />
                    )}
                  </Box>
                )}
              </TableCell>
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

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { Box, Typography } from '@mui/material';
import type { Region } from '../../../../types/sequence';

interface DomainGraphicsProps {
  regions: Region[];
  sequenceLength: number;
  width?: number;
  height?: number;
  onRegionClick: (region: Region) => void;
  selectedRegions: string[];
}

export const DomainGraphics: React.FC<DomainGraphicsProps> = ({
  regions,
  sequenceLength,
  width = 800,
  height = 80,
  onRegionClick,
  selectedRegions
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || regions.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // Clear previous render

    const margin = { top: 10, right: 20, bottom: 30, left: 20 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Create scales
    const xScale = d3.scaleLinear()
      .domain([1, sequenceLength])
      .range([0, innerWidth]);

    const g = svg
      .append('g')
      .attr('transform', `translate(${margin.left}, ${margin.top})`);

    // Draw background line representing the full sequence
    g.append('line')
      .attr('x1', 0)
      .attr('x2', innerWidth)
      .attr('y1', innerHeight / 2)
      .attr('y2', innerHeight / 2)
      .attr('stroke', '#e0e0e0')
      .attr('stroke-width', 2);

    // Sort regions by start position to avoid overlaps
    const sortedRegions = [...regions].sort((a, b) => a.start - b.start);

    // Draw regions
    const regionHeight = 20;
    const regionY = (innerHeight - regionHeight) / 2;

    const regionGroups = g.selectAll('.region-group')
      .data(sortedRegions)
      .enter()
      .append('g')
      .attr('class', 'region-group')
      .style('cursor', 'pointer');

    // Draw region rectangles
    regionGroups
      .append('rect')
      .attr('x', d => xScale(d.start))
      .attr('y', regionY)
      .attr('width', d => Math.max(2, xScale(d.stop) - xScale(d.start)))
      .attr('height', regionHeight)
      .attr('fill', d => d.color)
      .attr('stroke', d => selectedRegions.includes(d.id) ? '#000' : 'none')
      .attr('stroke-width', d => selectedRegions.includes(d.id) ? 2 : 0)
      .attr('opacity', 0.8)
      .on('mouseover', function(event, d) {
        d3.select(this)
          .attr('opacity', 1)
          .attr('stroke', '#333')
          .attr('stroke-width', 1);
        
        // Show tooltip
        const tooltip = d3.select('body')
          .append('div')
          .attr('class', 'domain-tooltip')
          .style('position', 'absolute')
          .style('background', 'rgba(0, 0, 0, 0.8)')
          .style('color', 'white')
          .style('padding', '8px')
          .style('border-radius', '4px')
          .style('font-size', '12px')
          .style('pointer-events', 'none')
          .style('z-index', 1000)
          .html(`
            <strong>${d.name}</strong><br/>
            Position: ${d.start}-${d.stop}<br/>
            Length: ${d.sequence.length} AA<br/>
            Type: ${d.type}
          `);

        tooltip
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 10) + 'px');
      })
      .on('mouseout', function(_, d) {
        d3.select(this)
          .attr('opacity', 0.8)
          .attr('stroke', selectedRegions.includes(d.id) ? '#000' : 'none')
          .attr('stroke-width', selectedRegions.includes(d.id) ? 2 : 0);
        
        // Remove tooltip
        d3.selectAll('.domain-tooltip').remove();
      })
      .on('click', function(event, d) {
        event.stopPropagation();
        onRegionClick(d);
      });

    // Add region labels
    regionGroups
      .append('text')
      .attr('x', d => xScale(d.start) + (xScale(d.stop) - xScale(d.start)) / 2)
      .attr('y', regionY + regionHeight / 2)
      .attr('dy', '0.35em')
      .attr('text-anchor', 'middle')
      .attr('fill', 'white')
      .attr('font-size', '10px')
      .attr('font-weight', 'bold')
      .style('pointer-events', 'none')
      .text(d => {
        const width = xScale(d.stop) - xScale(d.start);
        return width > 30 ? d.name : ''; // Only show label if region is wide enough
      });

    // Add position axis
    const xAxis = d3.axisBottom(xScale)
      .tickSize(5)
      .tickFormat(d => d.toString());

    g.append('g')
      .attr('transform', `translate(0, ${innerHeight - 5})`)
      .call(xAxis)
      .selectAll('text')
      .style('font-size', '10px');

  }, [regions, sequenceLength, width, height, selectedRegions, onRegionClick]);

  if (regions.length === 0) {
    return (
      <Box sx={{ 
        height, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        bgcolor: 'grey.100',
        borderRadius: 1
      }}>
        <Typography variant="caption" color="text.secondary">
          No regions to visualize
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', overflow: 'auto' }} data-testid="domain-graphics">
      <svg
        ref={svgRef}
        width={width}
        height={height}
        style={{ display: 'block' }}
      />
    </Box>
  );
};

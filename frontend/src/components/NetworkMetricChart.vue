<template>
  <div class="network-metric-chart-container">
    <div ref="chartContainer" class="chart"></div>
    <!-- The global tooltip component is used instead -->
  </div>
</template>

<script>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as d3 from 'd3'
import tooltipService from '../services/tooltipService.js'

export default {
  name: 'NetworkMetricChart',
  props: {
    metric: {
      type: String,
      required: true
    },
    unit: {
      type: String,
      default: 'ms'
    },
    color: {
      type: String,
      default: null // Will use CSS variables based on metric
    },
    minYScale: {
      type: Number,
      default: null
    },
    selectedHours: {
      type: Number,
      default: 3
    },
    data: {
      type: Array,
      default: () => []
    }
  },
  setup(props) {
    const chartContainer = ref(null)
    
    // Use the tooltip service directly
    const showTooltipAt = tooltipService.showTooltipAt.bind(tooltipService);
    const hideTooltip = tooltipService.hideAll.bind(tooltipService);
    
    // Get the appropriate chart color based on the metric
    const getChartColor = () => {
      // If color is explicitly provided, use it
      if (props.color) return props.color;
      
      // Otherwise use CSS variables based on metric
      const metricLower = props.metric.toLowerCase();
      if (metricLower.includes('latency')) {
        return getComputedStyle(document.documentElement).getPropertyValue('--color-chart-latency').trim();
      } else if (metricLower.includes('jitter')) {
        return getComputedStyle(document.documentElement).getPropertyValue('--color-chart-jitter').trim();
      } else if (metricLower.includes('packet') || metricLower.includes('loss')) {
        return getComputedStyle(document.documentElement).getPropertyValue('--color-chart-packet-loss').trim();
      }
      // Default color
      return getComputedStyle(document.documentElement).getPropertyValue('--color-brand-secondary').trim();
    };
    
    const drawChart = () => {
      // Exit if no container or data
      if (!chartContainer.value || !props.data || props.data.length === 0) return
      
      // Clear previous chart
      d3.select(chartContainer.value).selectAll('*').remove()
      
      // Set dimensions with more bottom margin for X-axis labels
      const margin = { top: 20, right: 20, bottom: 40, left: 40 }
      const width = chartContainer.value.clientWidth - margin.left - margin.right
      const height = 200 - margin.top - margin.bottom
      
      // Create SVG
      const svg = d3.select(chartContainer.value)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)
      
      // Process data and ensure timestamps are Date objects
      const processedData = props.data.map(d => ({
        timestamp: d.timestamp instanceof Date ? d.timestamp : new Date(d.timestamp),
        value: d.value
      })).sort((a, b) => a.timestamp - b.timestamp)
      
      // Calculate time range for the chart with millisecond precision
      const latestTimestamp = d3.max(processedData, d => d.timestamp)
      const startTime = new Date(latestTimestamp.getTime() - (props.selectedHours * 60 * 60 * 1000))
      
      // Create time scale
      const xScale = d3.scaleTime()
        .domain([startTime, latestTimestamp])
        .range([0, width])
      
      // Calculate y scale
      let yMax = d3.max(processedData, d => d.value) * 1.1
      if (props.minYScale) {
        yMax = Math.max(yMax, props.minYScale)
      }
      
      const yScale = d3.scaleLinear()
        .domain([0, yMax])
        .range([height, 0])
      
      // Configure X-axis ticks based on selected time range
      let xAxisTicks;
      
      // Set appropriate tick intervals based on the time range selected by the user
      // This ensures the x-axis has a readable number of markers regardless of range
      if (props.selectedHours <= 3) {
        // For 3-hour view: Show tick marks every 15 minutes
        // This provides enough detail for short-term monitoring
        xAxisTicks = d3.timeMinute.every(15);
      } else if (props.selectedHours <= 24) {
        // For 12-hour and 24-hour views: Show tick marks every hour
        // This gives a good balance of detail without overcrowding
        xAxisTicks = d3.timeHour.every(1);
      } else {
        // For 3-day and 7-day views: Show tick marks every day
        // This provides appropriate context for long-term trends
        xAxisTicks = d3.timeDay.every(1);
      }
      
      // Configure time format based on selected hours
      const timeFormat = (date) => {
        if (props.selectedHours <= 24) {
          // Show hour:minute for shorter time ranges
          return d3.timeFormat('%H:%M')(date);
        } else {
          // Show month/day for longer time ranges
          return d3.timeFormat('%m/%d')(date);
        }
      };
      
      // Draw X-axis with configured ticks and format
      const xAxis = svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale)
          .ticks(xAxisTicks)
          .tickFormat(timeFormat)
          .tickSizeOuter(0)
        );
      
      // Style X-axis text
      xAxis.selectAll('text')
        .style('text-anchor', 'end')
        .attr('dy', '0.5em')
        .attr('dx', '-0.3em')
        .attr('transform', 'rotate(-20)');
      
      // Draw Y-axis (with labels on every other tick)
      svg.append('g')
        .attr('class', 'y-axis')
        .call(d3.axisLeft(yScale)
          .tickFormat((d, i) => i % 2 === 0 ? d : '') // Only show label for every other tick
        )
      
      // Add Y axis label
      svg.append('text')
        .attr('class', 'axis-label')
        .attr('transform', 'rotate(-90)')
        .attr('y', 0 - margin.left)
        .attr('x', 0 - (height / 2))
        .attr('dy', '1em')
        .style('text-anchor', 'middle')
        .text(`${props.metric} (${props.unit})`)
      
      // Filter data to the selected time range
      const visibleData = processedData.filter(d => 
        d.timestamp >= startTime && d.timestamp <= latestTimestamp
      )
      
      // Debug log for each chart
      console.log(`${props.metric} chart data:`, {
        total: processedData.length,
        visible: visibleData.length,
        timeRange: `${startTime.toLocaleTimeString()} - ${new Date(latestTimestamp).toLocaleTimeString()}`,
        selectedHours: props.selectedHours,
        actualTimeSpan: ((latestTimestamp - startTime) / (1000 * 60 * 60)).toFixed(2) + 'h'
      })
      
      // Set maximum bar width based on time range
      let maxBarWidth
      
      if (props.selectedHours <= 3) {
        // For 3 hours view - allow wider bars
        maxBarWidth = 6
      } else if (props.selectedHours <= 24) {
        // For 12-24 hour views - medium maximum
        maxBarWidth = 4
      } else if (props.selectedHours <= 72) {
        // For 3 day view - smaller maximum
        maxBarWidth = 2
      } else {
        // For 7 day view - very small maximum
        maxBarWidth = 1.5
      }
      
      // Calculate bar width based on available space but cap at maximum
      const calculatedWidth = (width / Math.max(1, visibleData.length)) * 0.8
      const barWidth = Math.min(maxBarWidth, Math.max(1, calculatedWidth))
      
      // Draw the bars
      svg.selectAll('.bar')
        .data(visibleData)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', d => xScale(d.timestamp)) // Align to exact timestamp instead of centering
        .attr('width', barWidth)
        .attr('y', d => yScale(d.value))
        .attr('height', d => height - yScale(d.value))
        .attr('fill', getChartColor())
        .attr('opacity', 0.8)
        .attr('rx', 1)
        .attr('stroke', 'none') // No stroke by default
        .on('mouseover', function(event, d) {
          // Highlight the bar
          d3.select(this)
            .attr('opacity', 1)
            .attr('stroke', getComputedStyle(document.documentElement).getPropertyValue('--color-chart-highlight'))
            .attr('stroke-width', 1)
          
          // Make sure we have a valid timestamp
          const date = new Date(d.timestamp)
          
          // Format content for tooltip
          const tooltipContent = `<div class="tooltip-header">
              ${date.toLocaleDateString()} ${date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}
            </div>
            <div class="tooltip-content">
              ${props.metric}: <strong>${d.value.toFixed(2)} ${props.unit}</strong>
            </div>`;
          
          // Show tooltip using the global tooltip system with smart positioning
          showTooltipAt(
            event.clientX, 
            event.clientY, 
            tooltipContent,
            true // isChart = true
          );
        })
        .on('mousemove', function(event) {
          // Update tooltip position with the same content
          const d = d3.select(this).datum();
          const date = new Date(d.timestamp);
          
          // Format content for tooltip
          const tooltipContent = `<div class="tooltip-header">
              ${date.toLocaleDateString()} ${date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}
            </div>
            <div class="tooltip-content">
              ${props.metric}: <strong>${d.value.toFixed(2)} ${props.unit}</strong>
            </div>`;
          
          // Update tooltip position with smart positioning
          showTooltipAt(
            event.clientX, 
            event.clientY, 
            tooltipContent,
            true // isChart = true
          );
        })
        .on('mouseout', function() {
          // Reset bar style
          d3.select(this)
            .attr('opacity', 0.8)
            .attr('stroke', 'none')
          
          // Hide tooltip
          hideTooltip();
        })
    }
    
    // Draw chart on mount and handle resize
    onMounted(() => {
      drawChart()
      window.addEventListener('resize', drawChart)
    })
    
    // Clean up
    onBeforeUnmount(() => {
      window.removeEventListener('resize', drawChart)
    })
    
    // Redraw when data or selectedHours changes
    watch(() => [props.data, props.selectedHours], drawChart, { deep: true })
    
    return {
      chartContainer
    }
  }
}
</script>

<style scoped>
.network-metric-chart-container {
  width: 100%;
  margin: 0 auto;
}

.chart {
  width: 100%;
  height: 200px;
}

:deep(.domain),
:deep(.tick line) {
  stroke: var(--color-border-subtle);
}

:deep(.tick text) {
  font-size: var(--font-size-xs);
  fill: var(--color-text-secondary);
}

:deep(.axis-label) {
  fill: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

:deep(.x-axis path),
:deep(.y-axis path) {
  stroke: var(--color-border-subtle);
}

/* Enhance contrast for bars in dark mode */
:deep(.bar) {
  opacity: 0.8;
}

.dark-theme :deep(.bar) {
  opacity: 0.9; /* Increased opacity for dark mode */
}

/* Moved tooltip styles to Tooltip.vue */
</style>
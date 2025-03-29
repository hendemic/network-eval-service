<template>
  <div class="network-metric-chart-container">
    <div ref="chartContainer" class="chart"></div>
  </div>
</template>

<script>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as d3 from 'd3'

export default {
  name: 'NetworkMetricChart',
  props: {
    metric: {
      type: String,
      required: true,
      default: 'Latency'
    },
    unit: {
      type: String,
      default: 'ms'
    },
    color: {
      type: String,
      default: '#42b983'
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
    
    // Create a simple tooltip
    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'chart-tooltip')
      .style('position', 'fixed')
      .style('background', 'rgba(0,0,0,0.7)')
      .style('color', 'white')
      .style('padding', '8px')
      .style('border-radius', '4px')
      .style('font-size', '12px')
      .style('pointer-events', 'none')
      .style('opacity', 0)
      .style('z-index', 9999)
    
    const drawChart = () => {
      // Check if we have data and container
      if (!chartContainer.value || !props.data || props.data.length === 0) return
      
      // Clear previous chart if it exists
      d3.select(chartContainer.value).selectAll('*').remove()
      
      // Set dimensions
      const margin = { top: 20, right: 20, bottom: 30, left: 40 }
      const width = chartContainer.value.clientWidth - margin.left - margin.right
      const height = 300 - margin.top - margin.bottom
      
      // Create SVG
      const svg = d3.select(chartContainer.value)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)
      
      // IMPORTANT: Clone the data and ensure all timestamps are Date objects
      const processedData = props.data.map(d => ({
        timestamp: d.timestamp instanceof Date ? d.timestamp : new Date(d.timestamp),
        value: d.value
      }))
      
      // Sort data by timestamp
      const sortedData = [...processedData].sort((a, b) => a.timestamp - b.timestamp)
      
      // Log data range
      console.log("Data from", sortedData[0]?.timestamp, "to", sortedData[sortedData.length-1]?.timestamp);
      console.log("Data points:", sortedData.length);
      
      // Get the latest data timestamp
      const latestTimestamp = d3.max(sortedData, d => d.timestamp);
      console.log("Latest timestamp:", latestTimestamp);
      
      // Calculate start time based on selected hours
      const startTime = new Date(latestTimestamp);
      startTime.setHours(startTime.getHours() - props.selectedHours);
      console.log("Start time for selected hours:", startTime);
      
      // Create x scale based on selected time range
      const xScale = d3.scaleTime()
        .domain([startTime, latestTimestamp])
        .range([0, width])
      
      console.log(`Domain set to: ${startTime.toLocaleTimeString()} - ${latestTimestamp.toLocaleTimeString()} (${props.selectedHours} hours)`)
      
      // Determine Y axis scale with custom min
      let yMax = d3.max(sortedData, d => d.value) * 1.1
      
      // Apply minimum scale if provided
      if (props.minYScale) {
        yMax = Math.max(yMax, props.minYScale)
      }
      
      const yScale = d3.scaleLinear()
        .domain([0, yMax])
        .range([height, 0])
      
      // Draw X axis (no labels)
      svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale).tickSize(0).tickFormat(''))
      
      // Draw Y axis
      svg.append('g')
        .call(d3.axisLeft(yScale))
      
      // Add Y axis label
      svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 0 - margin.left)
        .attr('x', 0 - (height / 2))
        .attr('dy', '1em')
        .style('text-anchor', 'middle')
        .style('fill', '#666')
        .text(`${props.metric} (${props.unit})`)
      
      // Calculate bar width based on time range and data density
      const barWidth = () => {
        // Filter data to the selected time range for width calculation
        const rangeData = sortedData.filter(d => 
          d.timestamp >= startTime && d.timestamp <= latestTimestamp
        );
        
        if (rangeData.length <= 1) return 10;
        
        // Calculate average time between bars in pixels
        const timeRangeInMs = latestTimestamp - startTime;
        const pixelsPerBar = width / rangeData.length;
        
        // Scale it slightly to leave small gaps
        return Math.max(1, pixelsPerBar * 0.8);
      };
      
      // Filter data for the selected time range for better display
      const visibleData = sortedData.filter(d => 
        d.timestamp >= startTime && d.timestamp <= latestTimestamp
      );
      console.log("Visible data points:", visibleData.length);
      
      // Add visual indication for the time range
      svg.append('rect')
        .attr('class', 'time-range-indicator')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', width)
        .attr('height', height)
        .attr('fill', 'rgba(200, 200, 200, 0.05)')
        .attr('stroke', 'rgba(200, 200, 200, 0.2)')
        .attr('stroke-width', 1)
      
      // Draw the bars - only for points within the selected time range
      svg.selectAll('.bar')
        .data(visibleData)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', d => xScale(d.timestamp) - (barWidth() / 2)) // Center bar on timestamp
        .attr('width', barWidth())
        .attr('y', d => yScale(d.value))
        .attr('height', d => height - yScale(d.value))
        .attr('fill', props.color)
        .attr('opacity', 0.8)
        .attr('rx', 1)
        .on('mouseover', function(event, d) {
          // Highlight the bar
          d3.select(this)
            .attr('opacity', 1)
            .attr('stroke', '#333')
            .attr('stroke-width', 1)
          
          // Format the tooltip
          const date = d.timestamp;
          const formattedDate = date.toLocaleDateString();
          const formattedTime = date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
          
          const tooltipHtml = `
            <div>
              <div style="font-weight: bold;">${formattedDate} ${formattedTime}</div>
              <div>${props.metric}: ${d.value.toFixed(2)} ${props.unit}</div>
            </div>
          `;
          
          // Show and position tooltip
          tooltip.html(tooltipHtml)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px')
            .style('opacity', 0.9);
        })
        .on('mousemove', function(event) {
          // Update tooltip position
          tooltip
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
        })
        .on('mouseout', function() {
          // Restore bar appearance
          d3.select(this)
            .attr('opacity', 0.8)
            .attr('stroke', 'none')
          
          // Hide tooltip
          tooltip.style('opacity', 0);
        });
    }
    
    // Draw chart on mount
    onMounted(() => {
      drawChart()
      
      // Handle window resize
      window.addEventListener('resize', drawChart)
    })
    
    // Clean up event listener and tooltips on unmount
    onBeforeUnmount(() => {
      window.removeEventListener('resize', drawChart)
      
      // Remove tooltip
      tooltip.remove()
    })
    
    // Redraw chart when data changes
    watch(() => [props.data, props.selectedHours], () => {
      drawChart()
    }, { deep: true })
    
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
  height: 300px;
}

:deep(.domain),
:deep(.tick line) {
  stroke: #ddd;
}

:deep(.tick text) {
  display: none;
}
</style>
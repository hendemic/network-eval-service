<template>
  <div class="network-chart-container">
    <div ref="chartContainer" class="chart"></div>
  </div>
</template>

<script>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as d3 from 'd3'

export default {
  name: 'NetworkChart',
  props: {
    data: {
      type: Array,
      required: true
    },
    metric: {
      type: String,
      required: true
    },
    unit: {
      type: String,
      default: ''
    },
    color: {
      type: String,
      default: '#42b983'
    },
    minYScale: {
      type: Number,
      default: null
    }
  },
  setup(props) {
    const chartContainer = ref(null)
    
    const drawChart = () => {
      if (!chartContainer.value || props.data.length === 0) return
      
      // Clear previous chart if it exists
      d3.select(chartContainer.value).selectAll('*').remove()
      
      // Set dimensions
      const margin = { top: 20, right: 30, bottom: 50, left: 50 }
      const width = chartContainer.value.clientWidth - margin.left - margin.right
      const height = 300 - margin.top - margin.bottom
      
      // Create SVG
      const svg = d3.select(chartContainer.value)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`)
      
      // Create scales
      // Calculate the exact width for each bar with no padding
      const barCount = props.data.length;
      const barWidth = Math.max(1, Math.floor(width / barCount)); // Minimum 1px bar width
      
      // Create a mapping of timestamps to indices for position calculation
      const timestampIndices = {};
      props.data.forEach((d, i) => {
        timestampIndices[d.timestamp] = i;
      });
      
      // Create a proper d3 scale for x-axis that spans full width
      // Create array of timestamps for domain
      const timestamps = props.data.map(d => d.timestamp);
      
      const x = d3.scaleBand()
        .range([0, width])
        .domain(timestamps)
        .padding(0);
      
      // Function to get bar width
      x.bandwidth = () => Math.max(1, width / barCount);
      
      // Determine Y axis scale with custom min
      let yMax = d3.max(props.data, d => d.value) * 1.1
      
      // Apply minimum scale if provided for any metric
      if (props.minYScale) {
        yMax = Math.max(yMax, props.minYScale)
      }
      
      const y = d3.scaleLinear()
        .domain([0, yMax])
        .range([height, 0])
      
      // Create time formatter for X axis based on data time range
      let xAxisFormat;
      if (props.data.length > 0) {
        // Sort data to ensure we get correct time range
        const sortedByTime = [...props.data].sort((a, b) => a.timestamp - b.timestamp);
        const timeSpan = sortedByTime[sortedByTime.length - 1].timestamp - sortedByTime[0].timestamp;
        const hours = timeSpan / (1000 * 60 * 60);
        
        if (hours <= 3) {
          // 3-hour view: show hour:minute
          xAxisFormat = d3.timeFormat("%H:%M");
        } else if (hours <= 24) {
          // 12 & 24-hour views: show hour:minute
          xAxisFormat = d3.timeFormat("%H:%M");
        } else if (hours <= 72) {
          // 3-day view: show month/day hour
          xAxisFormat = d3.timeFormat("%m/%d %H:%M");
        } else {
          // 7-day view: show month/day hour
          xAxisFormat = d3.timeFormat("%m/%d %H:%M");
        }
      } else {
        xAxisFormat = d3.timeFormat("%H:%M");
      }
      
      // Create X axis with adaptive tick intervals based on data range
      // Determine the time range covered by the data
      const sortedData = [...props.data].sort((a, b) => a.timestamp - b.timestamp);
      const startDate = sortedData[0].timestamp;
      const endDate = sortedData[sortedData.length - 1].timestamp;
      const hoursDiff = (endDate - startDate) / (1000 * 60 * 60);
      
      // Determine appropriate number of ticks based on time range
      let tickCount;
      if (hoursDiff <= 3) {
        // 3-hour view: ~12 labels (every 15 min)
        tickCount = 12;
      } else if (hoursDiff <= 12) {
        // 12-hour view: ~12 labels (every hour)
        tickCount = 12;
      } else if (hoursDiff <= 24) {
        // 24-hour view: ~12 labels (every 2 hours)
        tickCount = 12;
      } else if (hoursDiff <= 72) {
        // 3-day view: ~12 labels (every 6 hours)
        tickCount = 12;
      } else {
        // 7-day view: ~14 labels (every 12 hours)
        tickCount = 14;
      }
      
      // Calculate tick interval based on data points
      const tickInterval = Math.max(1, Math.floor(props.data.length / tickCount));
      
      // Generate evenly spaced tick indices
      const tickIndices = [];
      
      // Always include the first point
      tickIndices.push(0);
      
      // Add regularly spaced ticks
      for (let i = tickInterval; i < props.data.length - 1; i += tickInterval) {
        tickIndices.push(i);
      }
      
      // Add the last point if not already included and not too close to previous
      const lastIndex = props.data.length - 1;
      if (!tickIndices.includes(lastIndex) && 
          (tickIndices.length === 0 || lastIndex - tickIndices[tickIndices.length - 1] > tickInterval / 2)) {
        tickIndices.push(lastIndex);
      }
      
      // Create a custom axis
      const xAxis = g => {
        g.attr('transform', `translate(0,${height})`)
         .call(g => {
           // Draw the axis line
           g.append('path')
            .attr('stroke', '#ddd')
            .attr('d', `M0.5,0.5H${width + 0.5}`);
           
           // Add the ticks and labels
           tickIndices.forEach(i => {
             if (i < props.data.length) {
               const dataPoint = props.data[i];
               
               // Draw the tick
               g.append('line')
                .attr('stroke', '#ddd')
                .attr('x1', x(dataPoint.timestamp) + x.bandwidth()/2)
                .attr('x2', x(dataPoint.timestamp) + x.bandwidth()/2)
                .attr('y1', 0)
                .attr('y2', 6);
               
               // Add the label with time format
               g.append('text')
                .attr('fill', '#666')
                .attr('x', x(dataPoint.timestamp) + x.bandwidth()/2)
                .attr('y', 9)
                .attr('dy', '0.71em')
                .attr('text-anchor', 'middle')
                .text(xAxisFormat(dataPoint.timestamp))
                .style('font-size', '10px')
                .attr('transform', 'rotate(-45)')
                .attr('transform-origin', `${x(dataPoint.timestamp) + x.bandwidth()/2}px 9px`);
             }
           });
         });
      };
      
      // Draw X axis
      svg.append('g')
        .call(xAxis);
      
      // Draw Y axis
      svg.append('g')
        .call(d3.axisLeft(y))
      
      // Add Y axis label
      svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 0 - margin.left)
        .attr('x', 0 - (height / 2))
        .attr('dy', '1em')
        .style('text-anchor', 'middle')
        .style('fill', '#666')
        .text(`${props.metric} (${props.unit})`)
      
      // Draw bars
      const bars = svg.selectAll('.bar')
        .data(props.data)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.timestamp))
        .attr('width', x.bandwidth())
        .attr('y', d => y(d.value))
        .attr('height', d => height - y(d.value))
        .attr('fill', props.color)
        .attr('opacity', 0.8)
        .attr('shape-rendering', 'crispEdges')
        .attr('stroke', 'rgba(255,255,255,0.1)')
        .attr('stroke-width', 0.5)
      
      // Add tooltip and interaction
      const tooltip = d3.select('body')
        .append('div')
        .attr('class', 'chart-tooltip')
        .style('position', 'absolute')
        .style('background', 'rgba(0,0,0,0.7)')
        .style('color', 'white')
        .style('padding', '8px')
        .style('border-radius', '4px')
        .style('font-size', '12px')
        .style('pointer-events', 'none')
        .style('opacity', 0)
      
      // Add invisible rect for mouse tracking
      const mouseArea = svg.append('rect')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', 'none')
        .attr('pointer-events', 'all')
      
      // Add tooltips to bars instead of hover line
      svg.selectAll('.bar')
        .on('mouseover', function(event, d) {
          d3.select(this)
            .attr('opacity', 1)
            .attr('stroke', '#333')
            .attr('stroke-width', 1)
            .attr('filter', 'brightness(1.2)')
          
          tooltip.transition().duration(200).style('opacity', 0.9)
          tooltip.html(`
            <div>
              <div>${new Date(d.timestamp).toLocaleString()}</div>
              <div>${props.metric}: <strong>${d.value.toFixed(2)} ${props.unit}</strong></div>
            </div>
          `)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px')
        })
        .on('mousemove', function(event) {
          tooltip
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px')
        })
        .on('mouseout', function() {
          d3.select(this)
            .attr('opacity', 0.8)
            .attr('stroke', 'rgba(255,255,255,0.1)')
            .attr('stroke-width', 0.5)
            .attr('filter', null)
          
          tooltip.transition().duration(500).style('opacity', 0)
        })
      
      // We don't need the mouseArea for bar charts since we added interactivity to bars
      mouseArea.remove()
    }
    
    // Draw chart on mount
    onMounted(() => {
      drawChart()
      
      // Handle window resize
      window.addEventListener('resize', drawChart)
    })
    
    // Clean up event listener on unmount
    onBeforeUnmount(() => {
      window.removeEventListener('resize', drawChart)
      // Remove tooltip
      d3.selectAll('.chart-tooltip').remove()
    })
    
    // Redraw chart when data changes
    watch(() => props.data, () => {
      drawChart()
    }, { deep: true })
    
    return {
      chartContainer
    }
  }
}
</script>

<style scoped>
.network-chart-container {
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
  fill: #666;
}

/* Firefox-specific fixes */
@-moz-document url-prefix() {
  .chart rect.bar {
    shape-rendering: crispEdges;
  }
}
</style>
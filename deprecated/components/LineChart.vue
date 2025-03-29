<template>
  <div class="line-chart-container">
    <div ref="chartContainer" class="chart"></div>
  </div>
</template>

<script>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as d3 from 'd3'

export default {
  name: 'LineChart',
  props: {
    chartData: {
      type: Array,
      required: true
    },
    chartLabels: {
      type: Array,
      required: true
    },
    minYScale: {
      type: Number,
      default: null
    }
  },
  setup(props) {
    const chartContainer = ref(null)
    let chart = null
    
    const drawChart = () => {
      if (!chartContainer.value || props.chartData.length === 0) return
      
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
      const barCount = props.chartLabels.length;
      const barWidth = Math.max(1, Math.floor(width / barCount)); // Minimum 1px bar width
      
      // Create proper d3 scale for x-axis that spans full width
      const x = d3.scaleBand()
        .range([0, width])
        .domain(props.chartLabels)
        .padding(0);
      
      // Function to get bar width
      x.bandwidth = () => Math.max(1, width / barCount);
      
      // Determine Y axis scale with custom min
      let yMax = d3.max(props.chartData) * 1.1
      
      // Apply minimum scale if provided
      if (props.minYScale) {
        yMax = Math.max(yMax, props.minYScale)
      }
      
      const y = d3.scaleLinear()
        .domain([0, yMax])
        .range([height, 0])
      
      // Create X axis with custom scale and adaptive tick intervals based on data density
      // Determine the time range covered by the data - use proxy dates for calculation
      // Note: chartLabels are already formatted as strings like "12:30" or "5/22 14:30"
      // We create proxy date objects just to calculate the time range
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      
      // Check format of labels (whether they include date or just time)
      const hasDateComponent = props.chartLabels[0].includes('/');
      
      // Create proxy dates for time difference calculation
      let startDate, endDate;
      
      if (hasDateComponent) {
        // If labels contain dates like "5/22 14:30"
        const firstParts = props.chartLabels[0].split(' ');
        const lastParts = props.chartLabels[props.chartLabels.length - 1].split(' ');
        
        const firstDateParts = firstParts[0].split('/');
        const lastDateParts = lastParts[0].split('/');
        
        const firstMonth = parseInt(firstDateParts[0]) - 1; // JS months are 0-based
        const firstDay = parseInt(firstDateParts[1]);
        const firstTime = firstParts[1];
        
        const lastMonth = parseInt(lastDateParts[0]) - 1;
        const lastDay = parseInt(lastDateParts[1]);
        const lastTime = lastParts[1];
        
        startDate = new Date(now.getFullYear(), firstMonth, firstDay);
        startDate.setHours(...firstTime.split(':').map(Number));
        
        endDate = new Date(now.getFullYear(), lastMonth, lastDay);
        endDate.setHours(...lastTime.split(':').map(Number));
      } else {
        // If labels are just times like "14:30"
        // Assume all timestamps are from today for calculation purposes
        startDate = new Date(today);
        endDate = new Date(today);
        
        const startTimeParts = props.chartLabels[0].split(':').map(Number);
        const endTimeParts = props.chartLabels[props.chartLabels.length - 1].split(':').map(Number);
        
        startDate.setHours(startTimeParts[0], startTimeParts[1]);
        endDate.setHours(endTimeParts[0], endTimeParts[1]);
        
        // If end time is earlier than start time, it means we crossed midnight
        if (endDate < startDate) {
          endDate.setDate(endDate.getDate() + 1);
        }
      }
      const hoursDiff = (endDate - startDate) / (1000 * 60 * 60);
      
      // Adaptive tick spacing based on time range
      let tickInterval;
      if (hoursDiff <= 3) {
        // 3-hour view: labels every 15 minutes (show 12 labels)
        tickInterval = Math.max(1, Math.floor(props.chartLabels.length / 12));
      } else if (hoursDiff <= 12) {
        // 12-hour view: labels every hour (show 12 labels)
        tickInterval = Math.max(1, Math.floor(props.chartLabels.length / 12));
      } else if (hoursDiff <= 24) {
        // 24-hour view: labels every 2 hours (show 12 labels)
        tickInterval = Math.max(1, Math.floor(props.chartLabels.length / 12));
      } else if (hoursDiff <= 72) {
        // 3-day view: labels every 6 hours (show 12 labels)
        tickInterval = Math.max(1, Math.floor(props.chartLabels.length / 12));
      } else {
        // 7-day view: labels every 12 hours (show 14 labels)
        tickInterval = Math.max(1, Math.floor(props.chartLabels.length / 14));
      }
      
      // Make sure we display both the first and last label
      const tickIndices = []
      
      // Add the first label
      tickIndices.push(0);
      
      // Add regularly spaced labels
      for (let i = tickInterval; i < props.chartLabels.length - 1; i += tickInterval) {
        tickIndices.push(i);
      }
      
      // Add the last label if it's not already included and not too close to the previous one
      const lastIndex = props.chartLabels.length - 1;
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
             if (i < props.chartLabels.length) {
               const label = props.chartLabels[i];
               
               // Draw the tick
               g.append('line')
                .attr('stroke', '#ddd')
                .attr('x1', x(label) + x.bandwidth()/2)
                .attr('x2', x(label) + x.bandwidth()/2)
                .attr('y1', 0)
                .attr('y2', 6);
               
               // Add the label
               g.append('text')
                .attr('fill', '#666')
                .attr('x', x(label) + x.bandwidth()/2)
                .attr('y', 9)
                .attr('dy', '0.71em')
                .attr('text-anchor', 'middle')
                .text(label)
                .style('font-size', '10px')
                .attr('transform', 'rotate(-45)')
                .attr('transform-origin', `${x(label) + x.bandwidth()/2}px 9px`);
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
        .text('Latency (ms)')
      
      // Draw bars
      const bars = svg.selectAll('.bar')
        .data(props.chartData)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', (d, i) => x(props.chartLabels[i]))
        .attr('width', x.bandwidth())
        .attr('y', d => y(d))
        .attr('height', d => height - y(d))
        .attr('fill', '#42b983')
        .attr('opacity', 0.8)
        .attr('shape-rendering', 'crispEdges')
        .attr('stroke', 'rgba(255,255,255,0.1)')
        .attr('stroke-width', 0.5)
      
      // Add tooltip
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
      
      // Add interactivity to bars
      bars.on('mouseover', function(event, d) {
          const i = props.chartData.indexOf(d)
          const label = props.chartLabels[i]
          
          d3.select(this)
            .attr('opacity', 1)
            .attr('stroke', '#333')
            .attr('stroke-width', 1)
            .attr('filter', 'brightness(1.2)')
          
          tooltip.transition().duration(200).style('opacity', 0.9)
          tooltip.html(`
            <div>
              <div>${label}</div>
              <div>Latency: <strong>${d.toFixed(2)} ms</strong></div>
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
      d3.selectAll('.chart-tooltip').remove()
    })
    
    // Redraw chart when data changes
    watch(() => [props.chartData, props.chartLabels], () => {
      drawChart()
    }, { deep: true })
    
    return {
      chartContainer
    }
  }
}
</script>

<style scoped>
.line-chart-container {
  width: 100%;
  margin: 0 auto;
}

.chart {
  width: 100%;
  height: 300px;
}

/* Firefox-specific fixes */
@-moz-document url-prefix() {
  .chart rect.bar {
    shape-rendering: crispEdges;
  }
}
</style>
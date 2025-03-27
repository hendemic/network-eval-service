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
      const x = d3.scaleTime()
        .domain(d3.extent(props.data, d => d.timestamp))
        .range([0, width])
      
      const y = d3.scaleLinear()
        .domain([0, d3.max(props.data, d => d.value) * 1.1])
        .range([height, 0])
      
      // Create line
      const line = d3.line()
        .x(d => x(d.timestamp))
        .y(d => y(d.value))
        .curve(d3.curveMonotoneX)
      
      // Create area
      const area = d3.area()
        .x(d => x(d.timestamp))
        .y0(height)
        .y1(d => y(d.value))
        .curve(d3.curveMonotoneX)
      
      // Draw X axis
      svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll('text')
        .style('text-anchor', 'end')
        .attr('dx', '-.8em')
        .attr('dy', '.15em')
        .attr('transform', 'rotate(-45)')
      
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
      
      // Draw area
      svg.append('path')
        .datum(props.data)
        .attr('fill', props.color)
        .attr('fill-opacity', 0.1)
        .attr('d', area)
      
      // Draw line
      svg.append('path')
        .datum(props.data)
        .attr('fill', 'none')
        .attr('stroke', props.color)
        .attr('stroke-width', 2)
        .attr('d', line)
      
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
      
      // Add hover line
      const hoverLine = svg.append('line')
        .attr('class', 'hover-line')
        .attr('y1', 0)
        .attr('y2', height)
        .style('stroke', '#999')
        .style('stroke-width', 1)
        .style('stroke-dasharray', '3,3')
        .style('opacity', 0)
      
      // Mouse move handler
      mouseArea.on('mousemove', function(event) {
        const mouse = d3.pointer(event)
        const mouseX = mouse[0]
        
        // Find closest data point
        const bisect = d3.bisector(d => d.timestamp).left
        const x0 = x.invert(mouseX)
        const i = bisect(props.data, x0, 1)
        const d0 = props.data[i - 1]
        const d1 = props.data[i] || d0
        const d = x0 - d0.timestamp > d1.timestamp - x0 ? d1 : d0
        
        // Show tooltip
        tooltip.transition().duration(200).style('opacity', 0.9)
        tooltip.html(`
          <div>
            <div>${new Date(d.timestamp).toLocaleString()}</div>
            <div>${props.metric}: <strong>${d.value.toFixed(2)} ${props.unit}</strong></div>
          </div>
        `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px')
        
        // Move hover line
        hoverLine
          .attr('x1', x(d.timestamp))
          .attr('x2', x(d.timestamp))
          .style('opacity', 1)
      })
      
      mouseArea.on('mouseout', function() {
        tooltip.transition().duration(500).style('opacity', 0)
        hoverLine.style('opacity', 0)
      })
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
</style>
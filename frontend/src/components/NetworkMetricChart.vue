<template>
  <div class="network-metric-chart-container">
    <div ref="chartContainer" class="chart"></div>
    <Tooltip 
      :visible="tooltipVisible" 
      :x="tooltipX" 
      :y="tooltipY"
    >
      <div v-if="tooltipData">
        <div style="font-weight: bold; margin-bottom: 4px;">
          {{ tooltipData.date }} {{ tooltipData.time }}
        </div>
        <div>
          {{ metric }}: <strong>{{ tooltipData.value }} {{ unit }}</strong>
        </div>
      </div>
    </Tooltip>
  </div>
</template>

<script>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as d3 from 'd3'
import Tooltip from './Tooltip.vue'

export default {
  name: 'NetworkMetricChart',
  components: {
    Tooltip
  },
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
    
    // Tooltip state
    const tooltipVisible = ref(false)
    const tooltipX = ref(0)
    const tooltipY = ref(0)
    const tooltipData = ref(null)
    
    const drawChart = () => {
      // Exit if no container or data
      if (!chartContainer.value || !props.data || props.data.length === 0) return
      
      // Clear previous chart
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
      
      // Process data and ensure timestamps are Date objects
      const processedData = props.data.map(d => ({
        timestamp: d.timestamp instanceof Date ? d.timestamp : new Date(d.timestamp),
        value: d.value
      })).sort((a, b) => a.timestamp - b.timestamp)
      
      // Calculate time range for the chart
      const latestTimestamp = d3.max(processedData, d => d.timestamp)
      const startTime = new Date(latestTimestamp)
      startTime.setHours(startTime.getHours() - props.selectedHours)
      
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
      
      // Draw axes
      svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale).tickSize(0).tickFormat(''))
      
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
      
      // Filter data to the selected time range
      const visibleData = processedData.filter(d => 
        d.timestamp >= startTime && d.timestamp <= latestTimestamp
      )
      
      // Debug log for each chart
      console.log(`${props.metric} chart data:`, {
        total: processedData.length,
        visible: visibleData.length,
        timeRange: `${startTime.toLocaleTimeString()} - ${latestTimestamp.toLocaleTimeString()}`
      })
      
      // Calculate bar width
      const barWidth = Math.max(1, (width / Math.max(1, visibleData.length)) * 0.8)
      
      // Draw the bars
      svg.selectAll('.bar')
        .data(visibleData)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', d => xScale(d.timestamp) - (barWidth / 2))
        .attr('width', barWidth)
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
          
          // Make sure we have a valid timestamp
          const date = new Date(d.timestamp)
          
          // Update tooltip data
          tooltipData.value = {
            date: date.toLocaleDateString(),
            time: date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'}),
            value: d.value.toFixed(2)
          }
          
          // Position and show tooltip - use clientX and clientY for viewport-relative positioning
          tooltipX.value = event.clientX + 10
          tooltipY.value = event.clientY - 28
          tooltipVisible.value = true
        })
        .on('mousemove', function(event) {
          // Update tooltip position using client coordinates (viewport-relative)
          tooltipX.value = event.clientX + 10
          tooltipY.value = event.clientY - 28
        })
        .on('mouseout', function() {
          // Reset bar style
          d3.select(this)
            .attr('opacity', 0.8)
            .attr('stroke', 'none')
          
          // Hide tooltip
          tooltipVisible.value = false
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
      chartContainer,
      tooltipVisible,
      tooltipX,
      tooltipY,
      tooltipData
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
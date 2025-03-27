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
      const x = d3.scaleBand()
        .domain(props.chartLabels)
        .range([0, width])
        .padding(0.1)
      
      const y = d3.scaleLinear()
        .domain([0, d3.max(props.chartData) * 1.1])
        .range([height, 0])
      
      // Create line
      const line = d3.line()
        .x((d, i) => x(props.chartLabels[i]) + x.bandwidth() / 2)
        .y(d => y(d))
        .curve(d3.curveMonotoneX)
      
      // Draw X axis
      svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x).tickValues(x.domain().filter((d, i) => i % 5 === 0)))
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
        .text('Latency (ms)')
      
      // Draw line
      svg.append('path')
        .datum(props.chartData)
        .attr('fill', 'none')
        .attr('stroke', '#42b983')
        .attr('stroke-width', 2)
        .attr('d', line)
      
      // Add dots
      svg.selectAll('dot')
        .data(props.chartData)
        .enter()
        .append('circle')
        .attr('cx', (d, i) => x(props.chartLabels[i]) + x.bandwidth() / 2)
        .attr('cy', d => y(d))
        .attr('r', 3)
        .attr('fill', '#42b983')
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
</style>
<template>
  <div class="dashboard">
    <!-- Global tooltip component -->
    <Tooltip ref="tooltipRef" />
    
    <div class="header">
      <h2>Network Status Dashboard</h2>
      <nav-menu @refresh="refreshData" />
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else-if="error && !error.includes('404')" class="error">
      {{ error }}
    </div>
    
    <div v-else-if="error && error.includes('404')" class="waiting">
      <div class="waiting-icon">⏱️</div>
      <div>Waiting for first network test data...</div>
      <div class="waiting-subtext">Initial test may take 60 seconds or longer depending on your test configuration</div>
    </div>

    <div v-else-if="stats">
      <!-- Latest stats section -->
      <div class="card stats-overview">
        <h3>Current Network Status</h3>
        <p class="last-updated">
          Last updated: {{ formatDateToLocaleString(stats.latest.timestamp) }}
        </p>

        <div class="stats-grid">
          <network-metric
            :value="stats.latest.avg_latency"
            metric-type="latency"
            label="Average Latency"
          />
          
          <network-metric
            :value="stats.latest.jitter"
            metric-type="jitter"
            label="Jitter"
          />
          
          <network-metric
            :value="stats.latest.packet_loss"
            metric-type="packetLoss"
            label="Packet Loss"
          />
        </div>
      </div>

      <!-- 24 hour overview -->
      <div class="card">
        <h3>24 Hour Overview</h3>
        <div class="stats-grid">
          <network-metric
            :value="stats.day_stats.avg_latency"
            metric-type="latency"
            label="Avg Latency (24h)"
          />
          
          <network-metric
            :value="stats.day_stats.avg_jitter"
            metric-type="jitter"
            label="Avg Jitter (24h)"
          />
          
          <network-metric
            :value="stats.day_stats.max_latency"
            metric-type="latency"
            label="Max Latency (24h)"
          />
          
          <network-metric
            :value="stats.day_stats.max_packet_loss"
            metric-type="packetLoss"
            label="Max Packet Loss (24h)"
          />
        </div>
      </div>

      <!-- Network Performance Charts -->
      <div class="card performance-section">
        <div class="section-header">
          <h3>Network Performance</h3>
          <div class="time-filters">
            <button
              v-for="(option, index) in timeOptions"
              :key="index"
              @click="setTimeRange(option.hours)"
              :class="{ 
                active: selectedHours === option.hours,
                disabled: !hasEnoughDataForTimeRange(option.hours)
              }"
              class="time-btn"
              :disabled="!hasEnoughDataForTimeRange(option.hours)"
              :ref="el => initButtonTooltip(el, option.hours)"
            >
              {{ option.label }}
            </button>
          </div>
        </div>

        <!-- Latency Chart -->
        <div class="chart-card">
          <h4>Network Latency</h4>
          <network-metric-chart
            v-if="latencyData && latencyData.length > 0"
            :data="latencyData"
            metric="Latency"
            unit="ms"
            :minYScale="50"
            :selectedHours="selectedHours"
          />
          <p v-else>Not enough data to display chart</p>
        </div>

        <!-- Network Jitter Chart -->
        <div class="chart-card">
          <h4>Network Jitter</h4>
          <network-metric-chart
            v-if="jitterData && jitterData.length > 0"
            :data="jitterData"
            metric="Jitter"
            unit="ms"
            :minYScale="10"
            :selectedHours="selectedHours"
          />
          <p v-else>Not enough data to display chart</p>
        </div>

        <!-- Packet Loss Chart -->
        <div class="chart-card">
          <h4>Packet Loss</h4>
          <network-metric-chart
            v-if="packetLossData && packetLossData.length > 0"
            :data="packetLossData"
            metric="Packet Loss"
            unit="%"
            :minYScale="5"
            :selectedHours="selectedHours"
          />
          <p v-else>Not enough data to display chart</p>
        </div>
      </div>
    </div>

    <div v-else class="waiting">
      <div class="waiting-icon">⏱️</div>
      <div>Waiting for network test data...</div>
      <div class="waiting-subtext">Please ensure tests are properly configured</div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useStore } from "vuex";
import NetworkMetricChart from "../components/NetworkMetricChart.vue";
import NavMenu from "../components/NavMenu.vue";
import NetworkMetric from "../components/NetworkMetric.vue";
import Tooltip from "../components/Tooltip.vue";
import { useTooltip } from "../composables/useTooltip.js";
import { useChartData } from "../composables/useChartData.js";
import { useTimeRange } from "../composables/useTimeRange.js";
import { formatDateToLocaleString } from "../utils/dateUtils.js";

export default {
  name: "Dashboard",
  components: {
    NetworkMetricChart,
    NavMenu,
    NetworkMetric,
    Tooltip
  },
  setup() {
    const store = useStore();
    const refreshInterval = ref(null);
    
    // Initialize tooltip system
    const tooltipRef = ref(null);
    const { attachDisabledTooltip, register } = useTooltip();
    
    // Fetch data on component mount
    onMounted(() => {
      fetchData();
      
      // Register the tooltip ref with the tooltip system after it's mounted
      nextTick(() => {
        if (tooltipRef.value) {
          register(tooltipRef.value);
        }
      });

      // Auto-refresh every minute
      refreshInterval.value = setInterval(() => {
        fetchData();
      }, 60000);
    });

    // Clear interval on component unmount
    onBeforeUnmount(() => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value);
      }
    });

    const fetchData = async () => {
      // Request enough data for all time filters
      const requestConfig = {
        hours: 168, // 7 days to cover all time filters
        limit: 1000
      };
      
      await Promise.all([
        store.dispatch("fetchStats"),
        store.dispatch("fetchPingResults", requestConfig),
      ]);
    };

    const refreshData = () => {
      fetchData();
    };
    
    // Helper function to calculate the data span in hours
    const calculateDataSpan = () => {
      const data = store.getters.latencyData;
      if (!data || data.length < 2) return 0;
      
      // Sort data by timestamp to accurately measure time span
      const sortedData = [...data].sort((a, b) => a.timestamp - b.timestamp);
      
      // Calculate the time span of our current data in hours
      const oldestTimestamp = sortedData[0].timestamp;
      const newestTimestamp = sortedData[sortedData.length - 1].timestamp;
      return (newestTimestamp - oldestTimestamp) / (1000 * 60 * 60);
    };
    
    // Initialize time range management
    const timeRange = useTimeRange({
      getDataSpan: calculateDataSpan,
      defaultRange: 3
    });
    
    // Function to initialize tooltips for time filter buttons
    const initButtonTooltip = (element, hours) => {
      if (!element) return;
      
      // Add tooltip to all buttons, but it will only show when they're disabled
      attachDisabledTooltip(element, timeRange.getTimeRangeTooltip(hours));
      
      // Return the button element for Vue's ref handling
      return element;
    };
    
    // Initialize chart data composables for each metric type
    const latencyChartData = useChartData({
      getData: () => store.getters.latencyData,
      selectedHours: timeRange.selectedHours
    });
    
    const jitterChartData = useChartData({
      getData: () => store.getters.jitterData,
      selectedHours: timeRange.selectedHours
    });
    
    const packetLossChartData = useChartData({
      getData: () => store.getters.packetLossData,
      selectedHours: timeRange.selectedHours
    });
    
    // Create a wrapper for the time range availability check
    const hasEnoughDataForTimeRange = (hours) => {
      return timeRange.isTimeRangeAvailable(hours);
    };
    
    return {
      loading: computed(() => store.state.loading),
      error: computed(() => store.state.error),
      stats: computed(() => store.state.stats),
      
      // Chart data from our composables
      latencyData: computed(() => store.getters.latencyData),
      jitterData: computed(() => store.getters.jitterData),
      packetLossData: computed(() => store.getters.packetLossData),
      
      // Time range controls - provide both raw and processed options
      timeOptions: timeRange.timeOptions,
      selectedHours: timeRange.selectedHours,
      setTimeRange: timeRange.setTimeRange,
      refreshData,
      
      // Formatting helpers
      formatDateToLocaleString,
      hasEnoughDataForTimeRange,
      
      // Store reference
      store,
      
      // Tooltip related
      tooltipRef,
      initButtonTooltip
    };
  },
};
</script>

<style scoped>
/* Component-specific styles only - shared styles are now in CSS modules */
</style>

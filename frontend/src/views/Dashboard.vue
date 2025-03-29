<template>
  <div class="dashboard">
    <!-- Global tooltip component -->
    <Tooltip ref="tooltipRef" />
    
    <div class="header">
      <h2>Network Status Dashboard</h2>
      <nav-menu @refresh="refreshData" />
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else-if="stats">
      <!-- Latest stats section -->
      <div class="card stats-overview">
        <h3>Current Network Status</h3>
        <p class="last-updated">
          Last updated: {{ formatDate(stats.latest.timestamp) }}
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

    <div v-else class="no-data">
      No data available. Ensure the network tests are running.
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
    const selectedHours = ref(3);
    
    // Initialize tooltip system
    const tooltipRef = ref(null);
    const { attachDisabledTooltip, register } = useTooltip();

    const timeOptions = [
      { label: "3 Hours", hours: 3 },
      { label: "12 Hours", hours: 12 },
      { label: "24 Hours", hours: 24 },
      { label: "3 Days", hours: 72 },
      { label: "7 Days", hours: 168 },
    ];

    // Function to initialize tooltips for time filter buttons
    const initButtonTooltip = (element, hours) => {
      if (!element) return;
      
      // Add tooltip to all buttons, but it will only show when they're disabled
      attachDisabledTooltip(element, 'Not enough data available for this time range');
      
      // Return the button element for Vue's ref handling
      return element;
    };
    
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

    const setTimeRange = (hours) => {
      selectedHours.value = hours;
      fetchData();
    };

    const refreshData = () => {
      fetchData();
    };
    
    // Check if there's enough data for a specific time range
    const hasEnoughDataForTimeRange = (hours) => {
      // Get the current data points directly from the getter
      const data = store.getters.latencyData;
      if (!data || data.length === 0) return false;
      
      // Sort data by timestamp to accurately measure time span
      const sortedData = [...data].sort((a, b) => a.timestamp - b.timestamp);
      
      // Calculate the time span of our current data in hours
      const oldestTimestamp = sortedData[0].timestamp;
      const newestTimestamp = sortedData[sortedData.length - 1].timestamp;
      const spanHours = (newestTimestamp - oldestTimestamp) / (1000 * 60 * 60);
      
      // Find the current time option index
      const currentOptionIndex = timeOptions.findIndex(option => option.hours === hours);
      
      // Enable the button if:
      // 1. It's one of the first two time options (3h, 12h) - always enabled
      // 2. OR we have enough data to justify this scale (at least more than the previous scale)
      if (currentOptionIndex <= 1) {
        // Always enable 3h and 12h options
        return true;
      } else if (currentOptionIndex > 1) {
        // For larger time scales, check if we have more data than would justify the previous scale
        const previousScale = timeOptions[currentOptionIndex - 1].hours;
        return spanHours > previousScale;
      }
      
      // Default fallback
      return false;
    };

    // Format date for display
    const formatDate = (dateString) => {
      // Add 'Z' to indicate this is UTC time
      const date = new Date(dateString + "Z");
      return date.toLocaleString();
    };

    // These are now handled by the NetworkMetric component

    // Modified to use structured data format for latency
    // This improves consistency with other metrics
    const chartData = computed(() => {
      const latencyData = store.getters.latencyData;
      if (latencyData.length === 0) return [];
      
      // Use the data directly rather than separate arrays
      return latencyData.map((item) => item.value);
    });

    const chartLabels = computed(() => {
      const latencyData = store.getters.latencyData;
      if (latencyData.length === 0) return [];
      
      // Format labels based on time range
      return latencyData.map((item) => {
        const date = item.timestamp;
        // Format differently depending on time range
        if (selectedHours.value <= 12) {
          // For shorter time periods, show hours:minutes with nicely formatted times
          return `${date.getHours().toString().padStart(2, "0")}:${date.getMinutes().toString().padStart(2, "0")}`;
        } else if (selectedHours.value <= 72) {
          // For 1-3 day view, show day and hour
          return `${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getDate().toString().padStart(2, "0")} ${date.getHours().toString().padStart(2, "0")}:00`;
        } else {
          // For 7-day view, show month/day and hour
          return `${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getDate().toString().padStart(2, "0")} ${date.getHours().toString().padStart(2, "0")}:00`;
        }
      });
    });

    return {
      loading: computed(() => store.state.loading),
      error: computed(() => store.state.error),
      stats: computed(() => store.state.stats),
      chartData,
      chartLabels,
      latencyData: computed(() => store.getters.latencyData),
      jitterData: computed(() => store.getters.jitterData),
      packetLossData: computed(() => store.getters.packetLossData),
      timeOptions,
      selectedHours,
      setTimeRange,
      refreshData,
      formatDate,
      hasEnoughDataForTimeRange,
      store,
      // Tooltip related
      tooltipRef,
      initButtonTooltip
    };
  },
};
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
}

/* Mobile responsive styling */
@media (max-width: 768px) {
  .header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}

.loading,
.error,
.no-data {
  text-align: center;
  padding: var(--space-xl);
  background: var(--bg-white);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
}

.error {
  color: var(--brand-danger);
}

.stats-overview {
  margin-bottom: var(--space-xl);
}

.last-updated {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin-bottom: var(--space-md);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-lg);
}

/* Stat-item styles now in the NetworkMetric component */

.performance-section {
  margin-top: var(--space-xl);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
  flex-wrap: wrap;
  gap: var(--space-md);
}

.time-filters {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.time-btn {
  padding: var(--space-xs) var(--space-sm);
  background-color: var(--bg-light);
  border: none;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--filter-inactive-color);
}

.time-btn.active {
  background-color: var(--brand-primary);
  color: var(--text-white);
}

.time-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chart-card {
  margin-top: var(--space-xl);
  padding-top: var(--space-md);
  border-top: var(--border-width-thin) solid var(--border-light);
}

.chart-card h4 {
  margin-top: 0;
  margin-bottom: var(--space-md);
  color: var(--text-secondary);
}

/* Status color classes moved to NetworkMetric component */
</style>

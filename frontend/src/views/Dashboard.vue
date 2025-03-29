<template>
  <div class="dashboard">
    <h2>Network Status Dashboard</h2>
    
    <div v-if="loading" class="loading">
      Loading...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else-if="stats">
      <!-- Latest stats section -->
      <div class="card stats-overview">
        <h3>Current Network Status</h3>
        <p class="last-updated">Last updated: {{ formatDate(stats.latest.timestamp) }}</p>
        
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value" :class="getLatencyClass(stats.latest.avg_latency)">
              {{ stats.latest.avg_latency.toFixed(2) }} ms
            </div>
            <div class="stat-label">Average Latency</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value" :class="getJitterClass(stats.latest.jitter)">
              {{ stats.latest.jitter.toFixed(2) }} ms
            </div>
            <div class="stat-label">Jitter</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value" :class="getPacketLossClass(stats.latest.packet_loss)">
              {{ stats.latest.packet_loss.toFixed(2) }}%
            </div>
            <div class="stat-label">Packet Loss</div>
          </div>
        </div>
      </div>
      
      <!-- 24 hour overview -->
      <div class="card">
        <h3>24 Hour Overview</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value" :class="getLatencyClass(stats.day_stats.avg_latency)">
              {{ stats.day_stats.avg_latency.toFixed(2) }} ms
            </div>
            <div class="stat-label">Avg Latency (24h)</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value" :class="getJitterClass(stats.day_stats.avg_jitter)">
              {{ stats.day_stats.avg_jitter.toFixed(2) }} ms
            </div>
            <div class="stat-label">Avg Jitter (24h)</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value">
              {{ stats.day_stats.max_latency.toFixed(2) }} ms
            </div>
            <div class="stat-label">Max Latency (24h)</div>
          </div>
          
          <div class="stat-item">
            <div class="stat-value" :class="getPacketLossClass(stats.day_stats.max_packet_loss)">
              {{ stats.day_stats.max_packet_loss.toFixed(2) }}%
            </div>
            <div class="stat-label">Max Packet Loss (24h)</div>
          </div>
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
              :class="{ active: selectedHours === option.hours }"
              class="time-btn"
            >
              {{ option.label }}
            </button>
          </div>
        </div>
        
        <!-- Latency Chart -->
        <div class="chart-card">
          <h4>Network Latency</h4>
          <line-chart 
            v-if="chartData && chartData.length > 0"
            :chart-data="chartData" 
            :chart-labels="chartLabels"
          />
          <p v-else>Not enough data to display chart</p>
        </div>
        
        <!-- Network Jitter Chart -->
        <div class="chart-card">
          <h4>Network Jitter</h4>
          <network-chart 
            v-if="jitterData && jitterData.length > 0"
            :data="jitterData"
            metric="Jitter"
            unit="ms"
            color="#2c3e50"
          />
          <p v-else>Not enough data to display chart</p>
        </div>
        
        <!-- Packet Loss Chart -->
        <div class="chart-card">
          <h4>Packet Loss</h4>
          <network-chart 
            v-if="packetLossData && packetLossData.length > 0"
            :data="packetLossData"
            metric="Packet Loss"
            unit="%"
            color="#e74c3c"
          />
          <p v-else>Not enough data to display chart</p>
        </div>
      </div>
    </div>
    
    <div v-else class="no-data">
      No data available. Ensure the network tests are running.
    </div>
    
    <div class="actions">
      <router-link to="/history" class="btn">View Full History</router-link>
      <button @click="refreshData" class="btn">Refresh Data</button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useStore } from 'vuex'
import LineChart from '../components/LineChart.vue'
import NetworkChart from '../components/NetworkChart.vue'

export default {
  name: 'Dashboard',
  components: {
    LineChart,
    NetworkChart
  },
  setup() {
    const store = useStore()
    const refreshInterval = ref(null)
    const selectedHours = ref(3)
    
    const timeOptions = [
      { label: '3 Hours', hours: 3 },
      { label: '12 Hours', hours: 12 },
      { label: '24 Hours', hours: 24 },
      { label: '3 Days', hours: 72 },
      { label: '7 Days', hours: 168 }
    ]
    
    // Fetch data on component mount
    onMounted(() => {
      fetchData()
      
      // Auto-refresh every minute
      refreshInterval.value = setInterval(() => {
        fetchData()
      }, 60000)
    })
    
    // Clear interval on component unmount
    onBeforeUnmount(() => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
      }
    })
    
    const fetchData = async () => {
      await Promise.all([
        store.dispatch('fetchStats'),
        store.dispatch('fetchPingResults', { 
          hours: selectedHours.value, 
          limit: selectedHours.value * 60 // One data point per minute
        })
      ])
    }
    
    const setTimeRange = (hours) => {
      selectedHours.value = hours
      fetchData()
    }
    
    const refreshData = () => {
      fetchData()
    }
    
    // Format date for display
    const formatDate = (dateString) => {
      // Add 'Z' to indicate this is UTC time
      const date = new Date(dateString + 'Z');
      return date.toLocaleString();
    }
    
    // Compute class based on metric values
    const getLatencyClass = (value) => {
      if (value < 20) return 'status-excellent'
      if (value < 60) return 'status-good'
      if (value < 100) return 'status-fair'
      return 'status-poor'
    }
    
    const getJitterClass = (value) => {
      if (value < 5) return 'status-excellent'
      if (value < 15) return 'status-good'
      if (value < 30) return 'status-fair'
      return 'status-poor'
    }
    
    const getPacketLossClass = (value) => {
      if (value < 0.5) return 'status-excellent'
      if (value < 2) return 'status-good'
      if (value < 5) return 'status-fair'
      return 'status-poor'
    }
    
    // Chart data for the line chart
    const chartData = computed(() => {
      // Take all data points for the selected time range
      const latencyData = store.getters.latencyData
      if (latencyData.length === 0) return []
      
      // Sample the data to avoid overcrowding
      const sampleSize = Math.max(1, Math.floor(latencyData.length / 60))
      const sampledData = latencyData.filter((_, i) => i % sampleSize === 0)
      
      return sampledData.map(item => item.value)
    })
    
    const chartLabels = computed(() => {
      // Take all data points for the selected time range
      const latencyData = store.getters.latencyData
      if (latencyData.length === 0) return []
      
      // Sample the data to avoid overcrowding
      const sampleSize = Math.max(1, Math.floor(latencyData.length / 60))
      const sampledData = latencyData.filter((_, i) => i % sampleSize === 0)
      
      return sampledData.map(item => {
        const date = item.timestamp
        // Format differently depending on time range
        if (selectedHours.value <= 24) {
          return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
        } else {
          return `${date.getMonth()+1}/${date.getDate()} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
        }
      })
    })
    
    return {
      loading: computed(() => store.state.loading),
      error: computed(() => store.state.error),
      stats: computed(() => store.state.stats),
      chartData,
      chartLabels,
      jitterData: computed(() => store.getters.jitterData),
      packetLossData: computed(() => store.getters.packetLossData),
      timeOptions,
      selectedHours,
      setTimeRange,
      refreshData,
      formatDate,
      getLatencyClass,
      getJitterClass,
      getPacketLossClass
    }
  }
}
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.loading, .error, .no-data {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.error {
  color: #d9534f;
}

.stats-overview {
  margin-bottom: 2rem;
}

.last-updated {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-item {
  text-align: center;
}

.performance-section {
  margin-top: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.time-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.time-btn {
  padding: 0.4rem 0.8rem;
  background-color: #f1f1f1;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.time-btn.active {
  background-color: var(--primary-color);
  color: white;
}

.chart-card {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.chart-card h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #555;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn {
  display: inline-block;
  background-color: var(--primary-color);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  font-size: 1rem;
}

.btn:hover {
  background-color: #1a2530;
}

/* Status color classes */
.status-excellent {
  color: #28a745;
}

.status-good {
  color: #17a2b8;
}

.status-fair {
  color: #ffc107;
}

.status-poor {
  color: #dc3545;
}
</style>
<template>
  <div class="history">
    <h2>Network Test History</h2>
    
    <div class="controls">
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
    
    <div v-if="loading" class="loading">
      Loading...
    </div>
    
    <div v-else-if="error" class="error">
      {{ error }}
    </div>
    
    <div v-else>
      <div class="card chart-card">
        <h3>Network Latency</h3>
        <network-chart 
          v-if="latencyData.length > 0"
          :data="latencyData"
          metric="Latency"
          unit="ms"
          color="#42b983"
        />
        <p v-else>No data available for the selected time period</p>
      </div>
      
      <div class="card chart-card">
        <h3>Network Jitter</h3>
        <network-chart 
          v-if="jitterData.length > 0"
          :data="jitterData"
          metric="Jitter"
          unit="ms"
          color="#2c3e50"
        />
        <p v-else>No data available for the selected time period</p>
      </div>
      
      <div class="card chart-card">
        <h3>Packet Loss</h3>
        <network-chart 
          v-if="packetLossData.length > 0"
          :data="packetLossData"
          metric="Packet Loss"
          unit="%"
          color="#e74c3c"
        />
        <p v-else>No data available for the selected time period</p>
      </div>
      
      <div class="card">
        <h3>Raw Data</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Target</th>
              <th>Avg Latency (ms)</th>
              <th>Min Latency (ms)</th>
              <th>Max Latency (ms)</th>
              <th>Jitter (ms)</th>
              <th>Packet Loss (%)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="result in pingResults" :key="result.id">
              <td>{{ formatDate(result.timestamp) }}</td>
              <td>{{ result.target }}</td>
              <td>{{ result.avg_latency.toFixed(2) }}</td>
              <td>{{ result.min_latency.toFixed(2) }}</td>
              <td>{{ result.max_latency.toFixed(2) }}</td>
              <td>{{ result.jitter.toFixed(2) }}</td>
              <td>{{ result.packet_loss.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <div class="actions">
      <router-link to="/" class="btn">Back to Dashboard</router-link>
      <button @click="refreshData" class="btn">Refresh Data</button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import NetworkChart from '../components/NetworkChart.vue'

export default {
  name: 'History',
  components: {
    NetworkChart
  },
  setup() {
    const store = useStore()
    const selectedHours = ref(24)
    
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
    })
    
    const fetchData = async () => {
      await store.dispatch('fetchPingResults', { 
        hours: selectedHours.value,
        limit: 10000
      })
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
      return new Date(dateString + 'Z').toLocaleString();
    }
    
    return {
      loading: computed(() => store.state.loading),
      error: computed(() => store.state.error),
      pingResults: computed(() => store.state.pingResults),
      latencyData: computed(() => store.getters.latencyData),
      jitterData: computed(() => store.getters.jitterData),
      packetLossData: computed(() => store.getters.packetLossData),
      timeOptions,
      selectedHours,
      setTimeRange,
      refreshData,
      formatDate
    }
  }
}
</script>

<style scoped>
.history {
  width: 100%;
}

.controls {
  margin-bottom: 2rem;
}

.time-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.time-btn {
  padding: 0.5rem 1rem;
  background-color: #f1f1f1;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.time-btn.active {
  background-color: var(--primary-color);
  color: white;
}

.chart-card {
  margin-bottom: 2rem;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.error {
  color: #d9534f;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.data-table th, .data-table td {
  text-align: left;
  padding: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.data-table th {
  font-weight: bold;
  background-color: #f8f9fa;
}

.data-table tr:hover {
  background-color: #f1f1f1;
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
</style>
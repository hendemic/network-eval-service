<template>
  <div class="history">
    <h2>Network Test History</h2>
    
    <div class="controls">
      <div class="page-size-controls">
        <span class="control-label">Entries per page:</span>
        <button
          v-for="size in pageSizeOptions"
          :key="size"
          @click="setPageSize(size)"
          :class="{ active: pageSize === size }"
          class="page-size-btn"
        >
          {{ size }}
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
            <tr v-for="result in paginatedResults" :key="result.id">
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
        
        <!-- Pagination controls -->
        <div class="pagination-controls">
          <div class="page-info">
            Showing {{ startIndex + 1 }}-{{ Math.min(endIndex, pingResults.length) }} of {{ pingResults.length }} entries
          </div>
          <div class="page-buttons">
            <button 
              @click="prevPage" 
              :disabled="currentPage === 1"
              class="pagination-btn"
            >
              Previous
            </button>
            <span class="page-indicator">{{ currentPage }} / {{ totalPages }}</span>
            <button 
              @click="nextPage" 
              :disabled="currentPage === totalPages"
              class="pagination-btn"
            >
              Next
            </button>
          </div>
        </div>
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

export default {
  name: 'History',
  components: {
  },
  setup() {
    const store = useStore()
    const currentPage = ref(1)
    const pageSize = ref(10)
    const pageSizeOptions = [10, 50, 100]
    
    // Fetch data on component mount
    onMounted(() => {
      fetchData()
    })
    
    const fetchData = async () => {
      // Fetch the last 72 hours of data by default (3 days)
      await store.dispatch('fetchPingResults', { 
        hours: 72,
        limit: 10000
      })
      
      // Reset to first page when new data is fetched
      currentPage.value = 1
    }
    
    const setPageSize = (size) => {
      pageSize.value = size
      currentPage.value = 1 // Reset to first page when changing page size
    }
    
    const refreshData = () => {
      fetchData()
    }
    
    // Pagination methods
    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
      }
    }
    
    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }
    
    // Format date for display
    const formatDate = (dateString) => {
      return new Date(dateString + 'Z').toLocaleString();
    }
    
    // Computed for pagination
    const pingResults = computed(() => {
      // Get results sorted by timestamp (newest first)
      return [...store.state.pingResults].sort((a, b) => {
        return new Date(b.timestamp) - new Date(a.timestamp)
      })
    })
    
    const totalPages = computed(() => {
      return Math.ceil(pingResults.value.length / pageSize.value)
    })
    
    const startIndex = computed(() => {
      return (currentPage.value - 1) * pageSize.value
    })
    
    const endIndex = computed(() => {
      return startIndex.value + pageSize.value
    })
    
    const paginatedResults = computed(() => {
      return pingResults.value.slice(startIndex.value, endIndex.value)
    })
    
    return {
      loading: computed(() => store.state.loading),
      error: computed(() => store.state.error),
      pingResults,
      paginatedResults,
      pageSizeOptions,
      pageSize,
      currentPage,
      totalPages,
      startIndex,
      endIndex,
      setPageSize,
      refreshData,
      nextPage,
      prevPage,
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

.page-size-btn {
  padding: 0.5rem 1rem;
  background-color: #f1f1f1;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.page-size-btn.active {
  background-color: var(--primary-color);
  color: white;
}

.page-size-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-label {
  font-size: 0.9rem;
  color: #666;
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

.pagination-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.page-info {
  font-size: 0.9rem;
  color: #666;
}

.page-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-btn {
  padding: 0.4rem 0.8rem;
  background-color: #f1f1f1;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn:not(:disabled):hover {
  background-color: #e1e1e1;
}

.page-indicator {
  padding: 0 0.5rem;
  font-size: 0.9rem;
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
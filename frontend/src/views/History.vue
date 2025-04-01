<template>
  <div class="history">
    <div class="header">
      <h2>Network Test History</h2>
      <nav-menu @refresh="refreshData" />
    </div>
    
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
    
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import NavMenu from '../components/NavMenu.vue'

export default {
  name: 'History',
  components: {
    NavMenu,
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
/* Component-specific styles only - shared styles are now in CSS modules */

/* Fix border-top variable */
.pagination-controls {
  border-top: 1px solid var(--border-light);
}
</style>
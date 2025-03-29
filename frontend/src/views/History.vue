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
.history {
  width: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.nav-container {
  position: relative;
  display: flex;
  align-items: center;
}

.menu-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  padding: 0.5rem;
  margin-right: 0.5rem;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-item {
  text-decoration: none;
  color: #666;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  /* No transition */
}

.nav-item:hover {
  background-color: #f1f1f1;
}

.nav-item.active {
  color: var(--primary-color);
  font-weight: 600;
}

.refresh-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  padding: 0.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  /* No transition */
}

.refresh-text {
  display: none;
}

.refresh-btn:hover {
  background-color: #f1f1f1;
  color: var(--primary-color);
}

/* Mobile responsive styling */
@media (max-width: 768px) {
  .header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
  
  .nav-container {
    position: relative;
  }
  
  .menu-toggle {
    display: block;
  }
  
  /* X icon for close state */
  .menu-toggle svg line:nth-child(1) {
    transform-origin: center;
    transition: transform 0.2s ease;
  }
  
  .menu-toggle svg line:nth-child(2) {
    transition: opacity 0.2s ease;
  }
  
  .menu-toggle svg line:nth-child(3) {
    transform-origin: center;
    transition: transform 0.2s ease;
  }
  
  /* Hamburger to X animation */
  .menu-toggle.active svg line:nth-child(1) {
    transform: rotate(45deg) translate(5px, 5px);
  }
  
  .menu-toggle.active svg line:nth-child(2) {
    opacity: 0;
  }
  
  .menu-toggle.active svg line:nth-child(3) {
    transform: rotate(-45deg) translate(5px, -5px);
  }
  
  .nav-menu {
    display: none;
    flex-direction: column;
    position: absolute;
    top: 100%;
    right: 0;
    width: 66%;
    background: white;
    padding: 1rem;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    border-radius: 4px;
    z-index: 10;
    margin-top: 0.5rem;
  }
  
  .nav-menu-expanded {
    display: flex;
  }
  
  .refresh-text {
    display: inline;
  }
  
  .refresh-btn {
    width: 100%;
    justify-content: flex-start;
  }
}

.controls {
  margin-bottom: 2rem;
}

.page-size-btn {
  padding: 0.5rem 1rem;
  background-color: var(--bg-light);
  border: none;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--filter-inactive-color);
}

.page-size-btn.active {
  background-color: var(--brand-primary);
  color: var(--text-white);
}

.page-size-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.chart-card {
  margin-bottom: 2rem;
}

.loading, .error {
  text-align: center;
  padding: var(--space-xl);
  background: var(--bg-white);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
}

.error {
  color: var(--brand-danger);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.data-table th, .data-table td {
  text-align: left;
  padding: 0.75rem;
  border-bottom: 1px solid var(--border-light);
}

.data-table th {
  font-weight: var(--font-weight-bold);
  background-color: var(--bg-light);
  color: var(--text-primary);
}

/* Override for dark mode */
.dark-theme .data-table th {
  background-color: var(--table-header-bg);
}

.data-table tr:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

/* Override for dark mode */
.dark-theme .data-table tr:hover {
  background-color: var(--table-hover-bg);
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
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.page-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-btn {
  padding: 0.4rem 0.8rem;
  background-color: var(--bg-light);
  border: none;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  color: var(--filter-inactive-color);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn:not(:disabled):hover {
  background-color: var(--table-header-bg);
}

.page-indicator {
  padding: 0 0.5rem;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

</style>
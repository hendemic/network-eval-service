import { createStore } from 'vuex'
import axios from 'axios'

// API base URL
const API_URL = process.env.VUE_APP_API_URL || '/api'

// Theme functions
const getThemeFromLocalStorage = () => {
  // Check if user has a saved preference
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark' || savedTheme === 'light') {
    return savedTheme
  }
  
  // If no preference, check system preference
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark'
  }
  
  // Default to light theme
  return 'light'
}

const setThemeInLocalStorage = (theme) => {
  localStorage.setItem('theme', theme)
}

const applyTheme = (theme) => {
  // Add or remove dark-theme class from html element
  if (theme === 'dark') {
    document.documentElement.classList.add('dark-theme')
  } else {
    document.documentElement.classList.remove('dark-theme')
  }
}

export default createStore({
  state: {
    pingResults: [],
    stats: null,
    loading: false,
    error: null,
    theme: getThemeFromLocalStorage()
  },
  getters: {
    latencyData(state) {
      return state.pingResults.map(result => ({
        timestamp: new Date(result.timestamp + 'Z'), // Add Z to indicate UTC
        value: result.avg_latency
      })).sort((a, b) => a.timestamp - b.timestamp)
    },
    jitterData(state) {
      return state.pingResults.map(result => ({
        timestamp: new Date(result.timestamp + 'Z'), // Add Z to indicate UTC
        value: result.jitter
      })).sort((a, b) => a.timestamp - b.timestamp)
    },
    packetLossData(state) {
      return state.pingResults.map(result => ({
        timestamp: new Date(result.timestamp + 'Z'), // Add Z to indicate UTC
        value: result.packet_loss
      })).sort((a, b) => a.timestamp - b.timestamp)
    },
    currentTheme(state) {
      return state.theme
    },
    isDarkMode(state) {
      return state.theme === 'dark'
    }
  },
  mutations: {
    SET_PING_RESULTS(state, results) {
      state.pingResults = results
    },
    SET_STATS(state, stats) {
      state.stats = stats
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    SET_THEME(state, theme) {
      state.theme = theme
    }
  },
  actions: {
    async fetchPingResults({ commit }, { hours = 24, limit = 1000 } = {}) {
      commit('SET_LOADING', true)
      try {
        const params = { hours, limit }
        const response = await axios.get(`${API_URL}/ping-results`, { params })
        commit('SET_PING_RESULTS', response.data)
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to fetch ping results')
        console.error('Error fetching ping results:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    async fetchStats({ commit }) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${API_URL}/ping-stats`)
        commit('SET_STATS', response.data)
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to fetch network stats')
        console.error('Error fetching network stats:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    setTheme({ commit }, theme) {
      // Update store
      commit('SET_THEME', theme)
      
      // Save to localStorage
      setThemeInLocalStorage(theme)
      
      // Apply the theme to the DOM
      applyTheme(theme)
    },
    
    initTheme({ state, dispatch }) {
      // Apply the current theme from state
      dispatch('setTheme', state.theme)
      
      // Add listener for system preference changes
      if (window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
        
        // Define handler function
        const handleThemeChange = (e) => {
          // Only apply if user hasn't set a preference manually
          if (!localStorage.getItem('theme')) {
            const newTheme = e.matches ? 'dark' : 'light'
            dispatch('setTheme', newTheme)
          }
        }
        
        // Add listener (with compatibility for older browsers)
        if (mediaQuery.addEventListener) {
          mediaQuery.addEventListener('change', handleThemeChange)
        } else if (mediaQuery.addListener) {
          // Older implementation
          mediaQuery.addListener(handleThemeChange)
        }
      }
    }
  }
})
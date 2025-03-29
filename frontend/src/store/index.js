import { createStore } from 'vuex'
import axios from 'axios'

// API base URL
const API_URL = process.env.VUE_APP_API_URL || '/api'

export default createStore({
  state: {
    pingResults: [],
    stats: null,
    loading: false,
    error: null
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
    }
  },
  actions: {
    async fetchPingResults({ commit }, { hours = 24, limit = 1000 } = {}) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${API_URL}/ping-results`, {
          params: { hours, limit }
        })
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
    }
  }
})
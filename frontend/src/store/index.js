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
    async fetchPingResults({ commit }, { 
      hours = 24, 
      startTime = null, 
      limit = 1000, 
      preserveOutliers = false,
      sampleMethod = 'all'
    } = {}) {
      commit('SET_LOADING', true)
      try {
        const params = { hours, limit }
        
        // Add startTime param if provided (allows fetching by specific date range)
        if (startTime !== null) {
          params.start_time = startTime
        }
        
        const response = await axios.get(`${API_URL}/ping-results`, { params })
        
        // If we need intelligent sampling with outlier preservation
        if (preserveOutliers && sampleMethod === 'outliers_first' && response.data.length > limit) {
          // Use helper functions defined below for intelligent sampling
          const processedData = intelligentSample(response.data, limit, hours)
          commit('SET_PING_RESULTS', processedData)
        } else {
          commit('SET_PING_RESULTS', response.data)
        }
        
        // Inner function to intelligently sample data with outlier preservation
        function intelligentSample(rawData, targetPoints, timeRangeHours) {
          if (rawData.length <= targetPoints) {
            return rawData // No sampling needed
          }
          
          // Sort data by timestamp for processing
          const sortedData = [...rawData].sort((a, b) => 
            new Date(a.timestamp) - new Date(b.timestamp)
          )
          
          // Step 1: Identify outliers in key metrics (we're particularly interested in packet loss)
          // Calculate mean and standard deviation for packet loss, latency, and jitter
          const metrics = {
            packet_loss: calculateStats(sortedData.map(d => d.packet_loss)),
            avg_latency: calculateStats(sortedData.map(d => d.avg_latency)),
            jitter: calculateStats(sortedData.map(d => d.jitter))
          }
          
          // Step 2: Create a score for each data point based on how "interesting" it is
          const scoredData = sortedData.map(point => {
            const packetLossZScore = Math.abs((point.packet_loss - metrics.packet_loss.mean) / metrics.packet_loss.stdDev)
            const latencyZScore = Math.abs((point.avg_latency - metrics.avg_latency.mean) / metrics.avg_latency.stdDev)
            const jitterZScore = Math.abs((point.jitter - metrics.jitter.mean) / metrics.jitter.stdDev)
            
            // Weight packet loss higher since spikes there are particularly important
            const interestScore = (packetLossZScore * 3) + latencyZScore + jitterZScore
            
            return {
              ...point,
              interestScore
            }
          })
          
          // Step 3: Reserve 30% of points for the most interesting data
          const outlierCount = Math.ceil(targetPoints * 0.3)
          const mostInteresting = [...scoredData]
            .sort((a, b) => b.interestScore - a.interestScore)
            .slice(0, outlierCount)
          
          // Step 4: Fill the remaining 70% with evenly spaced points to maintain the shape
          const remainingCount = targetPoints - outlierCount
          const regularSampleInterval = Math.floor(sortedData.length / remainingCount)
          
          const sampledRegularPoints = []
          for (let i = 0; i < sortedData.length; i += regularSampleInterval) {
            sampledRegularPoints.push(sortedData[i])
            if (sampledRegularPoints.length >= remainingCount) break
          }
          
          // Step 5: Combine outliers with regular samples and deduplicate
          const combinedPoints = [...mostInteresting, ...sampledRegularPoints]
          const seenTimestamps = new Set()
          const uniquePoints = combinedPoints.filter(point => {
            if (seenTimestamps.has(point.timestamp)) {
              return false
            }
            seenTimestamps.add(point.timestamp)
            return true
          })
          
          // Step 6: Sort by timestamp to maintain chronological order
          return uniquePoints.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
        }
        
        // Helper function to calculate mean and standard deviation
        function calculateStats(values) {
          const mean = values.reduce((sum, val) => sum + val, 0) / values.length
          
          const squaredDiffs = values.map(val => Math.pow(val - mean, 2))
          const variance = squaredDiffs.reduce((sum, val) => sum + val, 0) / values.length
          const stdDev = Math.sqrt(variance) || 0.0001 // Avoid division by zero
          
          return {
            mean,
            stdDev,
            min: Math.min(...values),
            max: Math.max(...values)
          }
        }
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
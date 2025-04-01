/**
 * Chart Data Composable
 * 
 * This composable provides utilities for processing and formatting network metrics
 * data for visualization in charts. It handles timestamp formatting, data sorting,
 * and appropriate data structure creation for different chart types.
 */
import { computed } from 'vue';
import { formatDateToLocaleString } from '../utils/dateUtils';

/**
 * Process network metrics data for chart visualization
 * 
 * @param {Object} options - Configuration options
 * @param {Function} options.getData - Function to retrieve raw data
 * @param {Number} options.selectedHours - Current time range selection in hours
 * @returns {Object} Object containing formatted chart data and supporting functions
 */
export function useChartData(options) {
  const { getData, selectedHours } = options;
  
  /**
   * Format chart data timestamps based on the selected time range
   * 
   * @param {Date} date - The date to format
   * @returns {String} Formatted date string appropriate for the current time range
   */
  const formatTimestamp = (date) => {
    if (selectedHours.value <= 12) {
      // For shorter time periods (≤12h), show hours:minutes with nicely formatted times
      return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
    } else if (selectedHours.value <= 72) {
      // For 1-3 day views, show day and hour
      return `${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:00`;
    } else {
      // For 7-day view, show month/day and hour
      return `${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:00`;
    }
  };

  /**
   * Format a date string (from API) for display
   * Ensures consistent handling of UTC timestamps
   * 
   * @param {String} dateString - ISO date string from API
   * @returns {String} Formatted local date/time string
   */
  const formatDateForDisplay = (dateString) => {
    return formatDateToLocaleString(dateString);
  };

  // Time range availability check removed as it's now handled by useTimeRange composable

  /**
   * Computed property that returns formatted chart values
   */
  const chartValues = computed(() => {
    const data = getData();
    if (!data || data.length === 0) return [];
    
    // Return the values directly from the data objects
    return data.map(item => item.value);
  });

  /**
   * Computed property that returns formatted chart labels
   */
  const chartLabels = computed(() => {
    const data = getData();
    if (!data || data.length === 0) return [];
    
    // Format labels based on current time range
    return data.map(item => formatTimestamp(item.timestamp));
  });

  // Return all the chart-related functions and data
  return {
    chartValues,
    chartLabels,
    formatDateForDisplay
  };
}
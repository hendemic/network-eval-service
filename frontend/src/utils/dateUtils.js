/**
 * Date and Timestamp Utility Functions
 * 
 * This module provides utility functions for consistent date and timestamp
 * handling throughout the application, ensuring UTC timestamps are properly
 * processed and formatted.
 */

/**
 * Parse an ISO timestamp string, ensuring it's treated as UTC
 * 
 * @param {string} isoString - ISO 8601 date string, with or without Z suffix
 * @returns {Date} JavaScript Date object representing the timestamp in UTC
 */
export const parseUtcTimestamp = (isoString) => {
  // Add 'Z' to indicate UTC if not already present
  // This ensures consistent timezone handling
  return new Date(isoString.endsWith('Z') ? isoString : isoString + 'Z');
};

/**
 * Format a date object to a localized date and time string
 * 
 * @param {string} isoString - ISO 8601 date string
 * @returns {string} Localized date and time string
 */
export const formatDateToLocaleString = (isoString) => {
  const date = parseUtcTimestamp(isoString);
  return date.toLocaleString();
};

/**
 * Transform raw API results into a standard metric data format
 * 
 * @param {Array} results - Array of results from the API
 * @param {string} metricKey - The key of the metric to extract (e.g., 'avg_latency')
 * @returns {Array} Array of objects with timestamp and value properties, sorted by time
 */
export const formatMetricData = (results, metricKey) => {
  if (!results || !results.length) {
    console.log('formatMetricData: No results provided');
    return [];
  }
  
  console.log(`formatMetricData: Processing ${results.length} results for ${metricKey}`);
  
  const formattedData = results
    .map(result => ({
      timestamp: parseUtcTimestamp(result.timestamp),
      value: result[metricKey]
    }))
    .sort((a, b) => a.timestamp - b.timestamp);
    
  if (formattedData.length > 0) {
    console.log(`formatMetricData: Formatted data span:`, {
      metric: metricKey,
      points: formattedData.length,
      oldest: formattedData[0].timestamp.toLocaleString(),
      newest: formattedData[formattedData.length - 1].timestamp.toLocaleString(),
      spanHours: ((formattedData[formattedData.length - 1].timestamp - formattedData[0].timestamp) / (1000 * 60 * 60)).toFixed(2)
    });
  }
  
  return formattedData;
};
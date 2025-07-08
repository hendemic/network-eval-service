/**
 * Time Range Management Composable
 * 
 * Provides utilities for managing time range selection in charts and data displays.
 * This composable handles time range options, availability checks based on data,
 * and selection state.
 */
import { ref, computed } from 'vue';

/**
 * Create a time range management system
 * 
 * @param {Object} options - Configuration options
 * @param {Function} options.getDataSpan - Function that returns the current data span in hours
 * @param {Number} [options.defaultRange=3] - Default time range in hours
 * @returns {Object} Object containing time range management functions and state
 */
export function useTimeRange(options) {
  const { getDataSpan, defaultRange = 3 } = options;
  
  // Define available time range options
  const timeOptions = [
    { label: "3 Hours", hours: 3, minDataSpan: 0 }, // Always available
    { label: "12 Hours", hours: 12, minDataSpan: 0 }, // Always available
    { label: "24 Hours", hours: 24, minDataSpan: 11 }, // Need at least 11h of data
    { label: "3 Days", hours: 72, minDataSpan: 23 }, // Need at least 23h of data
    { label: "7 Days", hours: 168, minDataSpan: 71 }, // Need at least 71h of data
  ];
  
  // Currently selected time range in hours
  const selectedHours = ref(defaultRange);
  
  /**
   * Check if a time range option is available based on current data span
   * 
   * @param {Number} hours - The time range option to check (in hours)
   * @returns {Boolean} Whether this time range option should be enabled
   */
  const isTimeRangeAvailable = (hours) => {
    // Get current data time span
    const dataSpanHours = getDataSpan();
    
    if (!dataSpanHours) {
      console.log(`Time range ${hours}h not available: no data span`);
      return false;
    }
    
    // Find the option that matches these hours
    const option = timeOptions.find(opt => opt.hours === hours);
    if (!option) {
      console.log(`Time range ${hours}h not available: option not found`);
      return false;
    }
    
    // Check if we have enough data for this option
    const available = dataSpanHours >= option.minDataSpan;
    console.log(`Time range ${hours}h availability:`, {
      dataSpanHours: dataSpanHours.toFixed(2),
      minRequired: option.minDataSpan,
      available
    });
    
    return available;
  };
  
  /**
   * Get the tooltip message for a time range button
   * 
   * @param {Number} hours - The time range in hours
   * @returns {String} Tooltip message to display
   */
  const getTimeRangeTooltip = (hours) => {
    return isTimeRangeAvailable(hours) 
      ? null
      : 'Not enough data available for this time range';
  };
  
  /**
   * Set the current time range
   * 
   * @param {Number} hours - The time range to set in hours
   */
  const setTimeRange = (hours) => {
    // Only update if the option is available
    if (isTimeRangeAvailable(hours)) {
      selectedHours.value = hours;
    }
  };
  
  /**
   * Get time range options with availability status
   */
  const availableTimeOptions = computed(() => {
    console.log('Computing available time options...');
    const options = timeOptions.map(option => ({
      ...option,
      available: isTimeRangeAvailable(option.hours),
      active: selectedHours.value === option.hours
    }));
    
    console.log('Available time options:', options.map(opt => ({
      label: opt.label,
      hours: opt.hours,
      available: opt.available,
      active: opt.active
    })));
    
    return options;
  });
  
  return {
    timeOptions,
    selectedHours,
    availableTimeOptions,
    isTimeRangeAvailable,
    getTimeRangeTooltip,
    setTimeRange
  };
}
/**
 * Tooltip Service - provides global access to tooltip functionality
 */

import { reactive } from 'vue';

// Create a global singleton for tooltip management
const tooltipState = reactive({
  // Registry of tooltip instances
  instances: new Set(),
  
  // Register a tooltip component
  register(tooltipInstance) {
    if (tooltipInstance && !this.instances.has(tooltipInstance)) {
      this.instances.add(tooltipInstance);
    }
  },
  
  // Unregister a tooltip component
  unregister(tooltipInstance) {
    if (tooltipInstance && this.instances.has(tooltipInstance)) {
      this.instances.delete(tooltipInstance);
    }
  },
  
  // Hide all tooltips
  hideAll() {
    this.instances.forEach(instance => {
      if (instance && typeof instance.hideTooltip === 'function') {
        instance.hideTooltip();
      }
    });
  },
  
  // Show a tooltip at a specific position with content
  showTooltipAt(x, y, content, isChart = false) {
    // First hide all tooltips
    this.hideAll();
    
    // Get the first available tooltip instance
    const tooltipInstance = this.instances.values().next().value;
    
    // Show the tooltip if an instance is available
    if (tooltipInstance && typeof tooltipInstance.showAt === 'function') {
      try {
        tooltipInstance.showAt(x, y, content, isChart);
        return true;
      } catch (e) {
        console.error('Error showing tooltip:', e);
      }
    }
    
    // If we got here, either no instance was available or there was an error
    return false;
  }
});

export default tooltipState;
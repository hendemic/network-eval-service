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
        // Get viewport dimensions
        const viewportHeight = window.innerHeight;
        const viewportWidth = window.innerWidth;
        
        // Estimate tooltip dimensions - we'll use averages here
        // In a more sophisticated version, we could measure the actual tooltip after rendering
        const estimatedTooltipHeight = 80; // pixels, approximate
        const estimatedTooltipWidth = 200; // pixels, approximate
        
        // Calculate optimal position
        let posX = x;
        let posY = y;
        
        // For chart tooltips, apply smart positioning
        if (isChart) {
          // Horizontal position - ensure tooltip doesn't go off screen
          if (x + (estimatedTooltipWidth / 2) > viewportWidth) {
            // Too close to right edge
            posX = viewportWidth - (estimatedTooltipWidth / 2) - 10;
          } else if (x - (estimatedTooltipWidth / 2) < 0) {
            // Too close to left edge
            posX = (estimatedTooltipWidth / 2) + 10;
          }
          
          // Vertical position - prefer above the cursor for chart data
          // to avoid obscuring the data point
          const spaceAbove = y;
          const spaceBelow = viewportHeight - y;
          
          // Default offset to position tooltip away from cursor
          const verticalOffset = 25; // pixels
          
          if (spaceAbove >= estimatedTooltipHeight + verticalOffset) {
            // Enough space above, position tooltip above cursor
            posY = y - estimatedTooltipHeight - verticalOffset;
          } else if (spaceBelow >= estimatedTooltipHeight + verticalOffset) {
            // Enough space below, position tooltip below cursor
            posY = y + verticalOffset;
          } else {
            // Limited space both above and below, use the side with more space
            posY = spaceAbove > spaceBelow ? 
              y - estimatedTooltipHeight - 5 : // Above with minimal offset
              y + 5; // Below with minimal offset
          }
        }
        
        // Show the tooltip at the calculated position
        tooltipInstance.showAt(posX, posY, content, isChart);
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
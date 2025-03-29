import { ref, onUnmounted } from 'vue';
import tooltipService from '../services/tooltipService';

export function useTooltip() {
  // Register this usage with the tooltip service
  const register = (tooltipRef) => {
    if (tooltipRef) {
      tooltipService.register(tooltipRef);
    }
  };
  
  // Cleanup on component unmount
  const unregister = (tooltipRef) => {
    if (tooltipRef) {
      tooltipService.unregister(tooltipRef);
    }
  };
  
  // Track elements with tooltips attached in this component
  const attachedElements = new Set();
  
  // Reference tracking to avoid memory leaks
  onUnmounted(() => {
    // Clean up all attached elements
    attachedElements.forEach(element => {
      if (element._tooltipCleanup) {
        element._tooltipCleanup();
        delete element._tooltipCleanup;
      }
    });
  });
  
  // Utility to attach tooltip to an element
  const attachTooltip = (element, text, options = {}) => {
    if (!element) return;
    
    // Clean up any existing tooltip on this element
    if (element._tooltipCleanup) {
      element._tooltipCleanup();
    }
    
    // Track this element
    attachedElements.add(element);
    
    // Get tooltip content and event handlers
    const isDisabledOnly = options.isDisabledOnly || false;
    
    // Function to show tooltip
    const showTooltip = (event) => {
      // Skip if this element shouldn't show a tooltip (e.g., if it's not disabled)
      if (isDisabledOnly && !element.disabled) return;
      if (event) event.stopPropagation();
      
      // Get element position
      const rect = element.getBoundingClientRect();
      const x = rect.left + rect.width / 2 + (options.offsetX || 0);
      const y = rect.bottom + (options.offsetY || 10);
      
      // Show tooltip at position
      tooltipService.showTooltipAt(x, y, text, options.isChart || false);
    };
    
    // Function to hide tooltip
    const hideTooltip = (event) => {
      if (event) event.stopPropagation();
      tooltipService.hideAll();
    };
    
    // Add event listeners
    element.addEventListener('mouseenter', showTooltip);
    element.addEventListener('mouseleave', hideTooltip);
    element.addEventListener('focusin', showTooltip);
    element.addEventListener('focusout', hideTooltip);
    
    // Mark element as having a tooltip
    element._isTooltipTrigger = true;
    
    // Create cleanup function
    const cleanup = () => {
      element.removeEventListener('mouseenter', showTooltip);
      element.removeEventListener('mouseleave', hideTooltip);
      element.removeEventListener('focusin', showTooltip);
      element.removeEventListener('focusout', hideTooltip);
      element._isTooltipTrigger = false;
    };
    
    // Store cleanup function on the element for later use
    element._tooltipCleanup = cleanup;
    
    return cleanup;
  };
  
  // Utility for button tooltips that only show when disabled
  const attachDisabledTooltip = (element, text) => {
    return attachTooltip(element, text, { isDisabledOnly: true });
  };
  
  // Manually show tooltip at specific coordinates
  const showTooltipAt = (x, y, text, isChart = true) => {
    tooltipService.showTooltipAt(x, y, text, isChart);
  };
  
  // Manually hide the tooltip
  const hideTooltip = () => {
    tooltipService.hideAll();
  };
  
  return {
    register,
    attachTooltip,
    attachDisabledTooltip,
    showTooltipAt,
    hideTooltip
  };
}
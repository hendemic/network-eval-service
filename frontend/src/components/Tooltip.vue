<template>
  <Teleport to="body">
    <div 
      v-if="show"
      class="tooltip" 
      :class="{'tooltip-chart': isChartTooltip}"
      :style="{
        left: `${x}px`,
        top: `${y}px`,
        opacity: show ? 0.9 : 0,
        visibility: show ? 'visible' : 'hidden',
        position: 'fixed',
        zIndex: isChartTooltip ? 10000 : 9000
      }"
    >
      <slot><div v-html="tooltipContent"></div></slot>
    </div>
  </Teleport>
</template>

<script>
import { ref, onUnmounted, onMounted, watch } from 'vue';

export default {
  name: 'Tooltip',
  props: {
    text: {
      type: String,
      default: ''
    },
    isChart: {
      type: Boolean,
      default: false
    }
  },
  // We'll handle this in setup instead
  emits: ['update:show'],
  setup(props, { emit }) {
    // Tooltip state
    const show = ref(false);
    const x = ref(0);
    const y = ref(0);
    
    // Map to store event handlers for each trigger element
    const eventHandlersMap = new Map();
    
    // Hide tooltip globally when needed
    const hideTooltip = () => {
      show.value = false;
      emit('update:show', false);
    };
    
    // Set up global click handler to hide tooltip
    const handleGlobalClick = (e) => {
      // Don't hide if clicking on a tooltip trigger that should keep its tooltip
      if (e.target && e.target._isTooltipTrigger) {
        return;
      }
      hideTooltip();
    };
    
    // Register global event listeners
    onMounted(() => {
      document.addEventListener('click', handleGlobalClick);
    });
    
    // Clean up global event listeners
    onUnmounted(() => {
      document.removeEventListener('click', handleGlobalClick);
      
      // Clean up any remaining event handlers
      eventHandlersMap.forEach((handlers, element) => {
        Object.keys(handlers).forEach(event => {
          element.removeEventListener(event, handlers[event]);
        });
      });
      eventHandlersMap.clear();
    });
    
    // Create a method to attach tooltip to an element
    const attachToElement = (element, content, options = {}) => {
      if (!element) return;
      
      // Default options
      const {
        isDisabledOnly = false,
        offsetX = 0,
        offsetY = 10,
        isChart = false
      } = options;
      
      // Only apply to disabled elements if isDisabledOnly is true
      if (isDisabledOnly && !element.disabled) return;
      
      // Store current element for cleanup
      const elementHandlers = {};
      
      // Show tooltip handler
      const handleShow = (event) => {
        // Skip if this element shouldn't show a tooltip
        if (isDisabledOnly && !element.disabled) return;
        if (event.stopPropagation) event.stopPropagation();
        
        // Update position based on element
        const rect = element.getBoundingClientRect();
        x.value = rect.left + rect.width / 2 + offsetX;
        y.value = rect.bottom + offsetY;
        
        // Update content
        tooltipContent.value = content;
        isChartTooltip.value = isChart;
        
        // Show the tooltip
        show.value = true;
        emit('update:show', true);
      };
      
      // Hide tooltip handler
      const handleHide = (event) => {
        if (event.stopPropagation) event.stopPropagation();
        
        hideTooltip();
      };
      
      // Add event listeners
      element.addEventListener('mouseenter', handleShow);
      element.addEventListener('mouseleave', handleHide);
      element.addEventListener('focusin', handleShow);
      element.addEventListener('focusout', handleHide);
      
      // Mark element as tooltip trigger
      element._isTooltipTrigger = true;
      
      // Store handlers for cleanup
      elementHandlers.mouseenter = handleShow;
      elementHandlers.mouseleave = handleHide;
      elementHandlers.focusin = handleShow;
      elementHandlers.focusout = handleHide;
      
      // Store in map for later cleanup
      eventHandlersMap.set(element, elementHandlers);
      
      // Return cleanup function
      return () => {
        Object.keys(elementHandlers).forEach(event => {
          element.removeEventListener(event, elementHandlers[event]);
        });
        eventHandlersMap.delete(element);
        element._isTooltipTrigger = false;
      };
    };
    
    // Reactive state for content
    const tooltipContent = ref(props.text);
    const isChartTooltip = ref(props.isChart);
    
    // Method to manually set position and show tooltip (for chart data points)
    const showAt = (clientX, clientY, content, isChart = true) => {
      x.value = clientX;
      y.value = clientY;
      tooltipContent.value = content;
      isChartTooltip.value = isChart;
      show.value = true;
      emit('update:show', true);
    };
    
    // Watch for changes in the show state
    watch(show, (newValue) => {
      emit('update:show', newValue);
    });
    
    return {
      show,
      x, 
      y,
      attachToElement,
      showAt,
      hideTooltip,
      tooltipContent,
      isChartTooltip
    };
  }
}
</script>

<style>
/* Non-scoped styles for global access */
.tooltip {
  background: rgba(0, 0, 0, 0.75);
  color: var(--text-white);
  padding: var(--space-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  pointer-events: none;
  max-width: 220px;
  box-shadow: var(--shadow-sm);
  transform: translateX(-50%);
  text-align: center;
  width: max-content;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Chart tooltips get a higher z-index */
.tooltip-chart {
  z-index: 10000;
}

/* Invert colors for dark theme */
.dark-theme .tooltip {
  background: rgba(255, 255, 255, 0.85);
  color: #222;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* Tooltip content styling */
.tooltip-header {
  font-weight: var(--font-weight-bold);
  margin-bottom: 4px;
}

.tooltip-content {
  font-size: var(--font-size-xs);
}
</style>
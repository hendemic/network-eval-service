<template>
  <div 
    class="tooltip" 
    :style="{
      left: `${x}px`,
      top: `${y}px`,
      opacity: visible ? 0.9 : 0,
      visibility: visible ? 'visible' : 'hidden',
      position: 'fixed' // Ensure the tooltip is always positioned relative to the viewport
    }"
  >
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'Tooltip',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    x: {
      type: Number,
      default: 0
    },
    y: {
      type: Number,
      default: 0
    }
  }
}
</script>

<style scoped>
.tooltip {
  background: rgba(0, 0, 0, 0.7);
  color: var(--text-white);
  padding: var(--space-sm);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  pointer-events: none;
  z-index: 9999;
  transition: opacity var(--transition-quick);
  max-width: 200px;
  box-shadow: var(--shadow-sm);
}
</style>
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
  color: white;
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  z-index: 9999;
  transition: opacity 0.2s;
  max-width: 200px;
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16);
}
</style>
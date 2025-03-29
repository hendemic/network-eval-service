<template>
  <div class="stat-item">
    <div class="stat-value">
      {{ formattedValue }}
    </div>
    <div class="stat-label">{{ label }}</div>
  </div>
</template>

<script>
import { computed } from 'vue';

export default {
  name: 'NetworkMetric',
  props: {
    // The numeric value of the metric
    value: {
      type: Number,
      required: true
    },
    // The metric type (latency, jitter, packetLoss)
    metricType: {
      type: String,
      required: true,
      validator: value => ['latency', 'jitter', 'packetLoss'].includes(value)
    },
    // The display label
    label: {
      type: String,
      required: true
    },
    // Custom unit (defaults based on metric type)
    unit: {
      type: String,
      default: null
    },
    // Override default decimal places
    decimalPlaces: {
      type: Number,
      default: 2
    }
  },
  setup(props) {
    // Default units for different metrics
    const defaultUnits = {
      latency: 'ms',
      jitter: 'ms',
      packetLoss: '%'
    };

    // The unit to display
    const displayUnit = computed(() => {
      if (props.unit !== null) {
        return props.unit;
      }
      return defaultUnits[props.metricType];
    });

    // Format the value with the appropriate number of decimal places and unit
    const formattedValue = computed(() => {
      return `${props.value.toFixed(props.decimalPlaces)} ${displayUnit.value}`;
    });
    
    return {
      formattedValue
    };
  }
};
</script>

<style scoped>
.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--primary-color, #2c3e50); /* Using CSS variable with fallback */
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}
</style>
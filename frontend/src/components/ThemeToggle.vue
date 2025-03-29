<template>
  <button 
    @click="toggleTheme" 
    class="theme-toggle"
    :title="isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'"
    aria-label="Toggle dark mode"
  >
    <!-- Sun icon (for light mode) -->
    <svg v-if="isDarkMode" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="12" cy="12" r="5"/>
      <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
    </svg>
    
    <!-- Moon icon (for dark mode) -->
    <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
    
    <span class="toggle-text">{{ isDarkMode ? 'Light' : 'Dark' }}</span>
  </button>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'ThemeToggle',
  setup() {
    const store = useStore()
    
    const isDarkMode = computed(() => store.getters.isDarkMode)
    
    const toggleTheme = () => {
      const newTheme = isDarkMode.value ? 'light' : 'dark'
      store.dispatch('setTheme', newTheme)
    }
    
    return {
      isDarkMode,
      toggleTheme
    }
  }
}
</script>

<style scoped>
.theme-toggle {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  padding: var(--space-sm);
  border-radius: var(--border-radius-sm);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  /* No transition for immediate theme switching */
}

.theme-toggle:hover {
  background-color: var(--bg-light);
  color: var(--brand-primary);
  /* No transition */
}

.toggle-text {
  display: none;
}

@media (max-width: 768px) {
  .theme-toggle {
    width: 100%;
    justify-content: flex-end;
    margin: var(--space-sm) 0;
    padding: var(--space-sm) var(--space-md);
  }
  
  .toggle-text {
    display: inline;
  }
}
</style>
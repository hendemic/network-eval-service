<template>
  <div class="nav-container">
    <!-- Mobile menu button (hamburger) -->
    <button @click="toggleMenu" class="menu-toggle" :class="{ 'active': menuExpanded }" aria-label="Toggle menu">
      <div class="hamburger-icon">
        <span class="line"></span>
        <span class="line"></span>
        <span class="line"></span>
      </div>
    </button>
    
    <!-- Navigation menu (desktop or mobile expanded) -->
    <div class="nav-menu" :class="{ 'nav-menu-expanded': menuExpanded }">
      <router-link to="/" class="nav-item" :class="{ 'active': currentRoute === '/' }">Dashboard</router-link>
      <router-link to="/history" class="nav-item" :class="{ 'active': currentRoute === '/history' }">Full History</router-link>
      <button @click="handleRefresh" class="refresh-btn" title="Refresh Data">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.3"/>
        </svg>
        <span class="refresh-text">Refresh</span>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'NavMenu',
  emits: ['refresh'],
  setup(props, { emit }) {
    const menuExpanded = ref(false)
    const route = useRoute()
    
    // Get current route for active link highlighting
    const currentRoute = computed(() => route.path)
    
    // Toggle mobile menu
    const toggleMenu = () => {
      menuExpanded.value = !menuExpanded.value
    }
    
    // Handle refresh button click
    const handleRefresh = () => {
      emit('refresh')
    }
    
    return {
      menuExpanded,
      toggleMenu,
      currentRoute,
      handleRefresh
    }
  }
}
</script>

<style scoped>
.nav-container {
  position: relative;
  display: flex;
  align-items: center;
}

.menu-toggle {
  display: none; /* Will be overridden in media query */
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  padding: 0.5rem;
  margin-right: 0.5rem;
  width: 40px;
  height: 40px;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-item {
  text-decoration: none;
  color: #666;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s, color 0.2s;
}

.nav-item:hover {
  background-color: #f1f1f1;
}

.nav-item.active {
  color: var(--primary-color);
  font-weight: 600;
}

.refresh-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
  padding: 0.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background-color 0.2s;
}

.refresh-text {
  display: none;
}

.refresh-btn:hover {
  background-color: #f1f1f1;
  color: var(--primary-color);
}

/* Mobile responsive styling */
@media (max-width: 768px) {
  .menu-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  /* Hamburger icon */
  .hamburger-icon {
    width: 24px;
    height: 24px;
    position: relative;
  }
  
  .hamburger-icon .line {
    display: block;
    position: absolute;
    width: 100%;
    height: 3px;
    background-color: #666;
    border-radius: 3px;
    transition: all 0.3s ease;
  }
  
  /* Position the lines */
  .hamburger-icon .line:nth-child(1) {
    top: 4px;
  }
  
  .hamburger-icon .line:nth-child(2) {
    top: 11px;
  }
  
  .hamburger-icon .line:nth-child(3) {
    top: 18px;
  }
  
  /* X animation */
  .menu-toggle.active .hamburger-icon .line:nth-child(1) {
    top: 11px;
    transform: rotate(45deg);
  }
  
  .menu-toggle.active .hamburger-icon .line:nth-child(2) {
    opacity: 0;
  }
  
  .menu-toggle.active .hamburger-icon .line:nth-child(3) {
    top: 11px;
    transform: rotate(-45deg);
  }
  
  .nav-menu {
    position: absolute;
    flex-direction: column;
    top: 100%;
    right: 0;
    width: 66vw; /* Use viewport width instead of percentage of parent */
    max-width: 300px;
    background: white;
    padding: 1rem;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    border-radius: 4px;
    z-index: 10;
    margin-top: 0.5rem;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-10px);
    transition: all 0.3s ease;
  }
  
  .nav-menu-expanded {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
  }
  
  .nav-item, .refresh-btn {
    width: 100%;
    text-align: right;
    margin: 0.5rem 0;
    padding: 0.75rem 1rem;
  }
  
  .nav-item:hover {
    background-color: #f8f8f8;
  }
  
  .refresh-text {
    display: inline;
  }
  
  .refresh-btn {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
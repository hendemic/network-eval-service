import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// Import CSS
import './assets/css/base.css'

// Create the Vue app instance
const app = createApp(App)
  .use(store)
  .use(router)

// Initialize the theme before mounting the app
store.dispatch('initTheme')

// Mount the app
app.mount('#app')
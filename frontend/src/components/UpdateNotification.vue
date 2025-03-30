<template>
  <div v-if="updateAvailable" class="update-notification">
    <div class="update-content">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2v4M12 18v4M4.93 7.93l2.83 2.83M16.24 13.24l2.83 2.83M7.93 19.07l2.83-2.83M13.24 8.76l2.83-2.83M19.07 16.07l-2.83-2.83M8.76 10.76L5.93 7.93"/>
      </svg>
      <span>Update available! Use <code>./update.sh</code> to update.</span>
      <button @click="dismissUpdate" class="dismiss-btn" aria-label="Dismiss">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { ref, onMounted } from 'vue'

export default {
  name: 'UpdateNotification',
  setup() {
    const updateAvailable = ref(false)
    const currentVersion = ref('1.0.0') // Default to the version we set
    const repoOwner = 'hendemic'
    const repoName = 'network-eval-service'

    // Load current version from file
    const loadCurrentVersion = async () => {
      try {
        const response = await fetch('/VERSION')
        currentVersion.value = await response.text()
        currentVersion.value = currentVersion.value.trim()
      } catch (error) {
        console.error('Error loading version:', error)
      }
    }

    // Check if update is available
    const checkForUpdates = async () => {
      try {
        // First check if user has dismissed this update
        const dismissedVersion = localStorage.getItem('dismissedUpdateVersion')
        if (dismissedVersion === currentVersion.value) {
          return
        }

        // Then check GitHub repo for changes to VERSION file
        const apiUrl = `https://api.github.com/repos/${repoOwner}/${repoName}/contents/VERSION`
        const response = await axios.get(apiUrl)
        
        if (response.data && response.data.content) {
          // GitHub API returns base64 encoded content
          const remoteVersionBase64 = response.data.content
          const remoteVersion = atob(remoteVersionBase64.replace(/\n/g, '')).trim()
          
          // Compare versions
          if (remoteVersion !== currentVersion.value) {
            console.log(`Update available: ${currentVersion.value} → ${remoteVersion}`)
            updateAvailable.value = true
          }
        }
      } catch (error) {
        console.error('Error checking for updates:', error)
      }
    }

    // Dismiss update notification
    const dismissUpdate = () => {
      updateAvailable.value = false
      localStorage.setItem('dismissedUpdateVersion', currentVersion.value)
    }

    onMounted(async () => {
      await loadCurrentVersion()
      await checkForUpdates()
    })

    return {
      updateAvailable,
      dismissUpdate
    }
  }
}
</script>

<style scoped>
.update-notification {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: var(--brand-primary);
  color: white;
  z-index: 1000;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.update-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dismiss-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.25rem;
  margin-left: auto;
}

code {
  background-color: rgba(255, 255, 255, 0.2);
  padding: 0.15rem 0.3rem;
  border-radius: 3px;
}
</style>
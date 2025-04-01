<template>
  <div v-if="updateAvailable" class="update-notification">
    <div class="update-content">
      <span role="img" aria-label="rocket" style="font-size: 1.2rem; margin-right: 0.2rem;">🚀</span>
      <span>Update available! Use <code>nes-update</code> or update manually with docker.</span>
      <button @click="dismissUpdate" class="dismiss-btn" aria-label="Dismiss">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { ref, onMounted } from "vue";

export default {
  name: "UpdateNotification",
  setup() {
    const updateAvailable = ref(false);
    const currentVersion = ref("1.0.0"); // Default to the version we set
    const repoOwner = "hendemic";
    const repoName = "network-eval-service";

    // Load current version from file
    const loadCurrentVersion = async () => {
      try {
        const response = await fetch("/VERSION");
        currentVersion.value = await response.text();
        currentVersion.value = currentVersion.value.trim();
      } catch (error) {
        console.error("Error loading version:", error);
      }
    };

    // Check if update is available
    const checkForUpdates = async () => {
      try {
        // Check if user has dismissed the update in this session
        if (sessionStorage.getItem("dismissedUpdate") === "true") {
          return;
        }

        // Then check GitHub repo for changes to VERSION file specifically from production branch
        const apiUrl = `https://api.github.com/repos/${repoOwner}/${repoName}/contents/VERSION?ref=production`;
        const response = await axios.get(apiUrl);

        if (response.data && response.data.content) {
          // GitHub API returns base64 encoded content
          const remoteVersionBase64 = response.data.content;
          const remoteVersion = atob(
            remoteVersionBase64.replace(/\n/g, ""),
          ).trim();

          // Compare versions
          console.log(`Current version: ${currentVersion.value}, Remote version: ${remoteVersion}`);
          if (remoteVersion !== currentVersion.value) {
            console.log(
              `Update available: ${currentVersion.value} → ${remoteVersion}`,
            );
            updateAvailable.value = true;
          }
        }
      } catch (error) {
        console.error("Error checking for updates:", error);
      }
    };

    // Dismiss update notification
    const dismissUpdate = () => {
      updateAvailable.value = false;
      // Use sessionStorage instead of localStorage so it's cleared when browser is closed
      sessionStorage.setItem("dismissedUpdate", "true");
    };

    onMounted(async () => {
      await loadCurrentVersion();
      await checkForUpdates();
    });

    return {
      updateAvailable,
      dismissUpdate,
    };
  },
};
</script>

<style scoped>
.update-notification {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: var(--color-surface-card);
  color: var(--color-text-primary);
  z-index: 1000;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  border-bottom: var(--border-width-thin) solid var(--color-border-subtle);
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
  color: var(--color-text-primary);
  cursor: pointer;
  padding: 0.25rem;
  margin-left: auto;
}

code {
  background-color: var(--color-surface-contrast);
  color: var(--color-text-on-brand);
  padding: 0.15rem 0.3rem;
  border-radius: 3px;
}
</style>

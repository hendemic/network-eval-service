<template>
  <div id="app">
    <update-notification />
    <main>
      <router-view />
    </main>
    <footer>
      <p>
        Network Evaluation Service &copy; {{ new Date().getFullYear() }} | Made
        with ❤️ in Seattle.
      </p>
    </footer>
  </div>
</template>

<script>
import UpdateNotification from './components/UpdateNotification.vue';

export default {
  name: "App",
  components: {
    UpdateNotification
  },
  mounted() {
    // Set the document title
    document.title = "NES";
  },
};
</script>

<style>
/* App styling moved to assets/css/base.css */
</style>

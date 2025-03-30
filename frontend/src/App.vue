<template>
  <div id="app">
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
export default {
  name: "App",
  mounted() {
    // Set the document title
    document.title = "NES";
  },
};
</script>

<style>
/* App styling moved to assets/css/base.css */
</style>

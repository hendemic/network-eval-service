<template>
  <div id="app">
    <main>
      <router-view />
    </main>
    <footer>
      <p>Network Evaluation Service &copy; {{ new Date().getFullYear() }}</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  mounted() {
    // Set the document title
    document.title = 'NES';
  }
}
</script>

<style>
/* App-specific styles */
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

header {
  background-color: var(--brand-primary);
  color: var(--text-white);
  padding: var(--space-md);
  text-align: center;
}

main {
  flex: 1;
  padding: var(--space-xl);
  max-width: 1200px;
  margin: var(--space-xl) auto 0;
  width: 100%;
}

footer {
  background-color: var(--brand-primary);
  color: var(--text-white);
  text-align: center;
  padding: var(--space-md);
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--brand-secondary);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}
</style>
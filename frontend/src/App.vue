<template>
  <div id="app">
    <header>
      <h1>Network Performance Monitor</h1>
    </header>
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
  name: 'App'
}
</script>

<style>
:root {
  --primary-color: #2c3e50;
  --secondary-color: #42b983;
  --bg-color: #f8f9fa;
  --text-color: #333;
  --border-color: #ddd;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-color);
  background-color: var(--bg-color);
  line-height: 1.6;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

header {
  background-color: var(--primary-color);
  color: white;
  padding: 1rem;
  text-align: center;
}

main {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

footer {
  background-color: var(--primary-color);
  color: white;
  text-align: center;
  padding: 1rem;
}

h1, h2, h3 {
  margin-bottom: 1rem;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: var(--secondary-color);
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}
</style>
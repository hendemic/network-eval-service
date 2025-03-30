const fs = require('fs');
const path = require('path');

// Copy VERSION file from repo root to public directory during build time
const copyVersionFile = () => {
  try {
    const repoRoot = path.resolve(__dirname, '..');
    const versionSrc = path.join(repoRoot, 'VERSION');
    const versionDest = path.join(__dirname, 'public', 'VERSION');
    
    if (fs.existsSync(versionSrc)) {
      if (!fs.existsSync(path.dirname(versionDest))) {
        fs.mkdirSync(path.dirname(versionDest), { recursive: true });
      }
      fs.copyFileSync(versionSrc, versionDest);
      console.log('VERSION file copied to public directory');
    } else {
      console.log('VERSION file not found in repo root');
      // Create a default VERSION file if not exists
      if (!fs.existsSync(versionDest)) {
        fs.writeFileSync(versionDest, '1.0.0');
        console.log('Default VERSION file created');
      }
    }
  } catch (error) {
    console.error('Error copying VERSION file:', error);
  }
};

// Execute immediately
copyVersionFile();

module.exports = {
  lintOnSave: false,
  devServer: {
    overlay: {
      warnings: false,
      errors: false
    },
    onBeforeSetupMiddleware: () => {
      // Copy VERSION file again when dev server starts
      copyVersionFile();
    }
  },
  // Disable eslint for production build
  chainWebpack: config => {
    config.plugins.delete('eslint');
    // Run version update function during build
    config.plugin('copy').tap(args => {
      copyVersionFile();
      return args;
    });
  }
}
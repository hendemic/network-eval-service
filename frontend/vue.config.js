module.exports = {
  lintOnSave: false,
  devServer: {
    overlay: {
      warnings: false,
      errors: false
    }
  },
  // Disable eslint for production build
  chainWebpack: config => {
    config.plugins.delete('eslint');
  }
}
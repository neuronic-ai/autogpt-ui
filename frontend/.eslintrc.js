module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
  },
  extends: ['@nuxtjs/eslint-config-typescript', 'prettier', 'plugin:prettier/recommended'],
  plugins: ['prettier'],
  reportUnusedDisableDirectives: true,
};

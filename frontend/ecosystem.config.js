module.exports = {
  apps: [
    {
      name: 'app',
      script: '.output/server/index.mjs',
      args: '--enable-network-family-autoselection',
    },
  ],
};

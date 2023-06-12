// https://nuxt.com/docs/api/configuration/nuxt-config
import { NaiveUiResolver } from 'unplugin-vue-components/resolvers';
import Components from 'unplugin-vue-components/vite';
import nodePolyfills from 'rollup-plugin-polyfill-node';

export default defineNuxtConfig({
  srcDir: 'src',
  modules: ['@vueuse/nuxt', 'nuxt-viewport'],
  css: ['@/assets/scss/main.scss'],
  runtimeConfig: {
    apiBase: '',
    public: {
      apiBase: '',
    },
  },
  typescript: {
    shim: false,
  },
  viewport: {
    breakpoints: {
      xs: 0,
      sm: 640,
      md: 1024,
      lg: 1280,
      xl: 1536,
      xxl: 1920,
    },
    defaultBreakpoints: {
      desktop: 'lg',
      mobile: 'xs',
      tablet: 'md',
    },
    fallbackBreakpoint: 'lg',
  },
  build: {
    transpile:
      process.env.NODE_ENV === 'production'
        ? ['naive-ui', 'vueuc', 'ansi_up', '@css-render/vue3-ssr', '@juggle/resize-observer']
        : ['@juggle/resize-observer'],
  },
  vite: {
    plugins: [
      Components({
        resolvers: [NaiveUiResolver()],
      }),
    ],
    resolve: {
      alias: {
        stream: 'rollup-plugin-node-polyfills/polyfills/stream',
        events: 'rollup-plugin-node-polyfills/polyfills/events',
        assert: 'assert',
        crypto: 'crypto-browserify',
        util: 'util',
        http: 'stream-http',
        https: 'https-browserify',
        url: 'url',
      },
    },
    optimizeDeps: {
      esbuildOptions: {
        define: {
          global: 'window',
        },
      },
      include: process.env.NODE_ENV === 'development' ? ['naive-ui', 'vueuc', 'date-fns-tz/esm/formatInTimeZone'] : [],
    },
    build: {
      rollupOptions: {
        plugins: [nodePolyfills()],
      },
    },
  },
});

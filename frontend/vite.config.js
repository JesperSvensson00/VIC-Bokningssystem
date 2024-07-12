import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import VueDevTools from 'vite-plugin-vue-devtools'

// https://vitejs.dev/config/
export default ({mode}) => {
  
  const env = loadEnv(mode, "../")
  
  return defineConfig({
  envDir: "../",
  envPrefix: "PUBLIC_",
  plugins: [
    vue(),
    vueJsx(),
    VueDevTools(), 
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    }
  },
  define: {
    'SERVER_URL': JSON.stringify(`http://${env.VITE_SERVER_HOST}:${env.VITE_SERVER_PORT}`),
  },
  server: {
    port: env.VITE_FRONTEND_PORT || 5173,
    host: env.VITE_SERVER_HOST || 'localhost',
  },
  preview: {
    port: env.VITE_FRONTEND_PORT || 6173,
  },

})}

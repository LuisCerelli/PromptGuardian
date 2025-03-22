import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/

export default defineConfig({
  plugins: [react()],
  server: {
    cors: true, // Habilita CORS en el servidor de desarrollo de Vite
    proxy: {
      "/api": {
        target: "https://functionforhackmar25.azurewebsites.net",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});

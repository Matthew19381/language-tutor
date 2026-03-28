import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['logo.svg'],
      manifest: {
        name: 'LinguaAI - Nauka Języków',
        short_name: 'LinguaAI',
        description: 'Nauka języków obcych z pomocą AI',
        start_url: '/',
        display: 'standalone',
        orientation: 'portrait-primary',
        background_color: '#030712',
        theme_color: '#4f46e5',
        lang: 'pl',
        icons: [
          {
            src: '/logo.svg',
            sizes: 'any',
            type: 'image/svg+xml',
            purpose: 'any'
          },
          {
            src: '/logo.svg',
            sizes: 'any',
            type: 'image/svg+xml',
            purpose: 'maskable'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^\/api\/lessons\//,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'lessons-cache',
              expiration: { maxEntries: 50, maxAgeSeconds: 7 * 24 * 60 * 60 }
            }
          },
          {
            urlPattern: /^\/api\/flashcards\//,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'flashcards-cache',
              expiration: { maxEntries: 20, maxAgeSeconds: 24 * 60 * 60 }
            }
          }
        ]
      }
    })
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/audio': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})

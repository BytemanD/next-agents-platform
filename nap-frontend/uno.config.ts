import {
  defineConfig,
  presetUno,
  presetAttributify,
  presetIcons,
  transformerDirectives
} from 'unocss'

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      warn: true
    })
  ],
  transformers: [
    transformerDirectives()
  ],
  theme: {
    colors: {
      nap: {
        page: '#f6f7fb',
        surface: '#ffffff',
        'surface-hover': '#f4f5fa',
        border: '#e7e9f2',
        'border-strong': '#d9dce8',
        primary: '#4f46e5',
        'primary-hover': '#6366f1',
        'accent-soft': '#eef0ff',
        secondary: '#8b5cf6',
        success: '#16a34a',
        warning: '#d97706',
        error: '#dc2626',
        text: '#1e2431',
        'text-secondary': '#5b6478',
        'text-tertiary': '#9aa3b8'
      }
    }
  },
  shortcuts: {
    'nap-card': 'bg-nap-surface border border-nap-border rounded-xl p-4',
    'nap-btn': 'bg-nap-primary text-white px-4 py-2 rounded-lg hover:opacity-90 transition-opacity',
    'nap-input': 'bg-nap-surface border border-nap-border rounded-lg px-3 py-2 text-nap-text focus:border-nap-primary outline-none',
    'bg-nap-gradient': 'bg-gradient-to-br from-[#6366f1] to-[#8b5cf6]'
  }
})

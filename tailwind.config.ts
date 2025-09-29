import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2563eb', // blue-600
          light: '#3b82f6',
          dark: '#1e40af',
        },
        accent: '#f59e0b', // amber-500
      },
      boxShadow: {
        glow: '0 0 25px rgba(37, 99, 235, 0.35)',
      },
    },
  },
  plugins: [],
};

export default config;
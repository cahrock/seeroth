/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      colors: {
        'halal-green': '#10b981',
        'doubtful-amber': '#f59e0b',
        'haram-red': '#ef4444',
      },
    },
  },
  plugins: [],
}

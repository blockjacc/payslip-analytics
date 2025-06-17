/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{vue,js,ts}",
    "./index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: '#24c2ab',
        secondary: '#b1bacd',
      },
      fontFamily: {
        'serif': ['Zilla Slab', 'serif'],
        'sans': ['Open Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
}


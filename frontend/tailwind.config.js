/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#3F51FF", // bold royal blue
          dark: "#2E3AEF", // deeper blue for hovers
        },
        accent: {
          DEFAULT: "#82B1FF", // light sky blue
          dark: "#6999F7", // slightly darker on hover
        },
        surface: {
          DEFAULT: "#1F2BD8", // deep blue background
        },
      },
    },
  },
  plugins: [],
}
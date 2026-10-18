/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#08111f",
        panel: "#101b2d",
        violet: "#8b7bff",
        cyan: "#67e8f9",
      },
    },
  },
  plugins: [],
};

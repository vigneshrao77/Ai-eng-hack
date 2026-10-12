import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        gxp: {
          high: "#ef4444",
          medium: "#f59e0b",
          low: "#10b981",
        },
      },
    },
  },
  plugins: [],
};
export default config;

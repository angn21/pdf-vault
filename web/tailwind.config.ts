import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        vault: {
          bg: "#0b0f14",
          card: "#121820",
          border: "#1e2a38",
          accent: "#3b82f6",
          accent2: "#22d3ee",
          muted: "#8b9cb3",
        },
      },
      animation: {
        pulseRing: "pulseRing 2s ease-in-out infinite",
      },
      keyframes: {
        pulseRing: {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;

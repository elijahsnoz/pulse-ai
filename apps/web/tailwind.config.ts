import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./hooks/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          900: "#070b16",
          800: "#0a0e1a",
          700: "#101626",
          600: "#161d31",
          500: "#1d263f",
        },
        home: "#52b1ff",
        away: "#ff5d73",
        ember: "#ff3b6b",
        gold: "#ffd166",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
      keyframes: {
        breathe: {
          "0%, 100%": { opacity: "0.85", transform: "scale(1)" },
          "50%": { opacity: "1", transform: "scale(1.01)" },
        },
      },
      animation: {
        breathe: "breathe 6s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;

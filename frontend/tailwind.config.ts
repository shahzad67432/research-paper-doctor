import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#06090F",
        surface: "#0C1220",
        "surface-high": "#111926",
        "border-subtle": "#192336",
        border: "#1E2D44",
        accent: "#5B8DEF",
        "accent-bright": "#7BB3FF",
        gold: "#E8B84B",
        mint: "#34D399",
        amber: "#FBBF24",
        rose: "#F87171",
        "text-primary": "#DCE6F0",
        "text-secondary": "#6B82A0",
        "text-muted": "#364860",
      },
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;

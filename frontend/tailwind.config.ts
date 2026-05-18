import type { Config } from "tailwindcss";

const config: Config = {
    content: ["./src/**/*.{ts,tsx}"],
    theme: {
        extend: {
            fontFamily: {
                display: ["var(--font-display)", "Space Grotesk", "sans-serif"],
                body: ["var(--font-body)", "IBM Plex Sans", "sans-serif"]
            },
            colors: {
                ink: "hsl(220 18% 12%)",
                smoke: "hsl(220 15% 97%)",
                accent: "hsl(24 94% 52%)",
                ocean: "hsl(204 70% 46%)"
            },
            boxShadow: {
                glow: "0 0 0 1px rgba(15, 23, 42, 0.08), 0 10px 40px rgba(15, 23, 42, 0.12)"
            }
        }
    },
    plugins: []
};

export default config;

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        "ink": "#09090b",
        "panel": "#131318",
        "edge": "#26262c",
        "archgreen": "#4ade80",
        "archamber": "#f59e0b",
        "inksoft": "#a1a1aa"
},
      fontFamily: {
        "display": [
                "'Space Grotesk'",
                "system-ui",
                "sans-serif"
        ],
        "body": [
                "'Inter'",
                "system-ui",
                "sans-serif"
        ],
        "mono": [
                "'JetBrains Mono'",
                "ui-monospace",
                "monospace"
        ]
},
    },
  },
  plugins: [],
};

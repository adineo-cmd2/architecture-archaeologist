import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwind from '@astrojs/tailwind';

// https://docs.astro.build/en/reference/configuration-reference/
export default defineConfig({
  site: 'https://adineo-cmd2.github.io',
  base: '/architecture-archaeologist',
  integrations: [react(), tailwind()],
  server: {
    port: 4321,
  },
});

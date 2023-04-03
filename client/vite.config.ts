import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import eslint from 'vite-plugin-eslint';

// https://vitejs.dev/config/
export default ({ mode }) => {
  return defineConfig({
    plugins: [react(), eslint()],
    define: {
      global: {},
    }
})
}

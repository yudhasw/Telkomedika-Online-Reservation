/**  {import('tailwindcss').Config} */
export default {
    content: [
      "./app/templates/**/*.html", "./app/static/src/**/*.css",
      "node_modules/preline/dist/*.js"
    ],
    theme: {
      extend: {},
    },
    plugins: [
      require('preline/plugin'),
    ],
  };
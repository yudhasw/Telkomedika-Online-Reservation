/**  {import('tailwindcss').Config} */
export default {
    content: [
      "./app/templates/**/*.html", "./app/static/src/**/*.css",
      "node_modules/preline/dist/*.js"
    ],
    theme: {
      extend: {
            colors: {
                'tm-red': '#E51B24',
                'tm-cyan': '#00A3C8',
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            }
        }
    },
    plugins: [
      require('preline/plugin'),
    ],
  };
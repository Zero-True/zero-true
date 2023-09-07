/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import { createVuetify } from 'vuetify'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme:'light',
    themes: {
      light: {
        dark:true,
        colors: {
          primary: '#AE9FE8',
          secondary: '#424242',
          accent: '#FFDCA7',
          error: '#FF6F6F',
          info: '#4CBCFC',
          success: '#16B48E',
          warning: '#F49E6E'
        },
      },
    },
  },
})

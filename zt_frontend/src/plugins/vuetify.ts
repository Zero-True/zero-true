import "vuetify/styles";
import { createVuetify } from "vuetify";
import { aliases, ztIconSet } from '../iconsets/custom'
import { aliases as mdiAliases, mdi } from 'vuetify/iconsets/mdi'


export default createVuetify({
  defaults: {
    global: {
      elevation: 0 
    },
    VAppBar: {
      VBtn: {
        color: 'white'
      }
    },
    VBtn: {
      style:[{ 'text-transform': 'capitalize' }]
    },
    VBtnToggle: {
      density: 'comfortable',
      VBtn: {
        style: [{ borderRadius: 'inherit' }],
        class: [ 'text-bluegrey-darken-1']
      }
    },
    VFooter: {
      VListItem: {
        minHeight: 15
      }
    }
  },
  theme: {
    defaultTheme: "dark",
    themes: {
      dark: {
        dark: true,
        colors: {
          background: '#0d1316',
          primary: "#ae9ee8",
          secondary: "#424242",
          surface: '#1B2F3C', 
          bluegrey: "#5F7F93",
          'bluegrey-darken-1': '#3A586B',
          'bluegrey-darken-2': '#294455',
          'bluegrey-darken-3': '#1B2F3C', 
          'bluegrey-darken-4': '#0E1B23',
          accent: "#FFDCA7",
          error: "#FF6F6F",
          info: "#4CBCFC",
          success: "#16B48E",
          warning: "#F49E6E",
          white: 'white'
        },
      },
    },
  },
  icons: {
    defaultSet: 'ztIconSet',
    aliases,
    sets: {
      ztIconSet,
    },
  },
});

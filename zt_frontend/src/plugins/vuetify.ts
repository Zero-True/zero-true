import "vuetify/styles";
import { createVuetify } from "vuetify";
import { ztIcon } from '../iconsets/ztIcon'
import { aliases, mdi } from 'vuetify/iconsets/mdi'


export default createVuetify({
  display: {
    mobileBreakpoint: 'md',
  },
  defaults: {
    global: {
      elevation: 0 
    },
    VAppBar: {
      VBtn: {
        color: 'white',
        ripple: false
      }
    },
    VBtn: {
      style:[{ 'text-transform': 'capitalize' }],
      color: 'bluegrey-darken-2',
      class: [ 'text-bluegrey-darken-1']
    },
    VBtnToggle: {
      density: 'comfortable',
      VBtn: {
        style: [{ borderRadius: 'inherit' }],
        class: [ 'text-bluegrey-darken-1']
      }
    },
    VCard: {
      color: "bluegrey-darken-4"
    },
    VDivider: {
      class: 'border-opacity-100'
    },
    VFooter: {
      VListItem: {
        minHeight: 15
      }
    },
    VMenu: {
      contentClass: 'zt-menu' 
    },
    VSwitch:{
      baseColor: 'bluegrey-darken-3',
      color: 'primary',
			density:'compact',
			hideDetails: true,
		},
    VTextarea: {
      bgColor: 'bluegrey-darken-3'
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
          white: '#E7E8E9'
        },
      },
      light: {
        colors: {
          background: '#E7E8E9',
          primary: '#AE9FE8',
          secondary: '#5F7F93',
          surface: '#FFFFFF',
          bluegrey: "#5F7F93",
          'bluegrey-darken-1': '#3A586B',
          'bluegrey-darken-2': '#294455',
          'bluegrey-darken-3': '#1B2F3C', 
          'bluegrey-darken-4': '#0E1B23',
          accent: '#FFDCA7',
          error: '#FF6F6F',
          info: '#4CBCFC',
          success: '#16B48E',
          warning: '#F49E6E',
          white: '#E7E8E9'
        }
      }
    },
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
      ztIcon,
    },
  },
});

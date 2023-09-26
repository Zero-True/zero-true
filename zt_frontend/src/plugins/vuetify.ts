import { mdi } from "vuetify/iconsets/mdi";
import 'vuetify/styles';
import type { IconSet, IconProps } from "vuetify";
import ZTIcon from "@/components/ZTIcon.vue"
import { createVuetify } from 'vuetify'

const customIcons: IconSet = {
  component: ZTIcon,
};

export default createVuetify({
  theme: {
    defaultTheme:'light',
    themes: {
      light: {
        dark:true,
        colors: {
          primary: '#AE9FE8',
          secondary: '#424242',
          bluegrey: '#0E1B23',
          bluegrey2: '#1B2F3C',
          accent: '#FFDCA7',
          error: '#FF6F6F',
          info: '#4CBCFC',
          success: '#16B48E',
          warning: '#F49E6E'
        },
      },
    },
  },
  icons: {
    defaultSet: "mdi",
    sets: {
      mdi,
      custom: customIcons,
    },
  },
})

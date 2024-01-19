import { mdi } from "vuetify/iconsets/mdi";
import { h } from "vue";
import "vuetify/styles";
import type { IconSet, IconProps } from "vuetify";
import ZTIcon from "@/components/ZTIcon.vue";
import { createVuetify } from "vuetify";

const customSvgNameToComponent: any = { ZTIcon };

const customIcons: IconSet = {
  component: (props: IconProps) =>
    h(props.tag, [
      h(customSvgNameToComponent[props.icon as string], {
        class: "v-icon__svg",
      }),
    ]),
};

export default createVuetify({
  defaults: {
    global: {
      elevation: 0 
    },
    VBtnGroup: {
      density: 'comfortable'
    }
  },
  theme: {
    defaultTheme: "dark",
    themes: {
      dark: {
        dark: true,
        colors: {
          background: '#0d1316',
          primary: "#AE9FE8",
          secondary: "#424242",
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
});

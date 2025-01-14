import "vuetify/styles";
import { createVuetify } from "vuetify";
import { ztIcon } from "../iconsets/ztIcon";
import { aliases, mdi } from "vuetify/iconsets/mdi";
import { ref, watch } from "vue";
import { computed } from "vue";

// Define the reactive theme variable
export const currentTheme = ref("dark");

// Function to toggle between themes
export const toggleTheme = () => {
  currentTheme.value = currentTheme.value === "light" ? "dark" : "light";
  console.log("Theme switched to:", currentTheme.value);
};


const buttonTextColor = computed(() =>
  currentTheme.value === "light" ? "text-black" : "text-white"
);

const buttonIconColor = computed(() =>
  currentTheme.value === "light" ? "black" : "white"
);

const vuetify = createVuetify({
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
      style: [{ 'text-transform': 'capitalize' }],
      class: buttonTextColor.value,
    },
    VBtnToggle: {
      density: 'comfortable',
      VBtn: {
        style: [{ borderRadius: 'inherit' }],
        class: buttonTextColor.value,
      }
    },
    VSwitch: {
      baseColor: 'bluegrey-darken-3',
      color: 'primary',
      density:'compact',
      hideDetails: true,
    },
    VCard: {
      color: "bluegrey-darken-4",
      class: "scroll"
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
  },
  theme: {
    defaultTheme: currentTheme.value, // Set the initial theme
    themes: {
      light: {
        dark: false,
        colors: {
          background: "#F5F5F5",
          primary: "#5E35B1",
          secondary: "#546E7A",
          surface: "#FFFFFF",
          bluegrey: "#ECEFF1",
          "bluegrey-darken-1": "#212121",
          "bluegrey-darken-2": "#7A9AAE",
          "bluegrey-darken-3": "#97B4C6", // Increase contrast
          "bluegrey-darken-4": "#FFFFFF", 
          accent: "#FFD54F", // Higher-contrast accent
          error: "#D32F2F",
          info: "#1976D2",
          success: "#388E3C",
          warning: "#F57C00",
          white: "#FFFFFF",
          text: "#212121",
        },
      },
      dark: {
        dark: true,
        colors: {
          background: "#0d1316",
          primary: "#ae9ee8",
          secondary: "#424242",
          surface: "#1B2F3C",
          bluegrey: "#5F7F93",
          "bluegrey-darken-1": "#3A586B",
          "bluegrey-darken-2": "#294455",
          "bluegrey-darken-3": "#1B2F3C",
          "bluegrey-darken-4": "#0E1B23",
          accent: "#FFDCA7",
          error: "#FF6F6F",
          info: "#4CBCFC",
          success: "#16B48E",
          warning: "#F49E6E",
          white: "#E7E8E9",
        },
      },
    },
  },
  icons: {
    defaultSet: "mdi",
    aliases,
    sets: {
      mdi,
      ztIcon,
    },
  },
});

// Watch for theme changes and update the Vuetify theme dynamically
watch(currentTheme, (newTheme) => {
  vuetify.theme.global.name.value = newTheme; // Update the global theme
});

export default vuetify;
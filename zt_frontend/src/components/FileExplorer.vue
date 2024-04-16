<template>
    <v-navigation-drawer v-if="$devMode && !isMobile && !isAppRoute" v-model="localDrawer" app class="sidebar">
      <v-treeview
        v-model="tree"
        :items="items"
        item-key="name"
        activatable
        open-on-click
      >
        <template v-slot:prepend="{ item }">
          <v-icon v-if="!item.file">
            {{ 'mdi-folder' }}
          </v-icon>
          <v-icon v-else>
            {{ fileIcon(item.file) }}
          </v-icon>
        </template>
      </v-treeview>
      <v-divider></v-divider>
      <v-file-input
        label="Upload File"
        prepend-icon="mdi-upload"
        filled
        @change="handleFileChange('sidebar_uploader', $event)"
      ></v-file-input>
    </v-navigation-drawer>
  </template>
  
  <script>
  import { defineComponent, computed, watch } from 'vue';
  
  export default defineComponent({
    name: 'SidebarComponent',
    props: {
      drawer: Boolean,
      items: Array,
      tree: Array,
      fileIcon: Function,
      handleFileChange: Function,
      isMobile: Boolean,  // Added to receive isMobile prop
      isAppRoute: Boolean  // Added to receive isAppRoute prop
    },
    emits: ['update:drawer'],
    setup(props, { emit }) {
      const localDrawer = computed({
        get: () => props.drawer,
        set: (val) => emit('update:drawer', val)
      });
  
      watch(() => props.drawer, (newVal) => {
        if (newVal !== localDrawer.value) {
          localDrawer.value = newVal;
        }
      });
  
      return { localDrawer };
    }
  });
  </script>
  
  <style scoped>
  /* Your styles here */
  </style>
  
<!-- <template>
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
</style> -->

<template>
  <v-navigation-drawer v-if="$devMode && !isMobile && !isAppRoute" v-model="localDrawer" app class="sidebar">
    <v-treeview
      v-model="tree"
      :items="items"
      item-value="id"
      :load-children="loadSubFolder"
      activatable
      open-on-click
      @update:open="onFolderToggle"
    >
      <template v-slot:prepend="{ item }">
        <v-icon v-if="item.file === 'folder'">
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
      @change="handleFileChange"
    ></v-file-input>
  </v-navigation-drawer>
</template>

<script>
import { defineComponent, ref, onMounted, watch } from 'vue';
import axios from 'axios';

export default defineComponent({
  name: 'SidebarComponent',
  props: {
    drawer: Boolean,
    items: Array,
    tree: Array,
    fileIcon: Function,
    isMobile: Boolean,
    isAppRoute: Boolean,
  },
  emits: ['update:drawer', 'update:items', 'handleFileChange'],
  setup(props, { emit }) {
    const localDrawer = ref(props.drawer);
    const localItems = ref(props.items || []);

    watch(() => props.drawer, (newValue) => {
      localDrawer.value = newValue;
    });

    watch(localDrawer, (newValue) => {
      emit('update:drawer', newValue);
    });

    const loadInitialData = async () => {
      try {
        const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}api/get_files`);
        localItems.value = response.data.files;
        emit('update:items', response.data.files);
      } catch (error) {
        console.error('Failed to load initial data:', error);
      }
    };

    onMounted(() => {
      loadInitialData();
    });

    const loadSubFolder = async (item) => {
      if (item.children && item.children.length > 0) {
        return item.children;
      }

      try {
        const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}api/get_children`, { params: { path: item.id } });
        item.children = response.data.files;
        return item.children;
      } catch (error) {
        console.error('Failed to load subfolder:', error);
        return [];
      }
    };


    const onFolderToggle = async (openItems) => {
      for (const id of openItems) {
        const item = findItemById(localItems.value, id);
        if (item && item.file === 'folder' && (!item.children || item.children.length === 0)) {
          await loadSubFolder(item);
        }
      }
    };


    const findItemById = (items, id) => {
      for (const item of items) {
        if (item.id === id) {
          return item;
        }
        if (item.children) {
          const found = findItemById(item.children, id);
          if (found) {
            return found;
          }
        }
      }
      return null;
    };

    const handleFileChange = async (file) => {
      if (file) {
        const formData = new FormData();
        formData.append("file", file);
        try {
          const response = await axios.post(`${import.meta.env.VITE_BACKEND_URL}api/upload_file`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          console.log("File processed", response.data);
          // Reload the file list after successful upload
          await loadInitialData();
        } catch (error) {
          console.error("Error processing file:", error.response);
        }
      } else {
        console.error("No file selected");
      }
    };

    return { 
      localDrawer, 
      localItems, 
      loadSubFolder, 
      onFolderToggle, 
      handleFileChange 
    };
  }
});
</script>
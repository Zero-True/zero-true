<template>
  <v-navigation-drawer
    v-if="$devMode && !isMobile && !isAppRoute"
    v-model="localDrawer"
    app
    class="sidebar"
    color="bluegrey-darken-4"
  >
    <div class="d-flex">
      <v-btn
        v-if="pathStack.length > 0"
        @click="goBack"
        color="bluegrey-darken-4"
        icon="mdi-arrow-left"
      />
      <v-spacer />
      <FileUploader :current-path="currentPath" @file-uploaded="refreshFiles" />
      <v-btn
        color="bluegrey-darken-4"
        icon="mdi-close"
        @click="localDrawer = false"
      />
    </div>

    <v-list>
      <v-list-item
        v-for="item in localItems"
        :key="item.id"
        @click="handleItemClick(item)"
      >
        <v-list-item-icon>
          <v-icon v-if="item.file === 'folder'">{{ "mdi-folder" }}</v-icon>
          <v-icon v-else>{{ fileIcon(item.file) }}</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch } from "vue";
import axios from "axios";
import FileUploader from "@/components/FileUploader.vue";
export default defineComponent({
  name: "SidebarComponent",
  components: {
    FileUploader,
  },
  props: {
    drawer: Boolean,
    items: Array,
    handleFileChange: Function,
    isMobile: Boolean,
    isAppRoute: Boolean,
  },
  emits: ["update:drawer", "update:items"],
  setup(props, { emit }) {
    const localDrawer = ref(props.drawer);
    const localItems = ref(props.items || ([] as any[]));
    const currentPath = ref("." as string);
    const pathStack = ref([] as string[]);
    watch(
      () => props.drawer,
      (newValue) => {
        localDrawer.value = newValue;
      }
    );
    watch(localDrawer, (newValue) => {
      emit("update:drawer", newValue);
    });
    const loadFiles = async (path: string) => {
      try {
        const response = await axios.get(
          `${import.meta.env.VITE_BACKEND_URL}api/get_children`,
          { params: { path } }
        );
        localItems.value = response.data.files;
        emit("update:items", response.data.files);
      } catch (error) {
        console.error("Failed to load files:", error);
      }
    };
    onMounted(() => {
      loadFiles(currentPath.value);
    });
    const handleItemClick = (item: any) => {
      if (item.file === "folder") {
        pathStack.value.push(currentPath.value);
        currentPath.value = item.id;
        loadFiles(currentPath.value);
      }
    };
    const goBack = () => {
      if (pathStack.value.length > 0) {
        currentPath.value = pathStack.value.pop() || ".";
        loadFiles(currentPath.value);
      }
    };
    const refreshFiles = () => {
      loadFiles(currentPath.value);
    };

    const fileIcon = (extension: string) => {
      switch (extension) {
        case "html":
          return "mdi:mdi-language-html5";
        case "js":
          return "mdi:mdi-nodejs";
        case "json":
          return "mdi:mdi-code-json";
        case "md":
          return "mdi:mdi-language-markdown";
        case "pdf":
          return "mdi:mdi-file-pdf-box";
        case "png":
          return "mdi:mdi-file-image";
        case "txt":
          return "mdi:mdi-file-document-outline";
        case "xls":
          return "mdi:mdi-file-excel";
        case "folder":
          return "mdi:mdi-folder";
        default:
          return "mdi:mdi-file";
      }
    };

    return {
      localDrawer,
      localItems,
      handleItemClick,
      goBack,
      pathStack,
      currentPath,
      refreshFiles,
      fileIcon,
    };
  },
});
</script>

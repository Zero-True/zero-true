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
      <FileFolderCreator :current-path="currentPath" @item-created="refreshFiles" />
      <FileUploader :current-path="currentPath" @file-uploaded="refreshFiles" />
      <v-btn
        color="bluegrey-darken-4"
        icon="mdi-refresh"
        @click="refreshFiles"
      />
      <v-btn
        color="bluegrey-darken-4"
        icon="mdi-close"
        @click="localDrawer = false"
      />
    </div>

    <v-list>
      <template v-for="item in localItems" :key="item.id">
        <!-- Main item -->
        <v-list-item>
          <template v-slot:prepend>
            <v-icon v-if="item.file === 'folder'">{{ "mdi-folder" }}</v-icon>
            <v-icon v-else>{{ fileIcon(item.file) }}</v-icon>
          </template>
          
          <v-list-item-title @click="handleItemClick(item)">{{ item.title }}</v-list-item-title>
          
          <template v-slot:append>
            <v-menu :close-on-content-click="false">
              <template v-slot:activator="{ props }">
                <v-btn
                  icon
                  variant="text"
                  density="compact"
                  class="mr-2"
                  v-bind="props"
                >
                  <v-icon size="small">mdi-dots-vertical</v-icon>
                </v-btn>
              </template>
              <v-list>
                 <v-list-item>
                <FileFolderDownloadDialog
                  :current-path="currentPath"
                  :title="item.title"
                  :file="item.file"
                  @file-downloaded="refreshFiles"
                />
              </v-list-item>
                <v-list-item v-if="item.file !== 'folder' && !isProtectedFile(item.title)">
                  <FileEditorDialog 
                    :file-path="item.id"
                    :file-name="item.title"
                    @file-saved="refreshFiles"
                  />
                </v-list-item>
                <v-list-item v-if="!isProtectedFile(item.title)">
                  <RenameDialog
                    :file-path="item.id"
                    :file-name="item.title"
                    :is-protected-file="isProtectedFile"
                    :is-folder="item.file === 'folder'"
                    @item-renamed="refreshFiles"
                  />
                </v-list-item>
                <v-list-item v-if="!isProtectedFile(item.title)">
                  <DeleteDialog
                    :file-path="item.id"
                    :file-name="item.title"
                    :is-protected-file="isProtectedFile"
                    @item-deleted="refreshFiles"
                  />
                </v-list-item>
              </v-list>
            </v-menu>
          </template>
        </v-list-item>
      </template>
    </v-list>

    <v-snackbar
      v-model="showError"
      color="error"
      :timeout="5000"
    >
      {{ errorMessage }}
      <template v-slot:actions>
        <v-btn
          color="white"
          variant="text"
          @click="showError = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-navigation-drawer>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch } from "vue";
import axios from "axios";
import FileUploader from "@/components/FileUploader.vue";
import FileFolderCreator from "@/components/FileFolderCreator.vue";
import RenameDialog from "@/components/FileFolderRenameDialog.vue";
import DeleteDialog from "@/components/FileFolderDeleteDialog.vue";
import FileEditorDialog from '@/components/FileEditorDialog.vue'
import FileFolderDownloadDialog from "@/components/FileFolderDownloadDialog.vue";



export default defineComponent({
  name: "SidebarComponent",
  components: {
    FileUploader,
    FileFolderCreator,
    RenameDialog,
    DeleteDialog,
    FileEditorDialog,
    FileFolderDownloadDialog
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
    const newItemName = ref("");
    const itemTypes = [
      { text: 'Folder', value: 'folder' },
      { text: 'File', value: 'file' }
    ];
    const errorMessage = ref("");
    const showError = ref(false);
    // Define the list of protected files
    const protectedFiles = ref(["requirements.txt", "notebook.ztnb","zt_db.db","zt_db.db.wal"]);

    // Function to check if a file is protected
    const isProtectedFile = (filename: string) => {
      return protectedFiles.value.includes(filename);
    };
    watch(
      () => props.drawer,
      (newValue) => {
        localDrawer.value = newValue;
      }
    );
    watch(localDrawer, (newValue) => {
      emit("update:drawer", newValue);
      if (newValue) {
        refreshFiles();
      }
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
      newItemName,
      itemTypes,
      errorMessage,
      showError,
      isProtectedFile,
    };
  },
});
</script>

<style scoped>
.clickable-item {
  cursor: pointer;
}
.clickable-item:hover {
  opacity: 0.8;
  text-decoration: underline;
}
</style>
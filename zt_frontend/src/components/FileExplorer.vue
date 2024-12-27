<template>
  <v-navigation-drawer
    v-if="$devMode && !isMobile && !isAppRoute"
    v-model="localDrawer"
    app
    class="sidebar"
    color="bluegrey-darken-4"
  >
    <div class="search-field-container">
      <v-text-field
  v-model="searchQuery"
  placeholder="Search"
  variant="outlined"
  density="compact"
  hide-details
  class="search-field"
  clearable
  :loading="isSearching"
  @click:clear="handleSearchClear"
>
  <template v-slot:prepend-inner>
    <v-icon
      icon="mdi-magnify"
      size="small"
      class="search-icon"
    />
  </template>
</v-text-field>
    </div>  

    <div class="section-header d-flex align-center px-4">
      <div class="section-title">File Explorer</div>
      <v-spacer></v-spacer>
      <div class="section-actions">
        <FileFolderCreator :current-path="currentPath" @item-created="refreshFiles" />
        <FileUploader :current-path="currentPath" @file-uploaded="refreshFiles" />
        <v-btn
          color="transparent"
          icon="mdi-refresh"
          @click="refreshFiles"
          size="small"
          class="action-btn"
        />
      </div>
    </div>

    <v-list class="file-tree">
      <FileTreeNode 
        v-for="item in filteredItems" 
        :key="item.id"
        :item="item"
        :depth="0"
        :current-path="currentPath"
        @refresh-files="refreshFiles"
      />
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
import { defineComponent, ref, onMounted, watch, computed } from "vue";
import axios from "axios";
import FileUploader from "@/components/FileUploader.vue";
import FileFolderCreator from "@/components/FileFolderCreator.vue";
import RenameDialog from "@/components/FileFolderRenameDialog.vue";
import DeleteDialog from "@/components/FileFolderDeleteDialog.vue";
import FileEditorDialog from '@/components/FileEditorDialog.vue';
import FileFolderDownloadDialog from "@/components/FileFolderDownloadDialog.vue";
import FileTreeNode from "@/components/FileTreeNode.vue";
import { debounce } from "lodash";

export default defineComponent({
  name: "SidebarComponent",
  components: {
    FileUploader,
    FileFolderCreator,
    RenameDialog,
    DeleteDialog,
    FileEditorDialog,
    FileFolderDownloadDialog,
    FileTreeNode
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
    const errorMessage = ref("");
    const showError = ref(false);
    const searchQuery = ref("");
    const searchResults = ref<any[]>([]);
    const isSearching = ref(false);

    const protectedFiles = ref(["requirements.txt", "notebook.ztnb","zt_db.db","zt_db.db.wal"]);

    const isProtectedFile = (filename: string) => {
      return protectedFiles.value.includes(filename);
    };

    const handleSearchClear = () => {
      searchQuery.value = "";
      searchResults.value = [];
      isSearching.value = false;
      refreshFiles();
    };

    const debouncedSearch = debounce(async (query: string) => {
      if (!query || query.length < 3) {
        searchResults.value = [];
        isSearching.value = false;
        return;
      }

      try {
        isSearching.value = true;
        const response = await axios.get(
          `${import.meta.env.VITE_BACKEND_URL}api/search_files`,
          { params: { query } }
        );
        searchResults.value = response.data.files || [];
      } catch (error) {
        console.error("Search failed:", error);
        errorMessage.value = "Failed to search files";
        showError.value = true;
        searchResults.value = [];
      } finally {
        isSearching.value = false;
      }
    }, 300);

    watch(searchQuery, (newQuery) => {
      if (!newQuery || newQuery.length === 0) {
        handleSearchClear();
        return;
      }
      if (newQuery.length >= 3) {
        debouncedSearch(newQuery);
      }
    });

    const filteredItems = computed(() => {
      return searchQuery.value.length >= 3 ? (searchResults.value || []) : (localItems.value || []);
    });

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

    const loadRootFolder = async () => {
    try {
      const response = await axios.get(
        `${import.meta.env.VITE_BACKEND_URL}api/get_files`
      );
      if (response.data.files && response.data.files[0]) {
        // Set root folder structure
        localItems.value = response.data.files;
        if (localItems.value[0].file === 'folder') {
        localItems.value[0].isExpanded = true;
      }
      }
      emit("update:items", localItems.value);
    } catch (error) {
      console.error("Failed to load root folder:", error);
      errorMessage.value = "Failed to load files";
      showError.value = true;
    }
  };

  onMounted(() => {
    loadRootFolder(); // Load root folder structure initially
  });

  const refreshFiles = () => {
    loadRootFolder(); // Refresh from root
  };

    return {
      localDrawer,
      localItems,
      pathStack,
      currentPath,
      refreshFiles,
      errorMessage,
      showError,
      isProtectedFile,
      filteredItems,
      searchQuery,
      isSearching,
      handleSearchClear,
    };
  },
});
</script>

<style scoped>
.search-field :deep(.v-field) {
  margin: 4px 8px !important;
  height: 33px;
  border-radius: 8px;        /* Rounded corners */
  border-bottom: none;
}

.search-field :deep(.v-field__input) {
  color: #ecf0f1;            /* Light text color */
  font-size: 11px;
}

/* Section Header */
.section-header {
  height: 32px;
  padding: 0 16px;
  display: flex;
  align-items: center;
}

.section-title {
  color: white;
  font-family: 'Pathway Extreme', sans-serif;
  font-size: 13px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Icons */
:deep(.v-icon) {
  font-size: 16px !important;
  width: 16px;
  height: 16px;
}

:deep(.action-btn.v-btn) {
  width: 24px !important;
  min-width: 24px !important;
  height: 24px !important;
  padding: 0 !important;
  margin: 0 !important;
  
  .v-icon {
    color: #3A586B !important;
  }
  
  &:hover .v-icon {
    color: #FFFFFF !important;
  }
}
.sidebar {
  scrollbar-width: thin;
  scrollbar-color: rgba(58, 88, 107, 0.5) transparent;
}

.sidebar::-webkit-scrollbar {
  width: 6px; /* Slightly wider to accommodate roundness */
}

.sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar::-webkit-scrollbar-thumb {
  background-color: rgba(58, 88, 107, 0.5);
  border-radius: 50px; /* Significantly more rounded */
  border: 2px solid transparent; /* Creates a softer, rounder appearance */
  background-clip: content-box; /* Allows the border to create additional roundness */
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(58, 88, 107, 0.7);
}

/* Remove padding from file-tree to allow full content scrolling */
.file-tree {
  padding: 0 !important;
  overflow: hidden; /* Let parent handle scrolling */
}
</style>
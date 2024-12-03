<template>
    <div class="file-tree-node">
      <div class="node-item" :class="{ 'is-folder': item.file === 'folder', 'is-active': isActive, 'is-expanded': isExpanded }" @click.stop="handleClick">
        <div class="node-content">
          <v-icon v-if="item.file === 'folder'" class="folder-toggle-icon" @click.stop="toggleExpand">
            {{ isExpanded ? 'mdi-chevron-down' : 'mdi-chevron-right' }}
          </v-icon>
          <v-icon class="file-icon">
            {{ item.file === 'folder' ? (isExpanded ? 'mdi-folder-open' : 'mdi-folder') : fileIcon(item.file) }}
          </v-icon>
          <span class="file-name" :title="item.title">{{ item.title }}</span>
        </div>
        <v-menu :close-on-content-click="false"  location="end">
          <template v-slot:activator="{ props }">
            <v-btn icon variant="text" density="compact" class="file-actions-menu" v-bind="props">
              <v-icon size="small">mdi-dots-vertical</v-icon>
            </v-btn>
          </template>
          <v-list class="menu-list">
            <v-list-item class="menu-item">
              <FileFolderDownloadDialog :current-path="currentPath" :title="item.title" :file="item.file" @file-downloaded="$emit('refresh-files')" />
            </v-list-item>
            <v-list-item v-if="item.file !== 'folder' && !isProtectedFile(item.title)" class="menu-item">
              <FileEditorDialog :file-path="item.id" :file-name="item.title" @file-saved="$emit('refresh-files')" />
            </v-list-item>
            <v-list-item v-if="!isProtectedFile(item.title)" class="menu-item">
              <RenameDialog :file-path="item.id" :file-name="item.title" :is-protected-file="isProtectedFile" :is-folder="item.file === 'folder'" @item-renamed="$emit('refresh-files')" />
            </v-list-item>
            <v-list-item v-if="!isProtectedFile(item.title)" class="menu-item">
              <DeleteDialog :file-path="item.id" :file-name="item.title" :is-protected-file="isProtectedFile" @item-deleted="$emit('refresh-files')" />
            </v-list-item>
          </v-list>
        </v-menu>
      </div>
      <div v-if="item.file === 'folder' && isExpanded" class="children-container">
        <FileTreeNode v-for="childItem in childItems" :key="childItem.id" :item="childItem" :depth="depth + 1" :current-path="item.id" @item-click="handleChildClick" @refresh-files="$emit('refresh-files')" />
      </div>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, ref } from 'vue';
  import axios from 'axios';
  import FileEditorDialog from '@/components/FileEditorDialog.vue';
  import FileFolderDownloadDialog from '@/components/FileFolderDownloadDialog.vue';
  import RenameDialog from '@/components/FileFolderRenameDialog.vue';
  import DeleteDialog from '@/components/FileFolderDeleteDialog.vue';
  
  export default defineComponent({
    name: 'FileTreeNode',
    components: {
      FileEditorDialog,
      FileFolderDownloadDialog,
      RenameDialog,
      DeleteDialog
    },
    props: {
      item: {
        type: Object,
        required: true
      },
      depth: {
        type: Number,
        default: 0
      },
      currentPath: {
        type: String,
        default: '.'
      }
    },
    emits: ['item-click', 'refresh-files'],
    setup(props, { emit }) {
      const isExpanded = ref(false);
      const childItems = ref<any[]>([]);
      const isActive = ref(false);
  
      const protectedFiles = ref(["requirements.txt", "notebook.ztnb", "zt_db.db", "zt_db.db.wal"]);
  
      const isProtectedFile = (filename: string) => {
        return protectedFiles.value.includes(filename);
      };
  
      const toggleExpand = async () => {
        if (props.item.file === 'folder') {
          isExpanded.value = !isExpanded.value;
          if (isExpanded.value && childItems.value.length === 0) {
            try {
              const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}api/get_children`, { params: { path: props.item.id } });
              childItems.value = response.data.files;
            } catch (error) {
              console.error('Failed to load child items:', error);
            }
          }
        }
      };
  
      const handleClick = () => {
        isActive.value = true;
        emit('item-click', props.item);
      };
  
      const handleChildClick = (childItem: any) => {
        emit('item-click', childItem);
      };
  
      const fileIcon = (extension: string) => {
        switch (extension) {
          case "html": return "mdi:mdi-language-html5";
          case "js": return "mdi:mdi-nodejs";
          case "json": return "mdi:mdi-code-json";
          case "md": return "mdi:mdi-language-markdown";
          case "pdf": return "mdi:mdi-file-pdf-box";
          case "png": return "mdi:mdi-file-image";
          case "txt": return "mdi:mdi-file-document-outline";
          case "xls": return "mdi:mdi-file-excel";
          default: return "mdi:mdi-file";
        }
      };
  
      return {
        isExpanded,
        toggleExpand,
        childItems,
        handleClick,
        handleChildClick,
        fileIcon,
        isProtectedFile,
        isActive
      };
    }
  });
  </script>
  
  <style scoped>
  .file-tree-node {
    user-select: none;
    position: relative;
    width: 100%;
  }
  
  .node-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 25px;
    cursor: pointer;
    border-radius: 4px;
    padding-right: 4px;
    transition: background-color 0.2s ease;
  }
  
  .node-content {
    display: flex;
    align-items: center;
    overflow: hidden;
    flex-grow: 1;
    min-width: 0;
  }
  
  .folder-toggle-icon {
    width: 20px;
    min-width: 20px;
    margin-right: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .file-icon {
    width: 20px;
    min-width: 20px;
    margin-right: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #B0BEC5;
  }
  
  .file-name {
    font-family: 'Pathway Extreme', sans-serif;
    font-size: 12px;
    color: #B0BEC5;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex-grow: 1;
    min-width: 0;
  }
  
  .node-item:hover {
    background-color: rgba(98, 114, 164, 0.1);
  }
  
  .node-item:hover .file-name {
    color: #FFFFFF;
  }
  
  .file-actions-menu {
    opacity: 0;
    margin-left: 4px;
  }
  
  .node-item:hover .file-actions-menu {
    opacity: 1;
  }
  
  .children-container {
    border-left: 1px solid rgba(230, 231, 236, 0.2);
    margin-left: 7px;
  }
  
  .file-actions-menu .v-icon {
    color: #607D8B;
    font-size: 16px;
  }
  
  .file-actions-menu:hover .v-icon {
    color: #FFFFFF;
  }
 

.menu-item {
  height: 20px !important;
  min-height: unset !important;
}

/* Update the menu-list styles */
.menu-list :deep(.v-list-item-title),
.menu-list :deep(.v-list-item__content) {
  color: #B0BEC5 !important;
  font-family: 'Pathway Extreme', sans-serif !important;
  font-size: 11px !important;
}

.menu-list :deep(.v-list-item:hover) .v-list-item-title,
.menu-list :deep(.v-list-item:hover) .v-list-item__content {
  color: #FFFFFF !important;
}

.menu-list :deep(.v-icon) {
  color: #607D8B;
  font-size: 16px;
  margin-right: 6px;
}

.menu-list :deep(.v-list-item:hover .v-icon) {
  color: #FFFFFF;
}
  </style>
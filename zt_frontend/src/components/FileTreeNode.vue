
<template>
  <div class="file-tree-node"
   draggable="true"
    @dragstart="handleDragStart"
    @dragover="handleDragOver"
    @dragenter="handleDragEnter" 
    @dragleave="handleDragLeave"
    @drop="handleDrop"
    @dragend="handleDragEnd"
  >
    <div 
      class="node-item" 
      :class="{ 
        'is-folder': item.file === 'folder', 
        'is-active': isActive, 
        'is-expanded': isExpanded,
        'menu-open': menuOpen,
        'drag-over': isDragOver,
        'drag-target': isDragTarget,
        'dragging': isDragging
      }" 
      @click.stop="handleClick"
      @contextmenu.prevent="handleRightClick"
    >
      <div class="node-content">
        <v-icon v-if="item.file === 'folder'" class="folder-toggle-icon">
          {{ isExpanded ? 'mdi-chevron-down' : 'mdi-chevron-right' }}
        </v-icon>
        <v-icon class="file-icon">
          {{ item.file === 'folder' ? (isExpanded ? 'mdi-folder-open' : 'mdi-folder') : fileIcon(item.file) }}
        </v-icon>
        <span class="file-name" :title="item.title">{{ item.title }}</span>
      </div>
      <v-menu 
        :close-on-content-click="false"  
        location="bottom end"
        v-model="menuOpen"
        :activator="menuActivator"
        @update:model-value="updateMenuOpenState"
        :offset="[-5, 60]"
        min-width="100"
      >
        <template v-slot:activator="{ props }">
          <v-btn icon variant="text" density="compact" class="file-actions-menu" v-bind="menuActivator ? {} : props">
            <v-icon size="small">mdi-dots-vertical</v-icon>
          </v-btn>
        </template>
        <v-list class="menu-list">
          <v-list-item v-if="item.file === 'folder'" class="menu-item">
          <FileFolderCreator :current-path="item.id" variant="text" @item-created= handleRefresh />
          </v-list-item>
          <v-list-item class="menu-item">
            <FileFolderDownloadDialog :current-path="currentPath" :title="item.title" :file="item.file" @file-downloaded= handleRefresh />
          </v-list-item>
          <v-list-item v-if="item.file !== 'folder' && !isProtectedFile(item.title)" class="menu-item">
            <FileEditorDialog :file-path="item.id" :file-name="item.title" @file-saved="$emit('refresh-files')" />
          </v-list-item>
          <v-list-item v-if="!isProtectedFile(item.title)" class="menu-item">
            <RenameDialog :file-path="item.id" :file-name="item.title" :is-protected-file="isProtectedFile" :is-folder="item.file === 'folder'" @item-renamed= handleRefresh />
          </v-list-item>
          <v-list-item v-if="!isProtectedFile(item.title)" class="menu-item">
            <DeleteDialog :file-path="item.id" :file-name="item.title" :is-protected-file="isProtectedFile" @item-deleted= handleRefresh />
          </v-list-item>
        </v-list>
      </v-menu>
    </div>
    <div v-if="item.file === 'folder' && isExpanded" class="children-container">
      <FileTreeNode 
        v-for="childItem in childItems" 
        :key="childItem.id" 
        :item="childItem" 
        :depth="depth + 1" 
        :current-path="item.id" 
        @item-click="handleChildClick" 
        @refresh-files="handleRefresh"  
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref} from 'vue';
import axios from 'axios';
import FileEditorDialog from '@/components/FileEditorDialog.vue';
import FileFolderDownloadDialog from '@/components/FileFolderDownloadDialog.vue';
import RenameDialog from '@/components/FileFolderRenameDialog.vue';
import DeleteDialog from '@/components/FileFolderDeleteDialog.vue';
import FileFolderCreator from '@/components/FileFolderCreator.vue'; // Import the component

let currentlyOpenMenu: any = null;


export default defineComponent({
  name: 'FileTreeNode',
  components: {
    FileEditorDialog,
    FileFolderDownloadDialog,
    RenameDialog,
    DeleteDialog,
    FileFolderCreator
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
    const menuOpen = ref(false);
    const menuActivator = ref<Element | undefined>(undefined);
    const isDragging = ref(false);
    const isDragOver = ref(false);
    const isDragTarget = ref(false);
    const protectedFiles = ref(["requirements.txt", "notebook.ztnb", "zt_db.db", "zt_db.db.wal"]);

    watch(menuOpen, (newVal) => {
      if (newVal) {
        if (currentlyOpenMenu && currentlyOpenMenu !== menuOpen) {
          currentlyOpenMenu.value = false;
        }
        currentlyOpenMenu = menuOpen;
      }
    });

    onMounted(() => {
      if (props.depth === 0 && props.item.file === 'folder') {
        isExpanded.value = true;
        refreshChildren();
      }
    });

    const isProtectedFile = (filename: string) => {
      return protectedFiles.value.includes(filename);
    };

    const refreshChildren = async () => {
    if (props.item.file === 'folder' && isExpanded.value) {
      try {
        const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}api/get_children`, { 
          params: { path: props.item.id } 
        });
        childItems.value = response.data.files;
      } catch (error) {
        console.error('Failed to refresh child items:', error);
      }
    }
  };

      const handleRefresh = () => {
        refreshChildren();
        emit('refresh-files');
      };

      watch(() => props.item, async () => {
        await refreshChildren();
      });


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
      if (!menuOpen.value) {
      isActive.value = true;
      emit('item-click', props.item);
      if (props.item.file === 'folder') {
        toggleExpand();
      }
    }
    };

    const handleChildClick = (childItem: any) => {
      emit('item-click', childItem);
    };

    const handleRightClick = (event: MouseEvent) => {
        event.preventDefault();
        menuActivator.value = event.currentTarget as Element;
        menuOpen.value = true;
      };

    const updateMenuOpenState = (isOpen: boolean) => {
      if (!isOpen) {
        menuActivator.value = undefined;
      }
    };

    const handleDragStart = (event: DragEvent) => {
    event.stopPropagation(); // Stop event from bubbling to parent folders
    
    if (isProtectedFile(props.item.title)) {
      event.preventDefault();
      return;
    }
    
    isDragging.value = true;
    
    // Use item.id which contains the full relative path
    const sourcePath = props.item.id;

    console.log('Drag started:', {
      sourcePath,
      itemTitle: props.item.title,
      currentPath: props.currentPath,
      itemId: props.item.id
    });

    const dragData = {
      id: sourcePath,
      type: props.item.file,
      name: props.item.title,
      path: sourcePath,
      parentPath: props.currentPath
    };
    
    event.dataTransfer?.setData('text/plain', JSON.stringify(dragData));
};
   
const scrollOnDrag = (event: DragEvent) => {
      const scrollMargin = 50; // Margin in pixels to start scrolling
      const scrollSpeed = 20; // Speed of scrolling

      const { clientY } = event;
      const { innerHeight } = window;

      if (clientY < scrollMargin) {
        window.scrollBy(0, -scrollSpeed);
      } else if (clientY > innerHeight - scrollMargin) {
        window.scrollBy(0, scrollSpeed);
      }
    };

    const handleDragOver = (event: DragEvent) => {
  event.preventDefault();
  scrollOnDrag(event);
  // Allow dropping into folders
  if (props.item.file === 'folder') {
    isDragOver.value = true;
    event.dataTransfer!.dropEffect = 'move';
  }
};

const handleDrop = async (event: DragEvent) => {
  event.preventDefault();
  event.stopPropagation();
  isDragOver.value = false;

  try {
    const dragData = JSON.parse(event.dataTransfer?.getData('text/plain') || '{}');
    let targetPath = props.item.id;

    // Check if the target is a file, if so, use the parent folder as the target
    if (props.item.file !== 'folder') {
      targetPath = props.currentPath;
    }

    console.log('Drop:', {
      sourcePath: dragData.path,
      targetPath: targetPath,
      dragData: dragData
    });

    // Prevent moving folder into itself or its children
    if (targetPath.startsWith(dragData.path) || dragData.path === targetPath) {
      console.warn('Invalid move: Cannot move folder into itself or its children');
      return;
    }

    // Clean paths - use exact paths from item.id
    const cleanTargetPath = targetPath;
    const cleanSourcePath = dragData.path;
    const newPath = `${cleanTargetPath}/${dragData.name}`;

    await axios.post(`${import.meta.env.VITE_BACKEND_URL}api/move_item`, {
      sourceId: cleanSourcePath,
      targetId: cleanTargetPath,
      sourcePath: cleanSourcePath,
      targetPath: newPath
    });

    handleRefresh();
    emit('refresh-files');

  } catch (error) {
    console.error('Failed to move item:', error);
  }
};

    const handleDragEnter = (event: DragEvent) => {
      event.preventDefault();
      scrollOnDrag(event);
      if (props.item.file === 'folder') {
        isDragOver.value = true;
        // Expand folder after hovering
        if (!isExpanded.value) {
          setTimeout(() => {
            if (isDragOver.value) {
              toggleExpand();
            }
          }, 800);
        }
      }
    };

    const handleDragLeave = () => {
      isDragOver.value = false;
    };

    const handleDragEnd = () => {
      isDragging.value = false;
      isDragOver.value = false;
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
      isActive,
      menuOpen,
      updateMenuOpenState,
      handleRightClick,
      menuActivator,
      refreshChildren,
      handleRefresh,
      handleDragStart,
      handleDragOver,
      handleDragEnter,
      handleDragLeave,
      handleDrop,
      handleDragEnd,
      isDragging,
      isDragOver,
      isDragTarget
    };
  }
});
</script>

<style scoped>
.file-tree-node {
  user-select: none;
  width: 100%;
}

.file-tree-node[draggable=true] {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

.node-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 25px;
  cursor: pointer;
  border-radius: 4px;
  padding-right: 4px;
  transition: all 0.2s ease;
  border: 1px solid transparent; /* Prepare for border transition */
}

.node-content {
  display: flex;
  align-items: center;
  overflow: hidden;
  flex-grow: 1;
  min-width: 0;
}

.folder-toggle-icon,
.file-icon {
  width: 20px;
  min-width: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.folder-toggle-icon {
  margin-right: 4px;
}

.file-icon {
  margin-right: 6px;
  color: #B0BEC5;
}

.file-name {
  font-family: 'Pathway Extreme', sans-serif;
  font-size: 12.5px;
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

/* Menu Open State */
.node-item.menu-open {
  background-color: rgba(98, 114, 164, 0.2);
  border-color:#FFFFFF;
}

.node-item.menu-open .file-name {
  color: #FFFFFF;
}

.node-item.menu-open .file-actions-menu {
  opacity: 1;
}

.node-item.dragging {
  opacity: 0.5;
}

.node-item.drag-over {
  background-color: rgba(98, 114, 164, 0.2);
  border: 1px dashed #FFFFFF;
}

.node-item.drag-target {
  background-color: rgba(98, 114, 164, 0.1);
}
</style>

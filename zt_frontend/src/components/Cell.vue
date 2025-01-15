<template>
  <v-card
    v-if="isDevMode || (!isDevMode && !hideCellValue)"
    :id="'codeCard' + cellId"
    :class="['cell', { 'cell--dev': isDevMode }]"
    color="bluegrey-darken-4"
    width="100%"
  >
    <v-divider
      class="indicator"
      vertical
      :color="dividerColor"
      :thickness="4"
    ></v-divider>
    <div class="content">
      <header class="header">
        <div class="click-edit" v-if="isDevMode && keepCodeInAppModel">
          <div class="click-edit__show-text" v-if="!editingCellName">
            <div class="loading-wrapper">
              <v-progress-circular
                v-if="cellId == currentlyExecutingCell && isCodeRunning"
                indeterminate
                size="24"
                class="ml-1 mr-2 green-loader"
              />
            </div>
            <h4
              class="text-bluegrey-darken-1 text-ellipsis click-edit__name"
              @click="toggleCellName"
            >
              {{ cellNameValue }}
            </h4>

            <!-- <v-btn
              v-if="isDevMode"
              color="bluegrey-darken-4"
              :icon="`ztIcon:${ztAliases.edit}`"
              size="x-small"
              class="text-bluegrey-darken-1"
              @click="toggleCellName"
            /> -->
          </div>

          <div class="click-edit__edit-field-wrapper" v-if="editingCellName">
            <v-text-field
              v-model="cellNameEditValue"
              :placeholder="cellType"
              density="compact"
              variant="plain"
              hide-details
              ref="cellNameField"
              class="click-edit__edit-field"
              @keydown.enter="saveCellName"
              @update:focused="
                (focused:any) => {
                  if (!focused) saveCellName();
                }
              "
            />
            <!-- <v-btn
              color="bluegrey-darken-4"
              :icon="`ztIcon:${ztAliases.save}`"
              size="x-small"
              @click="saveCellName"
            /> -->
            <!-- <v-btn
              color="bluegrey-darken-4"
              icon="$close"
              size="x-small"
              @click="toggleCellName"
            /> -->
          </div>
        </div>
        <h4
          v-else-if="isDevMode"
          class="text-bluegrey-darken-1 text-ellipsis click-edit__static-name"
        >
          {{ cellNameValue }}
        </h4>
        <slot v-else-if="keepCodeInAppModel" name="header-title"></slot>
        <v-spacer v-else></v-spacer>
        <v-defaults-provider
          :defaults="{
            VBtn: {
              variant: 'text',
              size: 'small',
            },
          }"
        >
          <div class="actions">
            <!-- <v-btn icon="$message"></v-btn> -->
            <v-btn
              v-if="isDevMode && showSaveBtn"
              :icon="`ztIcon:${ztAliases.save}`"
              @click="$emit('save')"
            ></v-btn>

            <v-btn
              v-if="isDevMode && showPlayBtn"
              :id="'runCode' + cellId"
              :icon="`ztIcon:${ztAliases.play}`"
              @click="$emit('play')"
            ></v-btn>
            <v-btn
              v-if="globalState.comments_enabled"
              :class="[
                'message-btn',
                'pa-0',
                {
                  'message-btn--alert': numberOfComments,
                },
              ]"
              @click="
                commentsStore.showCommentsPerCell({
                  cellId,
                  cellName: cellNameValue,
                  cellType,
                })
              "
              :ripple="false"
              slim
              rounded="circle"
            >
              <template #default>
                <v-icon
                  v-if="numberOfComments === 0"
                  size="x-large"
                  :icon="`ztIcon:${ztAliases.message}`"
                ></v-icon>
                <span v-else class="text-primary message-btn__counter">{{
                  numberOfComments
                }}</span>
              </template>
            </v-btn>
            <v-menu v-if="isDevMode" :close-on-content-click="false" v-model="isMenuOpen"
            >
              <template v-slot:activator="{ props }">
                <v-btn
                  :icon="`ztIcon:${ztAliases.more}`"
                  :id="'cellToolbar' + cellId"
                  v-bind="props"
                ></v-btn>
              </template>
              <v-list bg-color="bluegrey-darken-4">
                <v-list-item
                  v-if="keepCodeInAppModel"
                  :id="'updateCellReactivity' + cellId"
                >
                  <template v-slot:prepend>
                    <v-switch
                      v-model="nonReactiveValue"
                      @update:modelValue="updateReactivity"
                    ></v-switch>
                  </template>
                  <v-list-item-title>Non-Reactive</v-list-item-title>
                </v-list-item>
                <v-list-item :id="'hideCell' + cellId">
                  <template v-slot:prepend>
                    <v-switch
                      v-model="hideCellValue"
                      @update:modelValue="updateHideCell"
                      :id="'hideCellSwitch' + cellId"
                    ></v-switch>
                  </template>
                  <v-list-item-title>Hide Cell</v-list-item-title>
                </v-list-item>
                <v-list-item
                  v-if="keepCodeInAppModel"
                  :id="'expandCode' + cellId"
                >
                  <template v-slot:prepend>
                    <v-switch
                      v-model="hideCodeValue"
                      @update:modelValue="updateHideCode"
                    ></v-switch>
                  </template>
                  <v-list-item-title>Hide Code</v-list-item-title>
                </v-list-item>
                <v-list-item
                  v-if="keepCodeInAppModel"
                  :id="'expandCode' + cellId"
                >
                  <template v-slot:prepend>
                    <v-switch
                      v-model="expandCodeValue"
                      @update:modelValue="updateExpandCode"
                    ></v-switch>
                  </template>
                  <v-list-item-title>Expand Code</v-list-item-title>
                </v-list-item>
                <v-list-item
                  v-if="cellType === 'sql'"
                  :id="'updateShowTable' + cellId"
                >
                  <template v-slot:prepend>
                    <v-switch
                      v-model="showTableValue"
                      @update:modelValue="updateShowTable"
                    ></v-switch>
                  </template>
                  <v-list-item-title>Show Table</v-list-item-title>
                </v-list-item>
                <!-- <v-list-item>
                  <template v-slot:prepend>
                    <v-icon icon="$collapse"></v-icon>
                  </template>
                  <v-list-item-title>Move Up</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon icon="$expand"></v-icon>
                  </template>
                  <v-list-item-title>Move Down</v-list-item-title>
                </v-list-item>
                <v-list-item>
                  <template v-slot:prepend>
                    <v-icon :icon="`ztIcon:${ztAliases.duplicate}`"></v-icon>
                  </template>
                  <v-list-item-title>Duplicate</v-list-item-title>
                </v-list-item> -->
                <v-list-item
                  base-color="error"
                  :id="'deleteCell' + cellId"
                  class="delete-cell"
                  @click="$emit('delete')"
                >
                  <template v-slot:prepend>
                    <v-icon :icon="`ztIcon:${ztAliases.delete}`"></v-icon>
                  </template>
                  <v-list-item-title>Delete Cell</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </v-defaults-provider>
      </header>
      <div
        :class="['code', { 'code--dev': isDevMode }]"
        v-if="isDevMode || (!isDevMode && keepCodeInAppModel)"
      >
        <slot name="code"></slot>
      </div>
      <div
        :class="['outcome', { 'outcome--dev': isDevMode }]"
        v-if="!(isDevMode && !isAppRoute && cellType === 'text') && cellHasOutput"
      >
        <slot name="outcome"></slot>
      </div>
    </div>
    <v-tooltip v-if="nonReactiveValue" text="Cell is Stale">
      <template v-slot:activator="{ props }">
        <v-divider
          v-bind="props"
          class="indicator"
          vertical
          color="warning"
          :thickness="8"
        />
      </template>
    </v-tooltip>
  </v-card>
  <add-cell
    v-if="isDevMode"
    :cell-id="cellId"
    @createCodeCell="(e) => $emit('addCell', e)"
    
  />
</template>
<script setup lang="ts">
import axios from "axios";
import { computed, PropType, nextTick, ref, toRef } from "vue";
import type { Celltype } from "@/types/create_request";
import { ztAliases } from "@/iconsets/ztIcon";
import { useRoute } from "vue-router";
import type { VTextField } from "vuetify/lib/components/index.mjs";
import AddCell from "@/components/AddCell.vue";
import { HideCellRequest } from "@/types/hide_cell_request";
import { HideCodeRequest } from "@/types/hide_code_request";
import { ExpandCodeRequest } from "@/types/expand_code_request";
import { CellReactivityRequest } from "@/types/cell_reactivity_request";
import { ShowTableRequest } from "@/types/show_table_request";
import { NameCellRequest } from "@/types/name_cell_request";
import { useCellType } from "@/composables/cell-type";
import { globalState } from "@/global_vars";

import { useCommentsStore } from "@/stores/comments";

const commentsStore = useCommentsStore();
const { commentsByCell } = storeToRefs(commentsStore);

const numberOfComments = computed(() => commentsByCell.value(props.cellId!));

const props = defineProps({
  isDevMode: Boolean,
  cellType: {
    type: String as PropType<Celltype>,
    default: "code",
  },
  cellId: String,
  error: Boolean,
  hideCell: {
    type: Boolean,
    default: false,
  },
  hideCode: {
    type: Boolean,
    default: false,
  },
  expandCode: {
    type: Boolean,
    default: false,
  },
  nonReactive: {
    type: Boolean,
    default: false,
  },
  showTable: {
    type: Boolean,
    default: false,
  },
  cellName: {
    type: String,
    default: null,
  },

  currentlyExecutingCell: {
    type: String,
    default: null,
  },
  isCodeRunning: {
    type: Boolean,
    default: false,
  },
  cellHasOutput:{
    type: Boolean,
    default:false
  },
  isFocused: {
    type: Boolean,
    default: false,
  },
});
const emits = defineEmits<{
  (e: "delete"): void;
  (e: "play"): void;
  (e: "save"): void;
  (e: "expandCodeUpdate", expand: Boolean): void;
  (e: "updateReactivity", expand: Boolean): void;
  (e: "updateShowTable", expand: Boolean): void;
  (e: "hideCode", hideCode: Boolean): void;
  (e: "addCell", cellType: Celltype): void;
  (e: "renameCell", cellName: String): void;
}>();

const { cellTypeColor: dividerColor } = useCellType(
  toRef(props.cellType),
  toRef(props.error)
);

const hideCellValue = ref(props.hideCell || false);
const hideCodeValue = ref(props.hideCode || false);
const expandCodeValue = ref(props.expandCode || false);
const nonReactiveValue = ref(props.nonReactive || false);
const showTableValue = ref(props.showTable || false);
const cellNameValue = ref(props.cellName || props.cellType);
const cellNameEditValue = ref("");
const cellNameField = ref(null);
const editingCellName = ref(false);
const isMenuOpen = ref(false);

const showPlayBtn = computed(
  () => props.cellType === "code" || props.cellType === "sql"
);
const showSaveBtn = computed(
  () => props.cellType === "markdown" || props.cellType === "text"
);
const keepCodeInAppModel = computed(
  () => props.cellType === "code" || props.cellType === "sql"
);
const isAppRoute = computed(() => useRoute().name === "/app");

const updateHideCell = async (value: unknown) => {
  const hideCodeRequest: HideCellRequest = {
    cellId: props.cellId as string,
    hideCell: value as boolean,
  };
  await axios.post(
    import.meta.env.VITE_BACKEND_URL + "api/hide_cell",
    hideCodeRequest
  );
};
const updateHideCode = async (value: unknown) => {
  const hideCodeRequest: HideCodeRequest = {
    cellId: props.cellId as string,
    hideCode: value as boolean,
  };
  await axios.post(
    import.meta.env.VITE_BACKEND_URL + "api/hide_code",
    hideCodeRequest
  );
  emits("hideCode", value as boolean);
};
const updateExpandCode = async (value: unknown) => {
  const expandCodeRequest: ExpandCodeRequest = {
    cellId: props.cellId as string,
    expandCode: value as boolean,
  };
  await axios.post(
    import.meta.env.VITE_BACKEND_URL + "api/expand_code",
    expandCodeRequest
  );
  emits("expandCodeUpdate", value as boolean);
};
const updateReactivity = async (value: unknown) => {
  const cellReactivityRequest: CellReactivityRequest = {
    cellId: props.cellId as string,
    nonReactive: value as boolean,
  };
  await axios.post(
    import.meta.env.VITE_BACKEND_URL + "api/cell_reactivity",
    cellReactivityRequest
  );
  emits("updateReactivity", value as boolean);
};
const updateShowTable = async (value: unknown) => {
  const showTableRequest: ShowTableRequest = {
    cellId: props.cellId as string,
    showTable: value as boolean,
  };
  await axios.post(
    import.meta.env.VITE_BACKEND_URL + "api/show_table",
    showTableRequest
  );
  emits("updateShowTable", value as boolean);
};

const toggleCellName = () => {
  editingCellName.value = !editingCellName.value;
  if (editingCellName.value) {
    cellNameEditValue.value = cellNameValue.value as string;
    nextTick(() => {
      if (cellNameField.value) {
        (cellNameField.value as VTextField).focus();
      }
    });
  }
};

const saveCellName = async () => {
  const nameCellRequest: NameCellRequest = {
    cellId: props.cellId as string,
    cellName: cellNameEditValue.value as string,
  };
  await axios.post(
    import.meta.env.VITE_BACKEND_URL + "api/rename_cell",
    nameCellRequest
  );
  cellNameValue.value = cellNameEditValue.value;
  editingCellName.value = false;
  emits("renameCell", cellNameValue.value);
};
</script>

<style lang="scss" scoped>
.cell {
  padding: 5px;
  display: flex;
  margin-bottom: 2px;
  width: 100%;
  &--dev {
    margin-bottom: 6px;
  }
}
.message-btn {
  &--alert {
    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSIjQUU5RkU4Ij48cGF0aCBkPSJNMTMuMzA1IDIyLjVMMTIgMjEuNzVMMTUgMTYuNUgxOS41QzE5Ljg5NzggMTYuNSAyMC4yNzk0IDE2LjM0MiAyMC41NjA3IDE2LjA2MDdDMjAuODQyIDE1Ljc3OTQgMjEgMTUuMzk3OCAyMSAxNVY2QzIxIDUuNjAyMTggMjAuODQyIDUuMjIwNjQgMjAuNTYwNyA0LjkzOTM0QzIwLjI3OTQgNC42NTgwNCAxOS44OTc4IDQuNSAxOS41IDQuNUg0LjVDNC4xMDIxOCA0LjUgMy43MjA2NCA0LjY1ODA0IDMuNDM5MzQgNC45MzkzNEMzLjE1ODA0IDUuMjIwNjQgMyA1LjYwMjE4IDMgNlYxNUMzIDE1LjM5NzggMy4xNTgwNCAxNS43Nzk0IDMuNDM5MzQgMTYuMDYwN0MzLjcyMDY0IDE2LjM0MiA0LjEwMjE4IDE2LjUgNC41IDE2LjVIMTEuMjVWMThINC41QzMuNzA0MzUgMTggMi45NDEyOSAxNy42ODM5IDIuMzc4NjggMTcuMTIxM0MxLjgxNjA3IDE2LjU1ODcgMS41IDE1Ljc5NTYgMS41IDE1VjZDMS41IDUuMjA0MzUgMS44MTYwNyA0LjQ0MTI5IDIuMzc4NjggMy44Nzg2OEMyLjk0MTI5IDMuMzE2MDcgMy43MDQzNSAzIDQuNSAzSDE5LjVDMjAuMjk1NiAzIDIxLjA1ODcgMy4zMTYwNyAyMS42MjEzIDMuODc4NjhDMjIuMTgzOSA0LjQ0MTI5IDIyLjUgNS4yMDQzNSAyMi41IDZWMTVDMjIuNSAxNS43OTU2IDIyLjE4MzkgMTYuNTU4NyAyMS42MjEzIDE3LjEyMTNDMjEuMDU4NyAxNy42ODM5IDIwLjI5NTYgMTggMTkuNSAxOEgxNS44N0wxMy4zMDUgMjIuNVoiIGZpbGw9IiNBRTlGRTgiLz48L3N2Zz4=");
    background-position: center;
    background-repeat: no-repeat;
    transition: none;
  }
  &__counter {
    margin-bottom: 4px;
  }
}
.delete-cell:hover {
  background-color: #6e3d41;
}

.content {
  flex: 1;
  margin-left: 16px;
  margin-right: 0px;
  width: calc(100% - 36px);
}

.indicator {
  border-radius: 4px;
}

.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 2px;
  :deep(.v-btn) {
    color: rgba(var(--v-theme-bluegrey)) !important;
    .v-theme--light & {
      color: rgba(var(--v-theme-on-surface)) !important;
  }
  }
}

.code,
.outcome {
  padding: 0px;
  &--dev {
    border: 1px solid rgba(var(--v-theme-bluegrey));
    border-radius: 3px;
    padding: 6px;
  }
}

.code {
  margin-bottom: 10px;
}

.click-edit {
  width: calc(100% - 135px);
  &__name {
    cursor: text;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  &__show-text,
  &__edit-field-wrapper {
    height: 100%;
    display: flex;
    align-items: center;
  }
  &__name:hover {
    cursor: text;
    padding-left: 3px;
    padding-right: 3px;
    border: 1px solid #294455;
  }

  &__static-name {
    cursor: text;
    font-weight: normal;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &__edit-field {
    margin-top: -11px;
    & :deep(.v-field__input) {
      font-size: 1rem;
      letter-spacing: normal;
    }
  }
  .actions {
    display: flex;
    align-items: center;
  }

  .loading-wrapper {
    display: flex;
    align-items: center;
    margin-right: 8px;
  }

  .green-loader {
    color: rgba(var(--v-theme-success));
  }
}
</style>

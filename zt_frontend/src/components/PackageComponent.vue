<template>
  <v-dialog v-model="updatingDependencies" width="1024">
    <template v-slot:activator="{ props }">
      <v-btn
        color="bluegrey-darken-4"
        v-bind="props"
        icon
      >
      <v-icon :color="updatingDependencies ? 'primary' : 'white'">
        mdi-list-box-outline
        </v-icon>
    </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Add Dependencies</span>
      </v-card-title>
      <v-card-subtitle>
        Versions must adhere to
        <a
          href="https://pip.pypa.io/en/stable/reference/requirements-file-format/"
          target="_blank"
          >pip requirements file specification</a
        >. Examples: '==1.0.0' '!=1.5.0,>=1.4.1' etc.
      </v-card-subtitle>
      <v-list>
        <v-list-item v-for="dependency in dependencies.dependencies">
          <v-row>
            <v-col>
              <v-text-field
                v-model="dependency.package"
                label="Package (required)"
              ></v-text-field>
            </v-col>
            <v-col>
              <v-text-field
                v-model="dependency.version"
                label="Version"
              ></v-text-field>
            </v-col>
            <v-col cols="1">
              <v-btn icon color="primary">
                <v-icon
                  color="black"
                  @click="
                    dependencies.dependencies?.splice(
                      dependencies.dependencies.indexOf(dependency),
                      1
                    )
                  "
                  >mdi-delete</v-icon
                >
              </v-btn>
            </v-col>
          </v-row>
        </v-list-item>
        <v-list-item class="d-flex justify-center align-center">
          <v-btn
            icon="mdi-plus"
            variant="text"
            @click="
              dependencies.dependencies?.push({ package: '', version: '' })
            "
            text="Add Dependency"
            class="black--text"
          />
        </v-list-item>
        <v-list-item v-if="dependencyOutput.output">
          <codemirror
            v-model="dependencyOutput.output"
            :style="{ height: '400px' }"
            :indent-with-tab="true"
            :tab-size="2"
            :viewportMargin="Infinity"
            :extensions="extensions"
          />
        </v-list-item>
      </v-list>
      <v-card-actions>
        <v-btn
          v-if="!dependencyOutput.isLoading"
          color="primary"
          variant="flat"
          @click="updateDependencies"
          text="Install"
        />
        <div class="d-flex justify-center">
          <v-progress-circular
            v-if="dependencyOutput.isLoading"
            indeterminate
            color="primary"
          ></v-progress-circular>
        </div>
        <v-spacer />
        <v-btn
          color="error"
          variant="text"
          @click="updatingDependencies = false"
          text="Close"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import type { PropType } from "vue";
import { Codemirror } from "vue-codemirror";
import { markdown } from "@codemirror/lang-markdown";
import { oneDark } from "@codemirror/theme-one-dark";
import { EditorState } from "@codemirror/state";
import { Dependencies } from "@/types/notebook_response";
import { ztAliases } from "@/iconsets/ztIcon";
import { DependencyOutput } from "@/static-types/dependency_ouput";

export default {
  components: {
    codemirror: Codemirror,
  },
  data: () => ({
    updatingDependencies: false,
    ztAliases,
  }),
  emits: ["updateDependencies"],
  props: {
    dependencies: {
      type: Object as PropType<Dependencies>,
      required: true,
    },
    dependencyOutput: {
      type: Object as PropType<DependencyOutput>,
      required: true,
    },
  },
  computed: {
    extensions() {
      return [EditorState.readOnly.of(true), markdown(), oneDark];
    },
  },
  methods: {
    async updateDependencies() {
      this.dependencyOutput.isLoading = true;
      this.$emit("updateDependencies", this.dependencies);
    },
  },
};
</script>

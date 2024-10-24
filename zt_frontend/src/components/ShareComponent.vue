<template>
  <v-dialog v-model="dialog" max-width="600px" @afterEnter="loadValues()" @afterLeave="cleanUp()">
    <template v-slot:activator="{ props }">
      <v-btn
        v-bind="props"
        :prepend-icon="`ztIcon:${ztAliases.share}`"
        variant="flat"
        ripple
        color="primary"
        class="text-bluegrey-darken-4"
      >
        Publish
      </v-btn>
    </template>

    <v-card>
      <v-card-title>
        <span class="text-h5">Publish Notebook</span>
      </v-card-title>
      <v-alert v-if="successMessage" type="success" class="mb-4">
        {{ successMessage }}
      </v-alert>
      <v-alert v-if="errorMessage" type="error" class="mb-4">
        {{ errorMessage }}
      </v-alert>
      <v-alert v-if="warningMessage" type="warning" class="mb-4">
        {{ warningMessage }}
      </v-alert>
      <v-card-text>
        <v-form ref="form" v-model="valid" @submit.prevent="submitShareRequest">
          <v-text-field
            v-model="shareRequest.userName"
            label="User Name"
            :rules="[rules.required]"
            required
          ></v-text-field>
          <v-text-field
            v-model="shareRequest.projectName"
            label="Project Name"
            :rules="[rules.required]"
            required
          ></v-text-field>
          <v-text-field
            v-model="shareRequest.apiKey"
            label="API Key"
            :rules="[rules.required]"
            required
          ></v-text-field>
          <v-text-field
            v-model="shareRequest.teamName"
            label="Team Name (Optional)"
          ></v-text-field>
          <v-autocomplete
            v-model="shareRequest.computeProfile"
            :items="computeProfiles"
            label="Compute Profile"
          />
          <span
            >Need an API Key? Create an account
            <a href="https://www.zero-true.com/contact" target="_blank"
              >here</a
            ></span
          >
          <br /><br />
          <v-row justify="space-between">
            <v-col cols="auto">
              <v-btn v-if="!isLoading" type="submit" color="primary">{{
                confirmationRequired ? "Confirm" : "Publish"
              }}</v-btn>
              <div class="d-flex justify-center">
                <v-progress-circular
                  v-if="isLoading"
                  indeterminate
                  color="primary"
                ></v-progress-circular>
              </div>
            </v-col>
            <v-col cols="auto">
              <v-btn @click="dialog = false" color="error">Cancel</v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, Ref } from "vue";
import axios, { AxiosError } from "axios";
import { ztAliases } from "@/iconsets/ztIcon";
import { ShareRequest } from "@/types/share_request";

const props = defineProps({
  userName: {
    type: String,
    required: true,
  },
  projectName: {
    type: String,
    required: true,
  },
  teamName: {
    type: String,
    required: true,
  },
});

const dialog: Ref<boolean> = ref(false);
const shareRequest: Ref<ShareRequest> = ref({
  userName: "",
  projectName: "",
  apiKey: "",
  teamName: "",
  computeProfile: "X-Small (0.5 CPU, 2GB RAM)",
});
const valid: Ref<boolean> = ref(false);
const rules = {
  required: (value: string) => !!value || "Required.",
};

const computeProfiles = ref([
  "X-Small (0.5 CPU, 2GB RAM)",
  "Small (1 CPU, 4GB RAM)",
  "Medium (1.5 CPU, 8GB RAM)",
  "Large (2 CPU, 16GB RAM)",
  "X-Large (4 CPU, 32GB RAM)",
]);

const successMessage = ref("");
const errorMessage = ref("");
const warningMessage = ref("");
const confirmationRequired = ref(false);
const isLoading = ref(false);

const submitShareRequest = async () => {
  if (valid.value) {
    errorMessage.value = "";
    warningMessage.value = "";
    successMessage.value = "";
    isLoading.value = true;
    if (confirmationRequired.value) {
      try {
        await axios.post(
          import.meta.env.VITE_BACKEND_URL + "api/confirm_share", shareRequest.value
        );
        successMessage.value = "Project published successfully";
      } catch (error) {
        if (error instanceof AxiosError) {
          errorMessage.value =
            error.response?.data?.detail || "Error submitting share request";
        } else {
          errorMessage.value = "Error submitting share request";
        }
        console.error("Error submitting share request:", error);
      }
      confirmationRequired.value = false;
    } else {
      try {
        const response = await axios.post(
          import.meta.env.VITE_BACKEND_URL + "api/share_notebook",
          shareRequest.value
        );
        if (response.data?.warning) {
          warningMessage.value = response.data.warning;
          confirmationRequired.value = true;
        } else {
          successMessage.value = "Project published successfully";
          errorMessage.value = "";
          warningMessage.value = "";
        }
      } catch (error) {
        if (error instanceof AxiosError) {
          errorMessage.value =
            error.response?.data?.detail || "Error submitting share request";
        } else {
          errorMessage.value = "Error submitting share request";
        }
        console.error("Error submitting share request:", error);
      }
    }
    isLoading.value = false;
  }
};

function loadValues() {
  shareRequest.value.userName = props.userName;
  shareRequest.value.projectName = props.projectName;
  shareRequest.value.teamName = props.teamName;
}

function cleanUp() {
  errorMessage.value = "";
  successMessage.value = "";
  warningMessage.value = "";
  confirmationRequired.value = false;
  isLoading.value = false;
}
</script>

<template>
  <v-dialog v-model="dialog" max-width="600px">
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
      <v-alert v-if="errorMessage" type="error" class="mb-4">
        {{ errorMessage }}
      </v-alert>
      <v-card-text>
        <v-form ref="form" v-model="valid" @submit.prevent="submitShareRequest">
          <v-text-field
            label="User Name"
            v-model="shareRequest.userName"
            :rules="[rules.required]"
            required
          ></v-text-field>
          <v-text-field
            label="Project Name"
            v-model="shareRequest.projectName"
            :rules="[rules.required]"
            required
          ></v-text-field>
          <v-text-field
            label="API Key"
            v-model="shareRequest.apiKey"
            :rules="[rules.required]"
            required
          ></v-text-field>
          <v-text-field
            label="Team Name (Optional)"
            v-model="shareRequest.teamName"
          ></v-text-field>
          <span
            >Need an API Key? Create an account
            <a href="https://www.zero-true.com/contact" target="_blank"
              >here</a
            ></span
          >
          <br /><br />
          <v-row justify="space-between">
            <v-col cols="auto">
              <v-btn v-if="!isLoading" type="submit" color="primary"
                >Publish</v-btn
              >
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
import axios from "axios";
// If ztAliases is used within the template, ensure it's imported correctly. Otherwise, remove it if not needed.
import { ztAliases } from "@/iconsets/ztIcon";
import { ShareRequest } from "@/types/share_request";

const dialog: Ref<boolean> = ref(false);
const shareRequest: Ref<ShareRequest> = ref({
  userName: "",
  projectName: "",
  apiKey: "",
  teamName: "",
});
const valid: Ref<boolean> = ref(false);
const rules = {
  required: (value: string) => !!value || "Required.",
};

const errorMessage = ref("");
const isLoading = ref(false);

const submitShareRequest = async () => {
  if (valid.value) {
    isLoading.value = true;
    try {
      const response = await axios.post(
        import.meta.env.VITE_BACKEND_URL + "api/share_notebook",
        shareRequest.value
      );
      if (response.data.Error){
        errorMessage.value = response.data.Error;
        console.error("Error submitting share request:", response.data.Error);
      }
      else{
        errorMessage.value = "";
        dialog.value = false;
      }
    } catch (error) {
      errorMessage.value = "Error submitting share request";
      console.error("Error submitting share request:", error);
    }
    isLoading.value = false;
  }
};
</script>

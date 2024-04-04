<template>
    <v-dialog v-model="dialog" persistent max-width="600px">
      <template v-slot:activator="{ props }">
        <v-btn 
        v-bind="props"  
        :prepend-icon="`ztIcon:${ztAliases.share}`"
        variant="flat"
        ripple
        color="primary"
        class="text-bluegrey-darken-4">
        Publish
        </v-btn>
      </template>
  
      <v-card>
        <v-card-title>
          <span class="text-h5">Publish Notebook</span>
        </v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="valid" @submit.prevent="submitShareRequest">
            <v-text-field label="User Name" v-model="shareRequest.userName" :rules="[rules.required]" required></v-text-field>
            <v-text-field label="Project Name" v-model="shareRequest.projectName" :rules="[rules.required]" required></v-text-field>
            <v-text-field label="API Key" v-model="shareRequest.apiKey" :rules="[rules.required]" required></v-text-field>
            <span>Need an API Key? Create an account <a href='https://www.zero-true.com/contact' target="_blank">here</a></span>
            <br/><br/>
            <v-row justify="space-between">
              <v-col cols="auto">
                <v-btn type="submit" color="primary">Share</v-btn>
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
  


  <script lang="ts">
  import { defineComponent, ref, Ref } from 'vue';
  import axios from 'axios';
  // If ztAliases is used within the template, ensure it's imported correctly. Otherwise, remove it if not needed.
  import { ztAliases } from '@/iconsets/ztIcon';
  import  { ShareRequest } from '@/types/share_request';

  export default defineComponent({
    name: 'ShareNotebookDialog',
    setup() {
      const dialog: Ref<boolean> = ref(false);
      const shareRequest: Ref<ShareRequest> = ref({
        userName: '',
        projectName: '',
        apiKey: '',
      });
      const valid: Ref<boolean> = ref(false);
      const rules = {
        required: (value: string) => !!value || 'Required.',
      };
  
      const submitShareRequest = async () => {
        if (valid.value) {
          try {
            await axios.post(import.meta.env.VITE_BACKEND_URL + 'api/share_notebook', shareRequest.value);
            console.log('Share request submitted successfully');
            dialog.value = false;
          } catch (error) {
            console.error('Error submitting share request:', error);
          }
        }
      };
  
      return {
        dialog,
        shareRequest,
        valid,
        rules,
        submitShareRequest,
        ztAliases,
      };
    },
  });
  </script>
  
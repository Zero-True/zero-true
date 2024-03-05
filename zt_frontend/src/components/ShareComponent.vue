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
        Share
        </v-btn>
      </template>
  
      <v-card>
        <v-card-title>
          <span class="text-h5">Share Notebook</span>
        </v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="valid" @submit.prevent="submitShareRequest">
            <v-text-field label="User Name" v-model="shareRequest.userName" :rules="[rules.required]" required></v-text-field>
            <v-text-field label="Project Name" v-model="shareRequest.projectName" :rules="[rules.required]" required></v-text-field>
            <v-text-field label="API Key" v-model="shareRequest.apiKey" :rules="[rules.required]" required></v-text-field>
            <v-btn type="submit" color="primary">Share</v-btn>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="dialog = false">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  


<script>
import { defineComponent, ref } from 'vue';
import { ztAliases } from '@/iconsets/ztIcon';
import axios from 'axios';


export default defineComponent({
  name: 'ShareNotebookDialog',
  setup() {
    const dialog = ref(false);
    const shareRequest = ref({
      userName: '',
      projectName: '',
      apiKey: ''
    });
    const valid = ref(false);
    const rules = {
      required: value => !!value || 'Required.'
    };

    const submitShareRequest = async () => {
      if (valid.value) {
        try {
          // Replace with your actual API endpoint and method to send data
          await axios.post(import.meta.env.VITE_BACKEND_URL +'api/share_notebook', shareRequest.value);
          // Handle success response
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
      ztAliases
    };
  }
});
</script>

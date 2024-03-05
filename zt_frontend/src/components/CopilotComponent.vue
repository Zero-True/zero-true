<template>
  <v-dialog v-model="dialog" persistent max-width="400px">
    <template v-slot:activator="{ props }">
      <v-btn v-bind="props" icon>
        <v-icon :icon="`ztIcon:${ztAliases.copilot}`"></v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h4">GitHub Copilot </span>
      </v-card-title>
      <v-card-text>
        <v-btn
          v-if="!serverStarted"
          color="primary"
          @click="startServerAndCheckStatus"
          >Start Server
        </v-btn>
        <div v-else-if="serverStarted && !isSignedIn">
          <div v-if="signInData && signInData.verificationUri && signInData.userCode">
            <p>Please go to the following URL and enter the code to sign in:</p>
            <p>
              <strong>URL:</strong>
              <a :href="signInData.verificationUri" target="_blank">{{signInData.verificationUri}}</a>
            </p>
            <p><strong>Code:</strong> {{ signInData.userCode }}</p>
            <v-btn color="primary" @click="confirmSignIn">I Signed In</v-btn>
            <!-- Button for user to confirm sign-in -->
          </div>
          <div v-else-if="signInData && signInData.status">
            <p>Status: {{ signInData.status }}</p>
            <p>User: {{ signInData.user }}</p>
          </div>
          <div v-else>
            <v-btn color="primary" @click="signInInitiate">Sign In</v-btn>
          </div>
        </div>
        <v-btn v-else-if="isSignedIn" color="primary" @click="signOut">Sign Out</v-btn>
      </v-card-text>
      <v-btn
        class="ma-2"
        icon="mdi:mdi-close"
        variant="plain"
        position="absolute"
        location="top right"
        @click="dialog = false"
      />
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { defineComponent, ref } from "vue";
import { globalState } from "@/global_vars";
import { ztAliases } from "@/iconsets/ztIcon";
import axios from "axios";

export default defineComponent({
  name: "SignInDialogComponent",

  setup() {
    const dialog = ref(false);
    const serverStarted = ref(false);
    const isSignedIn = ref(false);
    const signInData = ref<any>(null);

    const startNodeServer = async () => {
      try {
        const response = await axios.post(
          import.meta.env.VITE_BACKEND_URL + "copilot/start_node_server",
          {}
        );
        console.log("Node server started successfully", response);
      } catch (error) {
        console.error("Error during starting the Node server:", error);
      }
    };
    const checkInitialStatus = async () => {
      try {
        const response = await axios.post(
          import.meta.env.VITE_BACKEND_URL + "copilot/check_status",
          {}
        );
        handleSignInResponse(response.data);
      } catch (error) {
        console.error("Error during initial status check:", error);
      }
    };

    const signInInitiate = async () => {
      try {
        const response = await axios.post(
          import.meta.env.VITE_BACKEND_URL + "copilot/sign_in_initiate",
          {}
        );
        handleSignInResponse(response.data);
      } catch (error) {
        console.error("Error during sign in initiation:", error);
      }
    };

    const confirmSignIn = async () => {
      try {
        const response = await axios.post(
          import.meta.env.VITE_BACKEND_URL + "copilot/sign_in_confirm",
          { userCode: signInData.value.userCode }
        );
        handleSignInResponse(response.data);
      } catch (error) {
        console.error("Error during sign in confirmation:", error);
      }
    };

    const signOut = async () => {
      try {
        await axios.post(
          import.meta.env.VITE_BACKEND_URL + "copilot/sign_out",
          {}
        );
        isSignedIn.value = false;
        signInData.value = null;
        globalState.copilot_active = false;
      } catch (error) {
        console.error("Error during sign out:", error);
      }
    };

    const handleSignInResponse = (data: any) => {
      signInData.value = data;
      if (data.status === "OK" || data.status === "AlreadySignedIn") {
        isSignedIn.value = true;
        globalState.copilot_active = true;
      } else if (data.status === "NotSignedIn") {
        isSignedIn.value = false;
      }
    };
    const startServerAndCheckStatus = async () => {
      try {
        await startNodeServer();
        setTimeout(async () => {
          await checkInitialStatus();
        }, 2500);
        serverStarted.value = true;
      } catch (error) {
        console.error(
          "Error during starting the server or checking status:",
          error
        );
      }
    };

    return {
      dialog,
      isSignedIn,
      serverStarted,
      signInData,
      signInInitiate,
      confirmSignIn,
      signOut,
      startServerAndCheckStatus,
      ztAliases
    };
  },
});
</script>

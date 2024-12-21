<template>
  <v-dialog v-model="dialog" max-width="400px">
    <!-- Activator Button -->
    <template v-slot:activator="{ props }">
      <v-btn
        color="bluegrey-darken-4"
        v-bind="props"
        icon
      >
        <v-icon 
          :icon="`ztIcon:${ztAliases.copilot}`" 
          :color="dialog ? 'primary' : 'white'"
        >
        </v-icon>
      </v-btn>
    </template>

    <!-- Main Card -->
    <v-card class="bg-dark rounded-lg">
      <!-- Loading Overlay -->
      <v-overlay
        :model-value="isLoading"
        class="align-center justify-center"
        persistent
      >
        <v-progress-circular
          indeterminate
          color="primary"
        ></v-progress-circular>
      </v-overlay>

      <!-- Close Button -->
      <v-card-title class="d-flex align-center justify-end pa-3">
        <v-btn
          icon="mdi-close"
          variant="plain"
          @click="dialog = false"
        />
      </v-card-title>

      <v-card-text class="px-6 pb-6 pt-0">
        <!-- Initial State - Hidden Server Start -->
        <div v-if="!serverStarted && !isLoading" class="d-flex flex-column align-center text-center pt-2">
          <v-icon
            :icon="`ztIcon:${ztAliases.copilot}`"
            color="white"
            class="mb-4 dialog-icon"
          ></v-icon>

          <h3 class="text-h5 mb-3 font-weight-bold text-white">
            GitHub Copilot
          </h3>

          <p class="text-body-2 mb-6 text-gray-400">
            Active GitHub Copilot subscription required
          </p>

          <v-btn
            color="primary"
            size="large"
            width="100%"
            @click="handleInitialStart"
            :loading="isLoading"
            class="rounded-lg text-capitalize font-weight-bold"
          >
            Get Started
          </v-btn>
        </div>

        <!-- Unauthorized State -->
        <div v-else-if="isUnauthorized" class="d-flex flex-column align-center text-center pt-2">
          <v-icon
            :icon="`ztIcon:${ztAliases.copilot}`"
            color="error"
            class="mb-4 dialog-icon"
          ></v-icon>
          
          <h3 class="text-h5 mb-3 font-weight-bold text-white">
            Unauthorized Access
          </h3>
          
          <p class="text-body-2 mb-4 text-gray-400">
            {{ signInData?.user ? `${signInData.user}, you don't have an active GitHub Copilot subscription.` : 'You don\'t have an active GitHub Copilot subscription.' }}
          </p>
          
          <p class="text-body-2 mb-6 text-gray-400">
            Please visit GitHub to manage your subscription.
          </p>

          <v-btn
            color="primary"
            size="large"
            width="100%"
            href="https://github.com/settings/copilot"
            target="_blank"
            class="rounded-lg text-capitalize font-weight-bold"
          >
            Manage Subscription
          </v-btn>
          
          <v-btn
            color="error"
            variant="text"
            class="mt-4"
            @click="signOut"
          >
            Sign Out
          </v-btn>
        </div>

        <!-- Sign In State -->
        <div v-else-if="serverStarted && !isSignedIn" class="text-center">
          <div v-if="signInData?.verificationUri && signInData?.userCode">
            <v-icon
              :icon="`ztIcon:${ztAliases.copilot}`"
              color="white"
              class="mb-4 dialog-icon"
            ></v-icon>

            <div class="text-h6 mb-4 text-white font-weight-bold">
              Complete Your Sign In
            </div>
            <v-alert
              color="info"
              variant="tonal"
              density="compact"
              class="rounded-lg"
            >
              <p class="text-body-2 mb-2 text-gray-300">
                Visit this URL to sign in:
              </p>
              <a
                :href="signInData.verificationUri"
                target="_blank"
                class="verification-link text-decoration-none text-primary"
              >
                {{ signInData.verificationUri }}
              </a>
              <v-divider class="my-3"></v-divider> 
              <div class="d-flex align-center justify-space-between">
                <div>
                  <div class="text-caption text-gray-400">Your code:</div>
                  <div class="verification-code text-h6 text-white">
                    {{ signInData.userCode }}
                  </div>
                </div>
                <v-btn
                  color="primary"
                  class="rounded-lg text-capitalize font-weight-bold" 
                  @click="confirmSignIn"
                  :loading="isLoading"
                >
                  I've Signed In
                </v-btn>
              </div>
            </v-alert>
          </div>
        </div>

        <!-- Signed In State -->
        <div v-else-if="isSignedIn" class="d-flex flex-column align-center text-center pt-2">
          <v-icon
            :icon="`ztIcon:${ztAliases.copilot}`"
            color="white"
            class="mb-4 dialog-icon"
          ></v-icon>
          
          <div class="text-h6 mb-2 text-white font-weight-bold">
            GitHub Copilot
          </div>
          <div class="text-body-2 mb-4 text-gray-400">
            Signed in as <span class="text-white">{{ signInData?.user }}</span>
          </div>
          <v-btn
            color="primary"
            size="large"
            width="100%"
            @click="signOut"
            :loading="isLoading"
            class="rounded-lg text-capitalize font-weight-bold"
          >
            Sign Out
          </v-btn>
        </div>
      </v-card-text>

      <!-- Error Snackbar -->
      <v-snackbar
        v-model="showError"
        color="error"
        timeout="3000"
        location="top"
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
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ztAliases } from '@/iconsets/ztIcon';
import { globalState } from '@/global_vars';
import axios from 'axios';

// State
const dialog = ref(false);
const serverStarted = ref(false);
const isSignedIn = ref(false);
const isLoading = ref(false);
const showError = ref(false);
const errorMessage = ref('');
const isUnauthorized = ref(false);
const signInData = ref<{
  verificationUri?: string;
  userCode?: string;
  status?: string;
  user?: string;
} | null>(null);

// API wrapper
const api = {
  async call(endpoint: string, data = {}) {
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}copilot/${endpoint}`,
        data
      );
      return { success: true, data: response.data };
    } catch (error) {
      console.error(`Error in ${endpoint}:`, error);
      return { success: false, error };
    }
  }
};

// Error handler
const handleError = (message: string) => {
  errorMessage.value = message;
  showError.value = true;
  isLoading.value = false;
};

// Response handler
const handleSignInResponse = (data: any) => {
  signInData.value = data;
  if (data.status === "OK" || data.status === "AlreadySignedIn") {
    isSignedIn.value = true;
    isUnauthorized.value = false;
    globalState.copilot_active = true;
  } else if (data.status === "NotSignedIn") {
    isSignedIn.value = false;
    isUnauthorized.value = false;
  } else if (data.status === "NotAuthorized") {
    isSignedIn.value = false;
    isUnauthorized.value = true;
    globalState.copilot_active = false;
  }
};

// Combined initial start
const handleInitialStart = async () => {
  isLoading.value = true;
  
  // Start server
  const serverResult = await api.call('start_node_server');
  if (!serverResult.success) {
    handleError('Failed to initialize Copilot server');
    return;
  }

  // Wait for server startup
  await new Promise(resolve => setTimeout(resolve, 2500));
  
  // Check status
  const statusResult = await api.call('check_status');
  if (!statusResult.success) {
    handleError('Failed to check Copilot status');
    return;
  }

  serverStarted.value = true;
  handleSignInResponse(statusResult.data);
  
  // If not already signed in and not unauthorized, initiate sign in
  if (!isSignedIn.value && !isUnauthorized.value) {
    await signInInitiate();
  }
  
  isLoading.value = false;
};

// Sign in initiation
const signInInitiate = async () => {
  isLoading.value = true;
  const result = await api.call('sign_in_initiate');
  
  if (result.success) {
    handleSignInResponse(result.data);
  } else {
    handleError('Failed to initiate sign in');
  }
  
  isLoading.value = false;
};

// Confirm sign in
const confirmSignIn = async () => {
  if (!signInData.value?.userCode) return;
  
  isLoading.value = true;
  const result = await api.call('sign_in_confirm', {
    userCode: signInData.value.userCode
  });
  
  if (result.success) {
    handleSignInResponse(result.data);
  } else {
    handleError('Failed to confirm sign in');
  }
  
  isLoading.value = false;
};

// Sign out
const signOut = async () => {
  isLoading.value = true;
  const result = await api.call('sign_out');
  
  if (result.success) {
    isSignedIn.value = false;
    isUnauthorized.value = false;
    serverStarted.value = false;
    signInData.value = null;
    globalState.copilot_active = false;
  } else {
    handleError('Failed to sign out');
  }
  
  isLoading.value = false;
};
</script>

<style scoped>
.verification-link {
  word-break: break-all;
  font-size: 0.875rem;
}

.verification-code {
  letter-spacing: 2px;
  font-weight: bold;
}

.dialog-icon {
  transform: scale(1.5);
  display: block;
  margin-left: auto;
  margin-right: auto;
}
</style>
// Composables
import { createRouter, createWebHistory } from 'vue-router/auto'
import axios from 'axios'

const getBaseUrl = async () => {
  const response = await axios.get(import.meta.env.VITE_BACKEND_URL + "base_path");
  return response.data
}

const router = getBaseUrl().then((url) => createRouter({
  history: createWebHistory(url),
}))

export default router
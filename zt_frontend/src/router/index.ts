// Composables
import { createRouter, createWebHistory } from 'vue-router/auto'
import axios from 'axios'

const getBaseUrl = async () => {
  const response = await axios.get(import.meta.env.VITE_BACKEND_URL + "base_path");
  console.log(response.data)
  return response.data
}

const router = createRouter({
  history: createWebHistory(await getBaseUrl()),
})

export default router
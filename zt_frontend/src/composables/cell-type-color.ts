import { Ref, computed } from 'vue'
import type { Celltype } from '@/types/create_request'

export function useCellTypeColor(type: Ref<Celltype>, error?: Ref<Boolean>) {
  const cellTypeColor = computed(() => {
    if (error?.value) return 'error' 
    switch (type.value) {
      case 'markdown':
        return '#4CBCFC';
      case 'code':
        return '#AE9FE8'
      case 'sql':
        return '#FFDCA7';
      case 'text':
        return '#16B48E';
    }
  })

  return { cellTypeColor }
}

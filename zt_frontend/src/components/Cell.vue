<template>
	<v-card
		class="cell"
		color="bluegrey-darken-4"
	>
		<v-divider 
			class="indicator"	
			vertical
			:color="dividerColor"
			:thickness="4"
		></v-divider>
		<div
			class="content"	
		>
			<header class="header">
				<h4 class="text-bluegrey-darken-1">{{cellType}} #1</h4>
				<v-defaults-provider
					:defaults="{
						'VIcon':{
							'color':'bluegrey',
						},
						'VBtn': {
							variant: 'text',
							size: 'small'
						}
					}"
				>	
					<div class="actions">
						<!-- <v-btn icon="$message"></v-btn> -->
						<v-btn
							v-if="showSaveBtn"	
							icon="$save"
							@click="$emit('save')"
						></v-btn>
						<v-btn
							v-if="showPlayBtn"	
							icon="$play"
							@click="$emit('play')"
						></v-btn>
						<v-btn
							icon="$delete"
							@click="$emit('delete')"
						></v-btn>
						<v-btn icon="$more"></v-btn>
					</div>
				</v-defaults-provider>
			</header>
			<div class="code">
				<slot name="code"></slot>
			</div>
			<div class="outcome">
				<slot name="outcome"></slot>
			</div>
		</div>
	</v-card>
	<v-menu v-if="isDevMode" transition="scale-transition">
    <template v-slot:activator="{ props }">
      <add-cell v-bind="props" />
    </template>
    <v-list>
      <v-list-item v-for="(item, i) in addCellItems" :key="i">
        <v-btn block>{{ item.title }} </v-btn>
      </v-list-item>
    </v-list>
  </v-menu>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import type { PropType } from 'vue'
import AddCell from '@/components/AddCell.vue'

type CellType = 'markdown' | 'code' | 'sql' | 'editor'

const props = defineProps({
  isDevMode: Boolean,
	cellType: String as PropType<CellType> 
})
defineEmits<{
	(e: 'delete'): void
	(e: 'play'): void
	(e: 'save'): void
}>()

const dividerColor = computed(() => {
	switch(props.cellType) {
		case 'markdown':
			return '#4CBCFC';
		case 'code':
			return '#AE9FE8'	
		case 'sql':
			return '#FFDCA7';
		case 'editor':
			return '#16B48E';
	}
})

const showPlayBtn = computed(() => props.cellType === 'code') 
const showSaveBtn = computed(() => props.cellType === 'markdown' || props.cellType === 'editor') 

const addCellItems = ref([
	{ title: 'Code' },
	{ title: 'SQL' },
	{ title: 'Markdown' },
	{ title: 'Text' },
])
</script>

<style lang="scss" scoped>
.cell {
	padding: 24px;
	display: flex;
	margin-bottom: 16px;
}
.content {
	flex: 1;
	margin-left: 16px;
}

.indicator {
	border-radius: 4px;
}

.header {
	display: flex;
	justify-content: space-between;
	margin-bottom: 16px;
}

.code,
.outcome {
	border: 1px solid rgba(var(--v-theme-bluegrey));
	border-radius: 4px;
	padding: 12px;
}

.code {
	margin-bottom: 16px;
}
</style>

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
							:icon="`ztIcon:${ztAliases.save}`"
							@click="$emit('save')"
						></v-btn>
						
						<v-btn
							v-if="showPlayBtn"	
							:icon="`ztIcon:${ztAliases.play}`"
							@click="$emit('play')"
						></v-btn>
						<v-menu
							:close-on-content-click="false"
						>
							<template v-slot:activator="{ props }">
								<v-btn
									:icon="`ztIcon:${ztAliases.visibility}`"
									v-bind="props"
								></v-btn>
							</template>
							
							<v-list>
								<v-list-item>
									<template v-slot:prepend>
										<v-switch
										></v-switch>
									</template>
									<v-list-item-title>Hide Cell</v-list-item-title>
								</v-list-item>
								<v-list-item>
									<template v-slot:prepend>
										<v-switch
										></v-switch>
									</template>
									<v-list-item-title>Hide Code</v-list-item-title>
								</v-list-item>
							</v-list>	
							
						</v-menu>
						<v-menu>
							<template v-slot:activator="{ props }">
								<v-btn :icon="`ztIcon:${ztAliases.more}`" v-bind="props"></v-btn>
							</template>
							<v-list>
								<v-list-item>
									<template v-slot:prepend>
          					<v-icon icon="$collapse"></v-icon>
        					</template>
									<v-list-item-title>Move Up</v-list-item-title>
								</v-list-item>
								<v-list-item>
									<template v-slot:prepend>
          					<v-icon icon="$expand"></v-icon>
        					</template>
									<v-list-item-title>Move Down</v-list-item-title>
								</v-list-item>
								<v-list-item>
									<template v-slot:prepend>
          					<v-icon :icon="`ztIcon:${ztAliases.duplicate}`"></v-icon>
        					</template>
									<v-list-item-title>Duplicate</v-list-item-title>
								</v-list-item>
								<v-list-item base-color="error" @click="$emit('delete')">
									<template v-slot:prepend>
          					<v-icon :icon="`ztIcon:${ztAliases.delete}`"></v-icon>
        					</template>
									<v-list-item-title>Delete Cell</v-list-item-title>
								</v-list-item>
							</v-list>
						</v-menu>
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
	<add-cell 
		v-if="isDevMode" 
		@createCodeCell="e => $emit('addCell', e)" 
	/>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import type { PropType } from 'vue'
import type { Celltype } from '@/types/create_request'
import AddCell from '@/components/AddCell.vue'
import { ztAliases } from '@/iconsets/ztIcon'

const props = defineProps({
  isDevMode: Boolean,
	cellType: String as PropType<Celltype> 
})
defineEmits<{
	(e: 'delete'): void
	(e: 'play'): void
	(e: 'save'): void
	(e: 'addCell', cellType: Celltype): void
}>()

const dividerColor = computed(() => {
	switch(props.cellType) {
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

const showPlayBtn = computed(() => props.cellType === 'code' || props.cellType === 'sql') 
const showSaveBtn = computed(() => props.cellType === 'markdown' || props.cellType === 'text') 
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
	width: calc(100% - 20px);
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

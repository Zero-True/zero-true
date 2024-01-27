<template>
	<v-card
		class="cell"
		color="bluegrey-darken-4"
	>
		<v-divider 
			class="indicator"	
			vertical
			color="#4CBCFC"
			:thickness="4"
		></v-divider>
		<div
			class="content"	
		>
			<header class="header">
				<h4 class="text-bluegrey-darken-1">Markdown #1</h4>
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
						<v-btn
							icon="$message"	
						></v-btn>
						<v-btn
							icon="$save"	
						></v-btn>
						<v-btn
							icon="$more"	
						></v-btn>
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
import { ref } from 'vue'
import AddCell from '@/components/AddCell.vue'
defineProps({
  isDevMode: Boolean
})
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

<template>
	
		<v-card
			class="cell"
			color="bluegrey-darken-4"
		>
			<v-divider 
				class="cell__indicator"	
				vertical
				color="#4CBCFC"
				:thickness="4"
			></v-divider>
			<div
				class="cell__content"	
			>
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
					<h4 class="text-bluegrey-darken-1">Markdown #1</h4>
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
					
			</div>
		</v-card>
</template>
<script setup lang="ts"></script>
<style lang="scss" scoped>
.cell {
	padding: 24px;
	display: flex;
	&__content {
		flex: 1;
		margin-left: 16px;
		display: flex;
		justify-content: space-between;
	}
	&__indicator {
		border-radius: 4px;
	}
}
</style>

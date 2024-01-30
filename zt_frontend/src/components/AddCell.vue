<template>
	<div class="divider">
		<v-divider
			class="divider__divider-line"
			color="bluegrey-darken-2"	
		></v-divider>
		<v-btn
			:prepend-icon="`ztIcon:${ztAliases.message}`"
			variant="text"
			density="compact"
			:ripple="false"
			@click="onClick"
			class="divider__btn bg-background"
		>Add cell</v-btn>
	</div>
</template>
<script setup lang="ts">
import { ztAliases } from '@/iconsets/ztIcon'
defineProps({
  onClick: null
})
</script>
<style lang="scss" scoped>
.divider {
	position: relative;
	height: 24px;
	&__divider-line {
		position: absolute;
		top: 50%;
    width: 100%;
    transform: translateY(-50%);
	}	
	&__btn {
		position: absolute;
		top: 0;
		left: 50%;
		transform: translateX(-50%);
	}
}	
</style>
import { h } from 'vue'
import type { IconSet, IconAliases, IconProps } from 'vuetify'

const aliases: IconAliases = {
	complete: '',
	cancel: '',
	close: '',
	delete: '',
	clear: '',
	success: '',
	info: '',
	warning: '',
	error: '',
	prev: '',
	next: '',
	checkboxOn: '',
	checkboxOff: '',
	checkboxIndeterminate: '',
	delimiter: '',
	sortAsc: '',
	sortDesc: '',
	expand: '',
	menu: '',
	subgroup: '',
	dropdown: '',
	radioOn: '',
	radioOff: '',
	edit: '',
	ratingEmpty: '',
	ratingFull: '',
	ratingHalf: '',
	loading: '',
	first: '',
	last: '',
	unfold: '',
	file: '',
	plus: '',
	minus: '',
	calendar: '',
  notebook: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M14.25 7.5H19.5V9H14.25V7.5ZM14.25 11.25H19.5V12.75H14.25V11.25ZM14.25 15H19.5V16.5H14.25V15Z" fill="currentColor"/><path d="M21 3.75H3C2.6023 3.7504 2.221 3.90856 1.93978 4.18978C1.65856 4.471 1.5004 4.8523 1.5 5.25V18.75C1.5004 19.1477 1.65856 19.529 1.93978 19.8102C2.221 20.0914 2.6023 20.2496 3 20.25H21C21.3976 20.2494 21.7788 20.0912 22.06 19.81C22.3412 19.5288 22.4994 19.1476 22.5 18.75V5.25C22.4996 4.8523 22.3414 4.471 22.0602 4.18978C21.779 3.90856 21.3977 3.7504 21 3.75ZM3 5.25H11.25V18.75H3V5.25ZM12.75 18.75V5.25H21L21.0015 18.75H12.75Z" fill="currentColor"/></svg>',
	logo: '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32" fill="none"><path d="M21.3432 32H10.6716L5.33867 24H5.33676L0 15.9943L5.33676 7.9914L10.664 0L10.6735 0.0143266V15.9914L16.0065 23.9943L21.3337 31.9857L21.3432 32Z" fill="#AE9FE8"/><path d="M26.6724 8L21.3376 0H10.6641L21.3357 16.0086V31.9857V32L26.6629 24.0086L31.9996 16.0057L26.6724 8Z" fill="#AE9FE8"/></svg>',
	monitor: '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M19.5 1.5H22.5V4.5H19.5V1.5ZM19.5 6H22.5V9H19.5V6ZM15 1.5H18V4.5H15V1.5ZM15 6H18V9H15V6Z" fill="currentColor"/><path d="M21 12V16.5H3V4.5H12V3H3C2.60218 3 2.22064 3.15804 1.93934 3.43934C1.65804 3.72064 1.5 4.10218 1.5 4.5V16.5C1.5 16.8978 1.65804 17.2794 1.93934 17.5607C2.22064 17.842 2.60218 18 3 18H9V21H6V22.5H18V21H15V18H21C21.3978 18 21.7794 17.842 22.0607 17.5607C22.342 17.2794 22.5 16.8978 22.5 16.5V12H21ZM13.5 21H10.5V18H13.5V21Z" fill="currentColor"/></svg>',
}

const ztIconSet: IconSet = {
  component: (props: IconProps) => h(props.tag, { innerHTML:  props.icon as string}),
}

export { aliases, ztIconSet }

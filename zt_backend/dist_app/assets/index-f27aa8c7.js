import{C as o,_ as r,r as l,o as c,c as a}from"./index-68abea86.js";const u={metaInfo(){return{meta:{dev:!0}}},props:{notebook:{type:Object,required:!0},completions:{type:Object,required:!0},runCode:{type:Function,required:!0},saveCell:{type:Function,required:!0},componentValueChange:{type:Function,required:!0},deleteCell:{type:Function,required:!0},createCodeCell:{type:Function,required:!0}},components:{CodeCellManager:o},methods:{getComponent(t){switch(t){case"code":return"CodeComponent";case"text":return"EditorComponent";case"markdown":return"MarkdownComponent";case"sql":return"SQLComponent";default:throw new Error(`Unknown component type: ${t}`)}}}};function d(t,C,e,m,s,i){const n=l("code-cell-manager");return c(),a(n,{notebook:e.notebook,completions:e.completions,runCode:e.runCode,saveCell:e.saveCell,componentValueChange:e.componentValueChange,deleteCell:e.deleteCell,createCell:e.createCodeCell},null,8,["notebook","completions","runCode","saveCell","componentValueChange","deleteCell","createCell"])}const _=r(u,[["render",d]]);export{_ as default};
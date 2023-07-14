<template>
  <div ref="containerRef" class="console" v-html="html"></div>
</template>

<script setup lang="ts">
import { watch } from 'vue';
import AnsiUp from 'ansi_up';

const props = defineProps<{
  log: string;
}>();
const ansi = new AnsiUp();
const containerRef = ref<HTMLElement | null>(null);

function scrollToBottom() {
  if (containerRef.value) {
    containerRef.value.scrollTop = containerRef.value.scrollHeight;
  }
}

const html = computed(() => {
  return ansi.ansi_to_html(props.log).replace(/\n/gm, '<br>');
});

watch(html, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    nextTick(() => scrollToBottom());
  }
});
</script>

<style scoped>
.console {
  font-family: 'Roboto Mono', monospace;
  text-align: left;
  /*background-color: black;*/
  /*color: #fff;*/
  overflow: auto;
  white-space: pre-wrap;
  height: 50vh;
}
</style>

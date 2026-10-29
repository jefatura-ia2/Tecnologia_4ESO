<template>
  <div class="codeblock">
    <button class="copy btn sm secondary" @click="copy">{{ copied ? 'Copiado ✓' : 'Copiar' }}</button>
    <pre class="code"><code class="hljs" v-html="html"></code></pre>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { highlight } from '../lib/markdown.js'

const props = defineProps({ code: { type: String, default: '' }, lang: { type: String, default: 'python' } })
const copied = ref(false)
const html = computed(() => highlight((props.code || '').replace(/\n$/, ''), props.lang))

async function copy() {
  try {
    await navigator.clipboard.writeText(props.code || '')
    copied.value = true
    setTimeout(() => (copied.value = false), 1500)
  } catch { /* portapapeles no disponible */ }
}
</script>

<style scoped>
.codeblock { position: relative; }
.copy { position: absolute; top: 8px; right: 8px; opacity: .85; }
pre { margin: 0; padding-top: 40px; }
@media (min-width: 700px) { pre { padding-top: 14px; } }
</style>

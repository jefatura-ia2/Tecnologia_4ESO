<template>
  <div class="editor">
    <div class="gutter" aria-hidden="true" :style="{ transform: `translateY(${-scrollTop}px)` }">
      <div v-for="n in lines" :key="n">{{ n }}</div>
    </div>
    <textarea
      ref="ta"
      :value="modelValue"
      spellcheck="false"
      autocapitalize="off"
      autocomplete="off"
      :rows="Math.max(8, lines + 1)"
      aria-label="Editor de código Python"
      @input="$emit('update:modelValue', $event.target.value)"
      @keydown="onKey"
      @scroll="scrollTop = $event.target.scrollTop"
      @paste="$emit('paste', $event)"
    ></textarea>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'

const props = defineProps({ modelValue: { type: String, default: '' } })
const emit = defineEmits(['update:modelValue', 'paste'])
const ta = ref(null)
const scrollTop = ref(0)
const lines = computed(() => props.modelValue.split('\n').length)

function insert(text, selStart, selEnd) {
  const el = ta.value
  const v = el.value
  const next = v.slice(0, selStart) + text + v.slice(selEnd)
  emit('update:modelValue', next)
  nextTick(() => {
    el.selectionStart = el.selectionEnd = selStart + text.length
  })
}

function onKey(e) {
  const el = ta.value
  if (e.key === 'Tab') {
    e.preventDefault()
    insert('    ', el.selectionStart, el.selectionEnd)
  } else if (e.key === 'Enter') {
    // mantiene la sangría y añade un nivel tras ':'
    const start = el.selectionStart
    const lineStart = el.value.lastIndexOf('\n', start - 1) + 1
    const line = el.value.slice(lineStart, start)
    let indent = line.match(/^\s*/)[0]
    if (line.trimEnd().endsWith(':')) indent += '    '
    e.preventDefault()
    insert('\n' + indent, start, el.selectionEnd)
  }
}
</script>

<style scoped>
.editor { position: relative; display: flex; background: var(--code-bg); border-radius: 10px; overflow: hidden; border: 1px solid var(--border); }
.gutter { flex: none; width: 40px; padding: 12px 6px 12px 0; text-align: right; color: #5b6878; font-family: var(--mono); font-size: .88rem; line-height: 1.5; user-select: none; }
textarea {
  flex: 1; border: none; border-radius: 0; background: transparent; color: var(--code-text);
  font-family: var(--mono); font-size: .88rem; line-height: 1.5; padding: 12px; resize: vertical;
  white-space: pre; overflow-x: auto; tab-size: 4; min-height: 180px;
}
textarea:focus { outline: none; }
.editor:focus-within { outline: 2px solid var(--primary); }
</style>

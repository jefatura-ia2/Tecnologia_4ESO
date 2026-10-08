<template>
  <div class="item card" :class="stateClass">
    <div class="row top">
      <span class="badge">{{ typeLabel }}</span>
      <span class="small muted">{{ item.points }} {{ item.points === 1 ? 'punto' : 'puntos' }}</span>
      <span class="spacer"></span>
      <span v-if="fb" class="badge" :class="fb.correct ? 'ok' : (fb.earned > 0 ? 'warn' : 'bad')">
        {{ fb.earned }} / {{ fb.points }}
      </span>
    </div>

    <!-- QUIZ -->
    <template v-if="item.type === 'quiz'">
      <div class="q prose" v-html="mdInline(item.question)"></div>
      <div class="options" role="radiogroup">
        <label v-for="o in item.options" :key="o.id" class="opt" :class="{ sel: modelValue === o.id }">
          <input type="radio" :name="uid" :value="o.id" :checked="modelValue === o.id"
                 @change="$emit('update:modelValue', o.id)" />
          <span v-html="mdInline(o.text)"></span>
        </label>
      </div>
      <div v-if="fb" class="alert" :class="fb.correct ? 'ok' : 'bad'">{{ fb.message }}</div>
    </template>

    <!-- FILL BLANK -->
    <template v-else-if="item.type === 'fill_blank'">
      <div class="q prose" v-html="mdInline(item.question)"></div>
      <pre class="fill"><template v-for="(part, i) in parts" :key="i"><span>{{ part }}</span><input
            v-if="i < parts.length - 1"
            class="blank"
            :class="blankClass(i)"
            :value="blanks[i] || ''"
            :size="Math.max(4, (blanks[i] || '').length + 1)"
            :aria-label="`Hueco ${i + 1}`"
            spellcheck="false" autocapitalize="off" autocomplete="off"
            @input="setBlank(i, $event.target.value)" /></template></pre>
      <template v-if="fb">
        <div v-for="(b, i) in fb.blanks" :key="i" v-show="!b.ok" class="alert bad small">Hueco {{ i + 1 }}: {{ b.message }}</div>
        <div v-if="fb.correct" class="alert ok">{{ fb.message }}</div>
      </template>
    </template>

    <!-- CODE -->
    <template v-else>
      <div class="q prose" v-html="md(item.prompt)"></div>
      <CodeEditor :model-value="modelValue ?? item.starter ?? ''" @update:model-value="$emit('update:modelValue', $event)"
                  @paste="$emit('paste')" />
      <div class="row small muted mt">
        <span>Pruebas automáticas:</span>
        <span v-for="(t, i) in item.tests" :key="i" class="badge"
              :class="fb?.tests?.[i] ? (fb.tests[i].passed ? 'ok' : 'bad') : ''">{{ t }}</span>
        <span class="spacer"></span>
        <button class="btn ghost sm" type="button" @click="reset">Restaurar plantilla</button>
      </div>
      <template v-if="fb">
        <div v-for="(m, i) in fb.messages" :key="'m' + i" class="alert" :class="fb.correct && i === 0 ? 'ok' : (m.startsWith('⚠️') || m.startsWith('💡') ? 'warn' : 'bad')">{{ m }}</div>
        <div v-for="(t, i) in fb.tests.filter((x) => !x.passed && x.message)" :key="'t' + i" class="alert bad small">
          <strong>{{ t.desc }}</strong> — {{ t.message }}
        </div>
        <details v-if="fb.stdout" class="small"><summary>Salida de print()</summary><pre class="code">{{ fb.stdout }}</pre></details>
      </template>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CodeEditor from './CodeEditor.vue'
import { md, mdInline } from '../lib/markdown.js'

const props = defineProps({
  item: { type: Object, required: true },
  modelValue: { default: undefined },
  feedback: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'paste'])
const uid = 'q-' + Math.random().toString(36).slice(2)
const fb = computed(() => props.feedback)
const typeLabel = computed(() => ({ quiz: 'Test', fill_blank: 'Completa', code: 'Código' })[props.item.type])
const stateClass = computed(() => (fb.value ? (fb.value.correct ? 'is-ok' : 'is-bad') : ''))

const parts = computed(() => (props.item.text || '').replace(/\n$/, '').split('___'))
const blanks = computed(() => (Array.isArray(props.modelValue) ? props.modelValue : []))
function setBlank(i, v) {
  const arr = [...blanks.value]
  while (arr.length < parts.value.length - 1) arr.push('')
  arr[i] = v
  emit('update:modelValue', arr)
}
function blankClass(i) {
  const b = fb.value?.blanks?.[i]
  return b ? (b.ok ? 'ok' : 'bad') : ''
}
function reset() {
  emit('update:modelValue', props.item.starter || '')
}
</script>

<style scoped>
.item { padding: 16px 18px; }
.item.is-ok { border-left: 4px solid var(--ok); }
.item.is-bad { border-left: 4px solid var(--bad); }
.top { margin-bottom: 6px; }
.q { font-weight: 600; margin: 6px 0 10px; }
.options { display: grid; gap: 6px; }
.opt { display: flex; gap: 10px; align-items: flex-start; font-weight: 400; margin: 0; padding: 9px 12px; border: 1px solid var(--border); border-radius: 9px; cursor: pointer; }
.opt input { width: auto; margin-top: 4px; }
.opt.sel { border-color: var(--primary); background: var(--primary-soft); }
.fill { font-family: var(--mono); background: var(--surface-2); padding: 12px 14px; border-radius: 10px; white-space: pre-wrap; line-height: 2.1; overflow-x: auto; margin: 0; }
.blank { display: inline-block; width: auto; font-family: var(--mono); padding: 2px 6px; margin: 0 2px; border: 2px dashed var(--primary); background: var(--surface); font-size: .92rem; }
.blank.ok { border: 2px solid var(--ok); }
.blank.bad { border: 2px solid var(--bad); }
</style>

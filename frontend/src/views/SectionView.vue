<template>
  <div v-if="error && !data" class="alert bad">{{ error }} <router-link to="/">Volver a las misiones</router-link></div>
  <div v-else-if="data">
    <div class="crumbs small muted">
      <router-link to="/">Misiones</router-link> ›
      {{ data.mission.icon }} Misión {{ data.mission.number }}: {{ data.mission.title }}
    </div>
    <div class="row head">
      <h1>{{ sec.kind === 'challenge' ? '🏆 ' : '' }}{{ sec.title }}</h1>
      <div class="spacer"></div>
      <span v-if="data.state.passed" class="badge ok">Superada · mejor nota {{ pct(data.state.best_score) }}</span>
      <span v-else-if="data.state.attempts" class="badge warn">{{ data.state.attempts }} intento(s) · mejor {{ pct(data.state.best_score) }}</span>
      <span class="badge">{{ sec.hours }} h de clase</span>
    </div>

    <div class="tabs" role="tablist">
      <button v-for="t in tabs" :key="t.id" role="tab" :aria-selected="tab === t.id" :class="{ active: tab === t.id }" @click="tab = t.id">
        {{ t.label }}
      </button>
    </div>

    <section v-show="tab === 'teoria'" class="card prose" v-html="md(sec.theory)"></section>

    <section v-show="tab === 'ejemplos'" class="grid">
      <div class="row">
        <span class="small muted">Ver código para:</span>
        <button class="btn sm" :class="board === 'pico_w' ? '' : 'secondary'" @click="board = 'pico_w'">🟩 Pico W</button>
        <button class="btn sm" :class="board === 'esp32_s3' ? '' : 'secondary'" @click="board = 'esp32_s3'">⬛ ESP32-S3</button>
      </div>
      <article v-for="ex in sec.examples" :key="ex.title" class="card">
        <h3 style="margin-top:0">{{ ex.title }}</h3>
        <p class="muted prose" v-html="mdInline(ex.explanation)"></p>
        <CodeBlock :code="ex[board]" />
      </article>
    </section>

    <section v-show="tab === 'practica'" class="card prose" v-html="md(sec.practice)"></section>

    <section v-show="tab === 'evaluacion'">
      <div class="alert info">{{ sec.evaluation.intro || 'Responde a todas las preguntas.' }}
        Los ejercicios de código se ejecutan en un simulador de MicroPython (machine, time, network, neopixel, bluetooth…).
        <span v-if="hasBrowserCode && pyStatus.state === 'loading'" class="small"><br />⏳ Preparando Python en tu navegador (solo tarda la primera vez)…</span></div>
      <form class="grid" @submit.prevent="submit">
        <EvalItem v-for="item in sec.evaluation.items" :key="item.id" :item="item"
                  v-model="answers[item.id]" :feedback="itemFeedback(item.id)" />
        <div v-if="error" class="alert warn">{{ error }}</div>
        <div v-if="result" class="card result" :class="result.passed ? 'pass' : 'fail'">
          <div class="score">{{ pct(result.score) }}</div>
          <div>
            <strong>{{ result.message }}</strong>
            <div class="small muted">{{ result.earned }} de {{ result.total }} puntos{{ result.preview ? ' · Vista previa del profesor (no se guarda)' : '' }}</div>
          </div>
          <div class="spacer"></div>
          <router-link v-if="result.passed && data.nav.next" :to="`/seccion/${data.nav.next}`" class="btn">Siguiente sección →</router-link>
          <router-link v-else-if="result.passed" to="/" class="btn">{{ result.mission_completed ? '🎉 ¡Misión completada! Ver misiones' : 'Volver a las misiones' }}</router-link>
        </div>
        <div class="row">
          <button class="btn" :disabled="busy">{{ busyLabel || 'Entregar y corregir' }}</button>
          <span class="small muted">Puedes reintentarlo; se guarda tu mejor nota. Tras varios fallos seguidos tendrás que esperar un poco.</span>
        </div>
      </form>
    </section>

    <div class="row mt nav">
      <router-link v-if="data.nav.prev" :to="`/seccion/${data.nav.prev}`" class="btn secondary">← Anterior</router-link>
      <div class="spacer"></div>
      <button v-if="tab !== 'evaluacion'" class="btn secondary" @click="nextTab">{{ nextTabLabel }} →</button>
    </div>
  </div>
  <div v-else class="muted">Cargando…</div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import CodeBlock from '../components/CodeBlock.vue'
import EvalItem from '../components/EvalItem.vue'
import { api, session } from '../lib/api.js'
import { md, mdInline } from '../lib/markdown.js'
import { preloadPython, pyStatus, runPython } from '../lib/pyrunner.js'

const props = defineProps({ id: { type: String, required: true } })
const data = ref(null)
const error = ref('')
const busy = ref(false)
const busyLabel = ref('')
const result = ref(null)
const tab = ref('teoria')
const board = ref(session.user?.board || 'pico_w')
const answers = reactive({})

const tabs = [
  { id: 'teoria', label: '📖 Teoría' },
  { id: 'ejemplos', label: '💻 Ejemplos' },
  { id: 'practica', label: '🔧 Práctica' },
  { id: 'evaluacion', label: '✅ Evaluación' },
]
const sec = computed(() => data.value?.section)
// Con Netlify, el código se ejecuta en el navegador (las secciones traen code_tests);
// con el servidor Python del centro, lo corrige el servidor.
const hasBrowserCode = computed(() => !!sec.value?.evaluation.items.some((i) => i.type === 'code' && i.code_tests))
watch(tab, (t) => { if (t === 'evaluacion' && hasBrowserCode.value) preloadPython() })
const nextTabLabel = computed(() => {
  const i = tabs.findIndex((t) => t.id === tab.value)
  return tabs[i + 1]?.label.slice(3) || ''
})
const pct = (x) => Math.round((x || 0) * 100) + '%'
const draftKey = () => `neumalab-draft-${session.user?.username}-${props.id}`

function nextTab() {
  const i = tabs.findIndex((t) => t.id === tab.value)
  tab.value = tabs[Math.min(i + 1, tabs.length - 1)].id
  window.scrollTo({ top: 0 })
}

function itemFeedback(id) {
  return result.value?.items?.find((i) => i.id === id) || null
}

async function load() {
  data.value = null
  error.value = ''
  result.value = null
  tab.value = 'teoria'
  Object.keys(answers).forEach((k) => delete answers[k])
  try {
    const d = await api(`/sections/${props.id}`)
    data.value = d
    let draft = null
    try { draft = JSON.parse(localStorage.getItem(draftKey()) || 'null') } catch { /* sin borrador */ }
    Object.assign(answers, d.last_submission?.answers || {}, draft || {})
    if (d.last_submission) result.value = d.last_submission.feedback
  } catch (e) {
    error.value = e.message
  }
}

watch(answers, () => {
  try { localStorage.setItem(draftKey(), JSON.stringify(answers)) } catch { /* sin almacenamiento */ }
}, { deep: true })

async function runCodeItems() {
  const results = {}
  for (const item of sec.value.evaluation.items) {
    if (item.type !== 'code' || !item.code_tests) continue
    const code = answers[item.id]
    if (typeof code !== 'string' || !code.trim() || code.trim() === (item.starter || '').trim()) continue
    busyLabel.value = pyStatus.state === 'ready' ? 'Ejecutando tu código…' : 'Preparando Python…'
    results[item.id] = await runPython({ code, tests: item.code_tests.tests, setup: item.code_tests.setup })
  }
  return results
}

async function submit() {
  busy.value = true
  busyLabel.value = 'Corrigiendo…'
  error.value = ''
  try {
    const code_results = hasBrowserCode.value ? await runCodeItems() : undefined
    busyLabel.value = 'Corrigiendo…'
    const r = await api(`/sections/${props.id}/submit`, { method: 'POST', body: { answers: { ...answers }, code_results } })
    result.value = r
    if (!r.preview) {
      data.value.state.attempts = r.attempts
      data.value.state.best_score = Math.max(data.value.state.best_score, r.score)
      if (r.passed) data.value.state.passed = true
    }
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
    busyLabel.value = ''
  }
}

watch(() => props.id, load, { immediate: true })
</script>

<style scoped>
.crumbs a { color: var(--muted); }
.head h1 { margin: 6px 0 14px; }
.result { display: flex; gap: 16px; align-items: center; flex-wrap: wrap; }
.result.pass { border: 2px solid var(--ok); background: var(--ok-soft); }
.result.fail { border: 2px solid var(--warn); background: var(--warn-soft); }
.score { font-size: 2rem; font-weight: 800; }
.nav { margin-top: 24px; }
</style>

<template>
  <div>
    <div class="row mb">
      <div>
        <h1 style="margin:0">Tus misiones</h1>
        <p class="muted" style="margin:4px 0 0">Curso completo · 3 trimestres · 3 h por semana. Supera cada sección para desbloquear la siguiente.</p>
      </div>
      <div class="spacer"></div>
      <div v-if="missions.length" class="overall card">
        <div class="small muted">Progreso total</div>
        <div class="big">{{ overall }}%</div>
        <div class="progress"><span :style="{ width: overall + '%' }"></span></div>
      </div>
    </div>

    <router-link to="/recursos" class="card recursos-aviso">🧩 <strong>Material complementario:</strong> taller PicoLab·IA para diseñar tu propia PCB con IA. Puedes usarlo cuando quieras, en paralelo a las misiones. →</router-link>

    <div v-if="error" class="alert bad">{{ error }}</div>
    <div v-if="loading" class="muted">Cargando…</div>

    <div class="path">
      <template v-for="(m, i) in missions" :key="m.id">
      <h2 v-if="m.trimestre && m.trimestre !== missions[i - 1]?.trimestre" class="trim">{{ m.trimestre }}.º trimestre</h2>
      <article class="mission card"
               :class="{ locked: !m.state.unlocked, done: m.state.completed }">
        <div class="head row">
          <div class="icon">{{ m.state.unlocked ? m.icon : '🔒' }}</div>
          <div class="title">
            <div class="small muted">Misión {{ m.number }} · Semanas {{ m.weeks[0] }}–{{ m.weeks[m.weeks.length - 1] }} · {{ m.hours }} h
              <span v-if="m.extra" class="badge accent">Ampliación</span></div>
            <h2>{{ m.title }}</h2>
            <div class="muted small">{{ m.subtitle }}</div>
          </div>
          <div class="spacer"></div>
          <span v-if="m.state.completed" class="badge ok">Completada ✓</span>
          <span v-else-if="m.state.unlocked" class="badge warn">{{ m.state.passed_sections }}/{{ m.state.total_sections }} secciones</span>
          <span v-else class="badge">Bloqueada</span>
        </div>
        <div class="progress mt"><span :style="{ width: (m.state.passed_sections / m.state.total_sections * 100) + '%' }"></span></div>

        <details class="mt">
          <summary class="small">Objetivos y material</summary>
          <ul class="small"><li v-for="o in m.objectives" :key="o">{{ o }}</li></ul>
          <div class="small muted"><strong>Material:</strong> {{ m.materials.join(' · ') }}</div>
        </details>

        <ol class="sections">
          <li v-for="s in m.sections" :key="s.id">
            <router-link v-if="s.state.unlocked" :to="`/seccion/${s.id}`" class="sec">
              <span class="status">{{ s.state.passed ? '✅' : (s.kind === 'challenge' ? '🏆' : '▶️') }}</span>
              <span class="stitle">{{ s.title }}</span>
              <span class="spacer"></span>
              <span v-if="s.foto" class="foto-st" :title="fotoTitulo(s.state)">{{ fotoIcono(s.state) }}</span>
              <span v-if="s.state.attempts" class="small muted">{{ Math.round(s.state.best_score * 100) }}%</span>
              <span class="small muted">{{ s.hours }} h</span>
            </router-link>
            <div v-else class="sec disabled">
              <span class="status">🔒</span><span class="stitle">{{ s.title }}</span>
              <span class="spacer"></span><span class="small muted">{{ s.hours }} h</span>
            </div>
          </li>
        </ol>
        <div class="small muted">Nota mínima para superar cada sección: <strong>{{ Math.round(m.passing_score * 100) }}%</strong></div>
      </article>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../lib/api.js'

const missions = ref([])
const loading = ref(true)
const error = ref('')

const fotoIcono = (st) => (!st.photo ? '📷' : { pendiente: '📷⏳', aceptada: '📷✅', rechazada: '📷❌' }[st.photo.status])
const fotoTitulo = (st) => (!st.photo ? 'Pide foto del montaje' : { pendiente: 'Foto subida, pendiente de revisión', aceptada: 'Foto aceptada', rechazada: 'Foto rechazada: vuelve a subirla' }[st.photo.status])

const overall = computed(() => {
  const total = missions.value.reduce((a, m) => a + m.state.total_sections, 0)
  const done = missions.value.reduce((a, m) => a + m.state.passed_sections, 0)
  return total ? Math.round((done / total) * 100) : 0
})

onMounted(async () => {
  try {
    missions.value = await api('/missions')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.foto-st { font-size: .85rem; opacity: .85; }
.recursos-aviso { display: block; margin-bottom: 16px; padding: 12px 16px; text-decoration: none; color: inherit; border-left: 4px solid #0f766e; }
.recursos-aviso:hover { background: #f0fdfa; }
.overall { padding: 10px 16px; min-width: 170px; }
.big { font-size: 1.6rem; font-weight: 800; }
.path { display: grid; gap: 16px; }
.mission { position: relative; }
.mission.locked { opacity: .62; }
.trim { margin: 18px 0 0; font-size: 1.05rem; color: var(--accent); text-transform: uppercase; letter-spacing: .04em; }
.badge.accent { background: var(--accent-soft); color: var(--accent); }
.mission.done { border-color: color-mix(in srgb, var(--ok) 45%, var(--border)); }
.head { align-items: flex-start; flex-wrap: nowrap; }
.icon { font-size: 2rem; width: 52px; height: 52px; display: grid; place-items: center; background: var(--surface-2); border-radius: 12px; flex: none; }
.title h2 { margin: 2px 0; }
.sections { list-style: none; padding: 0; margin: 14px 0 10px; display: grid; gap: 6px; }
.sec { display: flex; gap: 10px; align-items: center; padding: 9px 12px; border: 1px solid var(--border); border-radius: 9px; color: var(--text); text-decoration: none; background: var(--surface); }
a.sec:hover { border-color: var(--primary); background: var(--primary-soft); }
.sec.disabled { color: var(--muted); background: var(--surface-2); }
.stitle { font-weight: 600; }
summary { cursor: pointer; color: var(--primary); font-weight: 600; }
@media (max-width: 640px) {
  .head { flex-wrap: wrap; }
  .overall { width: 100%; }
}
</style>

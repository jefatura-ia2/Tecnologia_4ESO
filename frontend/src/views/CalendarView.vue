<template>
  <div>
    <h1>Calendario del curso</h1>
    <p class="muted">{{ cal?.regular_weeks || 33 }} semanas · {{ cal?.hours_per_week || 3 }} sesiones de 1 h por semana · inicio el {{ fmt(cal?.start) }} · las vacaciones se saltan con la variable SKIP_WEEKS</p>
    <div v-if="error" class="alert bad">{{ error }}</div>
    <div class="weeks">
      <article v-for="w in cal?.weeks || []" :key="w.week" class="card week" :class="{ now: isCurrent(w) }">
        <div class="row">
          <strong>Semana {{ w.week }}</strong>
          <span class="spacer"></span>
          <span v-if="isCurrent(w)" class="badge ok">Esta semana</span>
          <span v-if="w.extra" class="badge warn">Ampliación</span>
          <span class="small muted">{{ fmt(w.start) }} – {{ fmt(w.end) }}</span>
        </div>
        <ol>
          <li v-for="s in w.sessions" :key="s.session">
            <span class="ico">{{ s.icon }}</span>
            <router-link v-if="s.section_id" :to="`/seccion/${s.section_id}`">{{ s.title }}</router-link>
            <span v-else>{{ s.title }}</span>
          </li>
        </ol>
      </article>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../lib/api.js'

const cal = ref(null)
const error = ref('')
const fmt = (iso) => (iso ? new Date(iso + 'T12:00:00').toLocaleDateString('es-ES', { day: 'numeric', month: 'short' }) : '')
function isCurrent(w) {
  const today = new Date().toISOString().slice(0, 10)
  return today >= w.start && today <= w.end
}
onMounted(async () => {
  try { cal.value = await api('/calendar') } catch (e) { error.value = e.message }
})
</script>

<style scoped>
.weeks { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 14px; }
.week { padding: 14px 16px; }
.week.now { border: 2px solid var(--primary); }
ol { margin: 10px 0 0; padding-left: 22px; }
li { margin: 4px 0; font-size: .93rem; }
.ico { margin-right: 4px; }
</style>

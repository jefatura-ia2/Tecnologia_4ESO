<template>
  <div v-if="d">
    <div class="small muted"><router-link to="/profesor">Panel</router-link> › Alumno/a</div>
    <div class="row">
      <h1>{{ d.student.full_name }}</h1>
      <span class="badge">{{ d.student.username }}</span>
      <span class="badge">{{ d.student.group_name || 'sin grupo' }}</span>
      <span class="badge" :class="d.student.board === 'pico_w' ? 'pico' : 'esp'">{{ d.student.board === 'pico_w' ? 'Pico W' : 'ESP32-S3' }}</span>
    </div>
    <div v-if="msg" class="alert ok">{{ msg }}</div>
    <div v-if="error" class="alert bad">{{ error }}</div>

    <div class="grid">
      <article v-for="m in d.missions" :key="m.id" class="card">
        <div class="row">
          <h3 style="margin:0">{{ m.icon }} M{{ m.number }} · {{ m.title }}</h3>
          <span class="spacer"></span>
          <span v-if="m.completed" class="badge ok">Completada</span>
          <span v-else-if="m.unlocked" class="badge warn">{{ m.passed_sections }}/{{ m.total_sections }}</span>
          <button v-else class="btn sm secondary" @click="unlock(m.id)">🔓 Desbloquear</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Sección</th><th>Estado</th><th>Mejor</th><th>Intentos</th><th></th></tr></thead>
            <tbody>
              <tr v-for="s in m.sections" :key="s.id">
                <td>{{ s.title }}</td>
                <td>
                  <span v-if="s.passed" class="badge ok">Superada</span>
                  <span v-else-if="s.attempts" class="badge warn">En curso</span>
                  <span v-else-if="s.unlocked" class="badge">Disponible</span>
                  <span v-else class="badge">Bloqueada</span>
                </td>
                <td>{{ s.attempts ? Math.round(s.best_score * 100) + '%' : '—' }}</td>
                <td>{{ s.attempts }}<span v-if="s.failed_streak" class="small muted"> ({{ s.failed_streak }} fallos seguidos)</span></td>
                <td><button v-if="s.failed_streak" class="btn sm ghost" @click="resetAttempts(s.id)">Quitar espera</button></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="row grade">
          <label class="small" style="margin:0">Nota del profesor (0-10)</label>
          <input v-model.number="grades[m.id].grade" type="number" min="0" max="10" step="0.1" style="width:90px" />
          <input v-model="grades[m.id].notes" placeholder="Observaciones (proyecto, actitud, práctica…)" style="flex:1;min-width:200px" />
          <button class="btn sm" @click="saveGrade(m.id)">Guardar</button>
        </div>
      </article>
    </div>

    <h2>Historial de entregas</h2>
    <div v-if="!d.submissions.length" class="muted">Sin entregas todavía.</div>
    <details v-for="s in d.submissions" :key="s.id" class="card sub">
      <summary class="row">
        <span class="badge">{{ s.section_id }}</span>
        <span class="badge" :class="s.passed ? 'ok' : 'bad'">{{ Math.round(s.score * 100) }}%</span>
        <span v-if="s.flagged" class="badge bad">⚠️ alerta</span>
        <span class="small muted">{{ parseDate(s.created_at).toLocaleString('es-ES') }} · {{ s.elapsed_seconds }} s desde que abrió la sección</span>
      </summary>
      <pre v-if="s.flag_reason" class="reason">{{ s.flag_reason }}</pre>
      <div v-for="it in s.feedback.items || []" :key="it.id" class="ans">
        <div class="row"><strong>{{ it.id }}</strong><span class="badge" :class="it.correct ? 'ok' : 'bad'">{{ it.earned }}/{{ it.points }}</span></div>
        <CodeBlock v-if="it.type === 'code' && s.answers[it.id]" :code="s.answers[it.id]" />
        <div v-else class="small">Respuesta: <code>{{ JSON.stringify(s.answers[it.id] ?? '—') }}</code></div>
      </div>
    </details>

    <div class="card mt danger-zone">
      <h3 style="margin-top:0">Cuenta</h3>
      <div class="row">
        <input v-model="newPass" type="text" placeholder="Nueva contraseña (mín. 6)" style="max-width:260px" />
        <button class="btn secondary" :disabled="newPass.length < 6" @click="setPass">Cambiar contraseña</button>
        <span class="spacer"></span>
        <button v-if="!confirmDel" class="btn danger" @click="confirmDel = true">Eliminar alumno/a</button>
        <template v-else>
          <span class="small">¿Seguro? Se borrarán todas sus entregas.</span>
          <button class="btn danger" @click="del">Sí, eliminar</button>
          <button class="btn secondary" @click="confirmDel = false">Cancelar</button>
        </template>
      </div>
    </div>
  </div>
  <div v-else-if="error" class="alert bad">{{ error }}</div>
  <div v-else class="muted">Cargando…</div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import CodeBlock from '../components/CodeBlock.vue'
import { api, parseDate } from '../lib/api.js'

const props = defineProps({ id: { type: String, required: true } })
const router = useRouter()
const d = ref(null)
const error = ref('')
const msg = ref('')
const grades = reactive({})
const newPass = ref('')
const confirmDel = ref(false)

async function load() {
  try {
    d.value = await api(`/teacher/students/${props.id}`)
    for (const m of d.value.missions) grades[m.id] = { grade: m.grade, notes: m.notes }
  } catch (e) { error.value = e.message }
}
function flash(t) { msg.value = t; setTimeout(() => (msg.value = ''), 2500) }

async function unlock(mid) {
  await api(`/teacher/students/${props.id}/unlock`, { method: 'POST', body: { mission_id: mid } })
  flash('Misión desbloqueada'); load()
}
async function resetAttempts(sid) {
  await api(`/teacher/students/${props.id}/reset-attempts`, { method: 'POST', body: { section_id: sid } })
  flash('Espera eliminada: puede reintentar ya'); load()
}
async function saveGrade(mid) {
  error.value = ''
  try {
    const g = grades[mid]
    await api(`/teacher/students/${props.id}/grade`, { method: 'PUT',
      body: { mission_id: mid, grade: g.grade === '' || g.grade === null ? null : Number(g.grade), notes: g.notes || '' } })
    flash('Nota guardada')
  } catch (e) { error.value = e.message }
}
async function setPass() {
  await api(`/teacher/students/${props.id}/password`, { method: 'POST', body: { password: newPass.value } })
  newPass.value = ''; flash('Contraseña cambiada')
}
async function del() {
  await api(`/teacher/students/${props.id}`, { method: 'DELETE' })
  router.push('/profesor')
}
onMounted(load)
</script>

<style scoped>
h1 { margin: 6px 0; }
.grade { margin-top: 10px; padding-top: 10px; border-top: 1px dashed var(--border); }
.sub { margin-bottom: 8px; padding: 12px 16px; }
.sub summary { cursor: pointer; list-style: none; }
.ans { margin-top: 10px; }
.reason { white-space: pre-wrap; font-family: var(--mono); font-size: .85rem; background: var(--warn-soft); padding: 8px 10px; border-radius: 8px; }
.danger-zone { border-color: color-mix(in srgb, var(--bad) 35%, var(--border)); }
</style>

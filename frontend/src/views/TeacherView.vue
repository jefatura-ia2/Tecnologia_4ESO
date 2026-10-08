<template>
  <div>
    <div class="row">
      <h1 style="margin:0">Panel del profesorado</h1>
      <div class="spacer"></div>
      <button class="btn secondary" @click="downloadCsv">⬇ Exportar notas (CSV)</button>
    </div>
    <p v-if="info" class="muted">Código de clase para el registro del alumnado: <code class="code-big">{{ info.class_code }}</code></p>

    <div v-if="ov" class="kpis">
      <div class="card kpi"><div class="v">{{ ov.totals.students }}</div><div class="muted small">Alumnos</div></div>
      <div class="card kpi"><div class="v">{{ Math.round(ov.totals.avg_progress * 100) }}%</div><div class="muted small">Progreso medio</div></div>
      <div class="card kpi"><div class="v">{{ ov.totals.submissions }}</div><div class="muted small">Entregas</div></div>
      <div class="card kpi" :class="{ warnk: ov.totals.flags }"><div class="v">{{ ov.totals.flags }}</div><div class="muted small">Alertas por revisar</div></div>
    </div>

    <div class="tabs mt">
      <button v-for="t in tabs" :key="t.id" :class="{ active: tab === t.id }" @click="tab = t.id">{{ t.label }}</button>
    </div>
    <div v-if="error" class="alert bad">{{ error }}</div>

    <!-- ALUMNADO -->
    <section v-if="tab === 'alumnos' && ov">
      <div class="row mb">
        <input v-model="filter" placeholder="Buscar por nombre, usuario o grupo…" style="max-width:320px" />
        <span class="small muted">{{ students.length }} alumnos</span>
      </div>
      <div class="card table-wrap" style="padding:0">
        <table class="matrix">
          <thead>
            <tr>
              <th>Alumno/a</th><th>Grupo</th>
              <th v-for="m in ov.missions" :key="m.mission_id" class="c" :title="m.title">{{ m.icon }} M{{ m.number }}</th>
              <th class="c">Media</th><th class="c">Intentos</th><th class="c">⚠️</th><th>Última actividad</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in students" :key="s.id">
              <td><router-link :to="`/profesor/alumno/${s.id}`">{{ s.full_name }}</router-link>
                <div class="small muted">{{ s.username }} · <span class="badge" :class="s.board === 'pico_w' ? 'pico' : 'esp'">{{ s.board === 'pico_w' ? 'Pico W' : 'ESP32-S3' }}</span></div></td>
              <td>{{ s.group_name }}</td>
              <td v-for="pm in s.missions" :key="pm.mission_id" class="c">
                <span class="cell" :class="cellClass(pm)" :title="`Nota auto: ${(pm.avg_score * 10).toFixed(1)}`">{{ pm.passed }}/{{ pm.total }}</span>
              </td>
              <td class="c"><strong>{{ (s.avg_score * 10).toFixed(1) }}</strong></td>
              <td class="c">{{ s.attempts }}</td>
              <td class="c"><span v-if="s.flags" class="badge bad">{{ s.flags }}</span></td>
              <td class="small muted">{{ ago(s.last_activity) }}</td>
            </tr>
            <tr v-if="!students.length"><td :colspan="7 + ov.missions.length" class="muted">Todavía no hay alumnos registrados. Compárteles el código de clase.</td></tr>
          </tbody>
        </table>
      </div>
      <p class="small muted">Celdas: secciones superadas por misión. Verde = completada · amarillo = en curso · gris = sin empezar o bloqueada. La «Media» es la nota automática (0-10) de todas las secciones.</p>
    </section>

    <!-- ALERTAS -->
    <section v-if="tab === 'alertas'">
      <p class="muted small">Las alertas son <strong>indicios</strong> para revisar, no pruebas: en ejercicios sencillos es normal que haya soluciones parecidas. Habla con el alumnado antes de decidir.</p>
      <div v-if="!flags.length" class="card muted">No hay alertas pendientes. 👍</div>
      <div v-for="f in flags" :key="f.id" class="card flag">
        <div class="row">
          <router-link :to="`/profesor/alumno/${f.student_id}`"><strong>{{ f.student }}</strong></router-link>
          <span class="badge">{{ f.section_id }}</span>
          <span class="small muted">{{ parseDate(f.created_at).toLocaleString('es-ES') }} · nota {{ Math.round(f.score * 100) }}% · {{ f.elapsed_seconds }} s en la sección</span>
          <span class="spacer"></span>
          <button class="btn sm secondary" @click="dismiss(f.id)">Marcar revisada</button>
        </div>
        <pre class="reason">{{ f.reason }}</pre>
      </div>
    </section>

    <!-- DIFICULTAD -->
    <section v-if="tab === 'dificultad'">
      <p class="muted small">Media del último intento de cada alumno por pregunta. Las preguntas en rojo indican contenidos que conviene repasar en clase.</p>
      <div v-for="s in stats" :key="s.section_id" class="card mb">
        <div class="row">
          <strong>{{ s.section_id }} · {{ s.title }}</strong>
          <span class="spacer"></span>
          <span class="small muted">{{ s.students_passed }}/{{ s.students_started }} superada · {{ s.avg_attempts }} intentos de media</span>
        </div>
        <div class="items">
          <div v-for="i in s.items" :key="i.id" class="srow">
            <span class="badge">{{ i.id }}</span>
            <span class="small lbl">{{ i.label }}</span>
            <span class="spacer"></span>
            <span v-if="i.avg === null" class="small muted">sin datos</span>
            <span v-else class="badge" :class="i.avg >= .8 ? 'ok' : (i.avg >= .5 ? 'warn' : 'bad')">{{ Math.round(i.avg * 100) }}% (n={{ i.n }})</span>
          </div>
        </div>
      </div>
    </section>

    <!-- SOLUCIONES -->
    <section v-if="tab === 'soluciones'">
      <div class="row mb">
        <select v-model="solId" style="max-width:420px">
          <option value="">Elige una sección…</option>
          <optgroup v-for="m in missionList" :key="m.id" :label="`${m.icon} Misión ${m.number}: ${m.title}`">
            <option v-for="s in m.sections" :key="s.id" :value="s.id">{{ s.id }} · {{ s.title }}</option>
          </optgroup>
        </select>
      </div>
      <div v-if="sol" class="grid">
        <div v-for="item in sol.section.evaluation.items" :key="item.id" class="card">
          <div class="row"><span class="badge">{{ item.id }}</span><span class="badge">{{ item.type }}</span><span class="small muted">{{ item.points }} p</span></div>
          <div class="prose mt" v-html="md(item.question || item.prompt || '')"></div>
          <template v-if="item.type === 'quiz'">
            <ul><li v-for="o in item.options" :key="o.id" :class="{ right: o.id === item.answer }">{{ o.id }}) {{ o.text }} <span v-if="o.id === item.answer">✅</span></li></ul>
          </template>
          <template v-else-if="item.type === 'fill_blank'">
            <pre class="code">{{ item.text }}</pre>
            <div class="small">Respuestas aceptadas: <span v-for="(b, i) in item.blanks" :key="i"><strong>{{ i + 1 }}:</strong> {{ b.accept.join(' / ') }} &nbsp;</span></div>
          </template>
          <template v-else>
            <CodeBlock :code="item.solution" />
            <div class="small muted mt">Pruebas: {{ item.tests.map((t) => t.desc).join(' · ') }}</div>
          </template>
        </div>
      </div>
    </section>

    <!-- CLASE -->
    <section v-if="tab === 'clase' && ov">
      <div class="card">
        <h3 style="margin-top:0">Desbloquear una misión para toda la clase</h3>
        <p class="muted small">Por defecto cada misión se desbloquea al completar la anterior. Si el calendario avanza y quieres que todos puedan empezar la siguiente misión (por ejemplo, alumnado que ha faltado), desbloquéala aquí. El progreso de cada alumno se mantiene.</p>
        <div class="row">
          <select v-model="unlockId" style="max-width:360px">
            <option v-for="m in ov.missions" :key="m.mission_id" :value="m.mission_id">{{ m.icon }} Misión {{ m.number }}: {{ m.title }}</option>
          </select>
          <button class="btn" @click="unlockAll">Desbloquear para todos</button>
        </div>
        <div v-if="msg" class="alert ok">{{ msg }}</div>
      </div>
      <div v-if="info" class="card mt small">
        <h3 style="margin-top:0">Configuración actual</h3>
        <ul>
          <li>Inicio del trimestre: <strong>{{ info.course_start }}</strong> (variable <code>COURSE_START_DATE</code>)</li>
          <li>Tiempo mínimo en una sección antes del primer envío: <strong>{{ info.min_seconds }} s</strong></li>
          <li>Intentos fallidos sin espera: <strong>{{ info.free_attempts }}</strong>; después la espera crece en cada fallo.</li>
          <li>Umbral de similitud de código para alertar: <strong>{{ Math.round(info.plagiarism_threshold * 100) }}%</strong></li>
        </ul>
        <p class="muted">Se cambian en el archivo <code>.env</code> del servidor.</p>
      </div>
      <div class="grid mt">
        <div v-for="m in ov.missions" :key="m.mission_id" class="card row">
          <span style="font-size:1.4rem">{{ m.icon }}</span>
          <strong>M{{ m.number }} · {{ m.title }}</strong>
          <span class="spacer"></span>
          <span class="small muted">{{ m.completed }}/{{ m.students }} la han completado</span>
          <div class="progress" style="width:140px"><span :style="{ width: (m.students ? m.completed / m.students * 100 : 0) + '%' }"></span></div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import CodeBlock from '../components/CodeBlock.vue'
import { api, downloadCsv, parseDate } from '../lib/api.js'
import { md } from '../lib/markdown.js'

const tabs = [
  { id: 'alumnos', label: '👥 Alumnado' },
  { id: 'alertas', label: '⚠️ Alertas' },
  { id: 'dificultad', label: '📊 Dificultad' },
  { id: 'soluciones', label: '🔑 Soluciones' },
  { id: 'clase', label: '⚙️ Clase' },
]
const tab = ref('alumnos')
const ov = ref(null)
const info = ref(null)
const flags = ref([])
const stats = ref([])
const missionList = ref([])
const error = ref('')
const filter = ref('')
const solId = ref('')
const sol = ref(null)
const unlockId = ref('m2')
const msg = ref('')

const students = computed(() => {
  const q = filter.value.toLowerCase()
  return (ov.value?.students || []).filter((s) =>
    !q || [s.full_name, s.username, s.group_name].some((x) => (x || '').toLowerCase().includes(q)))
})

function cellClass(pm) {
  if (pm.completed) return 'done'
  if (pm.passed > 0) return 'doing'
  return 'none'
}
function ago(iso) {
  if (!iso) return '—'
  const d = (Date.now() - parseDate(iso).getTime()) / 1000
  if (d < 3600) return `hace ${Math.max(1, Math.round(d / 60))} min`
  if (d < 86400) return `hace ${Math.round(d / 3600)} h`
  return `hace ${Math.round(d / 86400)} días`
}

async function loadAll() {
  try {
    ;[ov.value, info.value, flags.value] = await Promise.all([api('/teacher/overview'), api('/teacher/info'), api('/teacher/flags')])
  } catch (e) { error.value = e.message }
}

watch(tab, async (t) => {
  error.value = ''
  try {
    if (t === 'dificultad' && !stats.value.length) stats.value = await api('/teacher/stats')
    if (t === 'soluciones' && !missionList.value.length) missionList.value = await api('/missions')
    if (t === 'alertas') flags.value = await api('/teacher/flags')
  } catch (e) { error.value = e.message }
})
watch(solId, async (id) => {
  sol.value = id ? await api(`/teacher/sections/${id}/solutions`) : null
})

async function dismiss(id) {
  await api(`/teacher/flags/${id}/dismiss`, { method: 'POST' })
  flags.value = flags.value.filter((f) => f.id !== id)
  if (ov.value) ov.value.totals.flags = Math.max(0, ov.value.totals.flags - 1)
}
async function unlockAll() {
  const r = await api('/teacher/unlock-all', { method: 'POST', body: { mission_id: unlockId.value } })
  msg.value = `Misión desbloqueada para ${r.unlocked} alumnos nuevos.`
  ov.value = await api('/teacher/overview')
}

onMounted(loadAll)
</script>

<style scoped>
.code-big { font-size: 1.05rem; font-weight: 700; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-top: 14px; }
.kpi { padding: 14px 16px; }
.kpi .v { font-size: 1.7rem; font-weight: 800; }
.kpi.warnk { border-color: var(--warn); background: var(--warn-soft); }
.matrix { margin: 0; min-width: 760px; }
.matrix th, .matrix td { border-left: none; border-right: none; }
.c { text-align: center; }
.cell { display: inline-block; min-width: 40px; padding: 2px 6px; border-radius: 6px; font-weight: 700; font-size: .85rem; }
.cell.done { background: var(--ok-soft); color: var(--ok); }
.cell.doing { background: var(--warn-soft); color: var(--warn); }
.cell.none { background: var(--surface-2); color: var(--muted); }
.flag { margin-bottom: 10px; }
.reason { white-space: pre-wrap; font-family: var(--mono); font-size: .85rem; background: var(--surface-2); padding: 8px 10px; border-radius: 8px; margin: 8px 0 0; }
.items { margin-top: 8px; display: grid; gap: 4px; }
.srow { display: flex; gap: 8px; align-items: center; }
.lbl { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.right { font-weight: 700; color: var(--ok); }
</style>

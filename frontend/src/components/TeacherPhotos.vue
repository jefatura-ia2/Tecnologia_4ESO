<template>
  <section>
    <div class="row mb" style="gap:10px; flex-wrap:wrap">
      <label class="small muted">Mostrar</label>
      <select v-model="estado" style="max-width:220px" @change="cargar">
        <option value="pendiente">Pendientes de revisar</option>
        <option value="rechazada">Rechazadas</option>
        <option value="aceptada">Aceptadas</option>
        <option value="">Todas</option>
      </select>
      <input v-model="filtro" placeholder="Filtrar por alumno, grupo o sección…" style="max-width:300px" />
      <span class="small muted">{{ lista.length }} fotos</span>
    </div>
    <div v-if="error" class="alert bad">{{ error }}</div>
    <div v-if="cargando" class="muted">Cargando…</div>
    <div v-else-if="!lista.length" class="card muted">No hay fotos {{ estado ? `${estado}s` : '' }}. 👍</div>

    <div class="fotos">
      <article v-for="f in lista" :key="f.username + f.section_id" class="card foto">
        <div class="img" @click="ampliar(f)">
          <img v-if="imgs[clave(f)]" :src="imgs[clave(f)]" :alt="`Montaje de ${f.student} en ${f.section_title}`" />
          <span v-else class="muted small">Cargando foto…</span>
        </div>
        <div class="small"><strong>{{ f.student }}</strong> <span class="muted">· {{ f.group_name }}</span></div>
        <div class="small muted">M{{ f.mission_number }} · {{ f.section_title }} · {{ fecha(f.uploaded_at) }}</div>
        <div v-if="f.note" class="small">💬 {{ f.note }}</div>
        <div class="small"><span class="badge" :class="badge(f.status)">{{ f.status }}</span>
          <span v-if="!f.score_passed" class="badge warn" title="La evaluación de la sección aún no está aprobada">evaluación sin aprobar</span></div>
        <textarea v-model="comentarios[clave(f)]" rows="2" placeholder="Comentario para el alumno (opcional)"></textarea>
        <div class="row" style="gap:8px">
          <button class="btn sm" @click="revisar(f, 'aceptada')">✅ Aceptar</button>
          <button class="btn sm secondary" @click="revisar(f, 'rechazada')">❌ Rechazar</button>
        </div>
      </article>
    </div>

    <div v-if="grande" class="modal" @click="grande = null">
      <img :src="grande" alt="Foto ampliada del montaje" />
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { api, parseDate } from '../lib/api.js'

const emit = defineEmits(['cambio'])
const estado = ref('pendiente')
const filtro = ref('')
const todas = ref([])
const imgs = reactive({})
const comentarios = reactive({})
const cargando = ref(false)
const error = ref('')
const grande = ref(null)

const clave = (f) => `${f.username}/${f.section_id}`
const fecha = (iso) => parseDate(iso)?.toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' }) || ''
const badge = (s) => ({ pendiente: '', aceptada: 'ok', rechazada: 'bad' }[s])
const lista = computed(() => {
  const q = filtro.value.toLowerCase()
  return todas.value.filter((f) => !q || `${f.student} ${f.username} ${f.group_name} ${f.section_title} m${f.mission_number}`.toLowerCase().includes(q))
})

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    todas.value = await api(`/teacher/photos${estado.value ? `?status=${estado.value}` : ''}`)
    for (const f of todas.value) {
      comentarios[clave(f)] = f.comment || ''
      if (!imgs[clave(f)]) {
        api(`/teacher/photos/${encodeURIComponent(f.username)}/${f.section_id}`)
          .then((r) => { imgs[clave(f)] = r.image })
          .catch(() => { imgs[clave(f)] = '' })
      }
    }
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
}

async function revisar(f, status) {
  try {
    await api(`/teacher/photos/${encodeURIComponent(f.username)}/${f.section_id}`, { method: 'PUT', body: { status, comment: comentarios[clave(f)] || '' } })
    f.status = status
    if (estado.value && estado.value !== status) todas.value = todas.value.filter((x) => x !== f)
    emit('cambio')
  } catch (e) {
    error.value = e.message
  }
}

function ampliar(f) {
  if (imgs[clave(f)]) grande.value = imgs[clave(f)]
}

onMounted(cargar)
</script>

<style scoped>
.fotos { display: grid; gap: 14px; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
.foto { display: grid; gap: 6px; padding: 12px; }
.img { height: 190px; display: flex; align-items: center; justify-content: center; background: var(--surface-2); border-radius: 8px; overflow: hidden; cursor: zoom-in; }
.img img { width: 100%; height: 100%; object-fit: cover; }
textarea { width: 100%; resize: vertical; }
.modal { position: fixed; inset: 0; background: rgba(0, 0, 0, .8); display: flex; align-items: center; justify-content: center; z-index: 50; cursor: zoom-out; padding: 16px; }
.modal img { max-width: 100%; max-height: 100%; border-radius: 8px; }
</style>

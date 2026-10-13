<template>
  <div class="card foto" :class="estadoClase">
    <div class="row" style="gap:10px; align-items:flex-start">
      <div class="ico">📷</div>
      <div style="flex:1; min-width:0">
        <h3 style="margin:0 0 4px">Foto del montaje <span class="obl">obligatoria</span></h3>
        <p class="small" style="margin:0">{{ indicaciones }} <span class="muted">Que no salgan caras.</span></p>
      </div>
    </div>

    <div v-if="photo" class="estado" :class="photo.status">
      <strong>{{ etiqueta }}</strong>
      <span class="small muted"> · subida el {{ fecha(photo.uploaded_at) }}</span>
      <div v-if="photo.comment" class="small"><strong>Comentario del profesor:</strong> {{ photo.comment }}</div>
    </div>
    <p v-else-if="isTeacher" class="small muted">El alumnado debe subir aquí la foto de su montaje. Revísalas en el Panel → Fotos.</p>
    <p v-else class="small muted">Haz la foto con el móvil o el ordenador; se reduce automáticamente antes de subirla. Fotografía solo el montaje: que no salgan caras ni datos personales.</p>

    <div v-if="!isTeacher" class="row" style="gap:10px; flex-wrap:wrap; margin-top:10px">
      <label class="btn" :class="{ disabled: busy }">
        {{ photo ? 'Cambiar foto' : 'Hacer o elegir foto' }}
        <input type="file" accept="image/*" capture="environment" hidden :disabled="busy" @change="elegir" />
      </label>
      <button v-if="photo && !verMia" type="button" class="btn ghost" @click="cargarMia">Ver mi foto</button>
    </div>

    <div v-if="preview" class="prev">
      <img :src="preview.dataUrl" alt="Vista previa de la foto del montaje" />
      <div class="small muted">{{ preview.width }} × {{ preview.height }} px · {{ preview.kb }} KB</div>
      <input v-model="nota" class="nota" maxlength="300" placeholder="Comentario opcional (qué se ve, qué funciona…)" />
      <div class="row" style="gap:10px">
        <button type="button" class="btn" :disabled="busy" @click="subir">{{ busy ? 'Subiendo…' : 'Subir foto' }}</button>
        <button type="button" class="btn ghost" :disabled="busy" @click="preview = null">Cancelar</button>
      </div>
    </div>
    <div v-else-if="verMia" class="prev"><img :src="verMia" alt="Tu foto del montaje" /></div>

    <div v-if="error" class="alert warn" style="margin-top:10px">{{ error }}</div>
    <div v-if="ok" class="alert ok" style="margin-top:10px">{{ ok }}</div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { api, parseDate, session } from '../lib/api.js'
import { comprimirFoto } from '../lib/imagen.js'

const props = defineProps({
  sectionId: { type: String, required: true },
  indicaciones: { type: String, default: '' },
  photo: { type: Object, default: null },
})
const emit = defineEmits(['subida'])
const isTeacher = computed(() => session.user?.role === 'teacher')
const preview = ref(null)
const nota = ref('')
const busy = ref(false)
const error = ref('')
const ok = ref('')
const verMia = ref(null)

const etiqueta = computed(() => ({
  pendiente: '⏳ Foto subida · pendiente de revisión',
  aceptada: '✅ Foto aceptada por el profesor',
  rechazada: '❌ Foto rechazada: vuelve a subirla',
}[props.photo?.status] || ''))
const estadoClase = computed(() => (props.photo ? props.photo.status : 'falta'))
const fecha = (iso) => parseDate(iso)?.toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' }) || ''

async function elegir(ev) {
  error.value = ''
  ok.value = ''
  const file = ev.target.files?.[0]
  ev.target.value = ''
  if (!file) return
  try {
    busy.value = true
    preview.value = await comprimirFoto(file)
    verMia.value = null
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
  }
}

async function subir() {
  busy.value = true
  error.value = ''
  try {
    const r = await api(`/sections/${props.sectionId}/photo`, { method: 'POST', body: { image: preview.value.dataUrl, note: nota.value } })
    preview.value = null
    nota.value = ''
    ok.value = '¡Foto subida! El profesor la revisará.'
    emit('subida', r)
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
  }
}

async function cargarMia() {
  try {
    verMia.value = (await api(`/sections/${props.sectionId}/photo`)).image
  } catch (e) {
    error.value = e.message
  }
}
</script>

<style scoped>
.foto { border-left: 5px solid var(--warn); margin-top: 16px; }
.foto.pendiente { border-left-color: var(--primary); }
.foto.aceptada { border-left-color: var(--ok); }
.foto.rechazada { border-left-color: var(--bad); }
.ico { font-size: 1.8rem; line-height: 1; }
.obl { font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 999px; background: var(--warn-soft); color: var(--warn); vertical-align: middle; }
.estado { margin-top: 10px; padding: 8px 12px; border-radius: 8px; background: var(--primary-soft); }
.estado.aceptada { background: var(--ok-soft); }
.estado.rechazada { background: var(--bad-soft); }
.prev { margin-top: 12px; display: grid; gap: 8px; }
.prev img { max-width: 100%; max-height: 420px; object-fit: contain; border-radius: 10px; border: 1px solid var(--border, #e2e8f0); background: var(--surface-2); }
.nota { width: 100%; }
label.btn { cursor: pointer; }
label.btn.disabled { opacity: 0.6; pointer-events: none; }
</style>

<template>
  <div>
    <h1 style="margin:0">Material complementario</h1>
    <p class="muted" style="margin:4px 0 18px">
      Recursos que puedes consultar en cualquier momento, en paralelo a las sesiones del curso. No hace falta tenerlos
      desbloqueados ni cuentan para la nota de la plataforma, salvo que tu profesor te diga otra cosa.
    </p>

    <div v-if="!abierto" class="grid">
      <article v-for="r in RECURSOS" :key="r.id" class="card recurso">
        <div class="row" style="gap:12px; align-items:flex-start">
          <div class="ico">{{ r.icono }}</div>
          <div style="flex:1; min-width:0">
            <h2 style="margin:0 0 4px; font-size:1.15rem">{{ r.titulo }}</h2>
            <div class="small muted">{{ r.autor }} · {{ r.sesiones }}</div>
          </div>
        </div>
        <p>{{ r.resumen }}</p>
        <p class="small muted">🔗 {{ r.relacion }}</p>
        <div class="tags"><span v-for="t in r.etiquetas" :key="t" class="tag">{{ t }}</span></div>
        <div class="row" style="gap:10px; margin-top:12px; flex-wrap:wrap">
          <button class="btn" @click="abrir(r)">Abrir aquí</button>
          <a class="btn ghost" :href="r.archivo" target="_blank" rel="noopener">Abrir en pestaña nueva ↗</a>
        </div>
      </article>
    </div>

    <div v-else>
      <div class="row mb" style="gap:10px; flex-wrap:wrap">
        <button class="btn ghost sm" @click="abierto = null">← Volver a los recursos</button>
        <strong style="flex:1; min-width:200px">{{ abierto.titulo }}</strong>
        <a class="btn ghost sm" :href="abierto.archivo" target="_blank" rel="noopener">Pantalla completa ↗</a>
      </div>
      <iframe class="visor" :src="abierto.archivo" :title="abierto.titulo"></iframe>
      <p class="small muted">Tu progreso dentro del taller se guarda en este navegador.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RECURSOS } from '../lib/recursos.js'

const abierto = ref(null)
function abrir(r) {
  abierto.value = r
}
</script>

<style scoped>
.grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }
.recurso p { margin: 10px 0 0; overflow-wrap: anywhere; }
.ico { font-size: 2rem; line-height: 1; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.tag { font-size: 0.78rem; padding: 2px 8px; border-radius: 999px; background: #e0f2f1; color: #0f766e; }
.visor { width: 100%; height: calc(100vh - 210px); min-height: 520px; border: 1px solid #e2e8f0; border-radius: 12px; background: #fff; }
</style>

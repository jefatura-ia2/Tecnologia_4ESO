<template>
  <header v-if="session.token" class="topbar">
    <div class="container row">
      <router-link :to="isTeacher ? '/profesor' : '/'" class="brand">
        <span class="brand-main">⚙️ TEC_IVJP_lab27 <span class="lvl">4º ESO</span></span>
        <span class="school">IES Valle del Jerte (Plasencia) <span class="author">Autor: José I. Sánchez Castaño</span></span>
      </router-link>
      <nav class="nav">
        <router-link v-if="isTeacher" to="/profesor">Panel</router-link>
        <router-link to="/">Misiones</router-link>
        <router-link to="/calendario">Calendario</router-link>
        <router-link to="/placas">Material</router-link>
      </nav>
      <div class="spacer"></div>
      <div class="user row">
        <select v-if="!isTeacher" v-model="board" class="board" title="Placa que usas en clase" @change="saveBoard">
          <option value="pico_w">Pico W</option>
          <option value="esp32_s3">ESP32-S3</option>
        </select>
        <span class="name">{{ session.user?.full_name }}</span>
        <button class="btn ghost sm" @click="doLogout">Salir</button>
      </div>
    </div>
  </header>
  <main class="container page">
    <router-view />
  </main>
  <footer class="container footer muted small">
    IES Valle del Jerte (Plasencia) · Autor: José I. Sánchez Castaño · TEC_IVJP_lab27 · Programación MicroPython, electrónica y neumática
  </footer>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api, logout, session, updateUser } from './lib/api.js'

const router = useRouter()
const isTeacher = computed(() => session.user?.role === 'teacher')
const board = ref(session.user?.board || 'pico_w')
watch(() => session.user, (u) => { if (u) board.value = u.board })

async function saveBoard() {
  try {
    updateUser(await api('/auth/me', { method: 'PATCH', body: { board: board.value } }))
  } catch { /* se mantiene la elección local */ }
}

function doLogout() {
  logout()
  router.push('/login')
}
</script>

<style scoped>
.topbar { background: var(--surface); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 10; }
.topbar .container { min-height: 58px; padding-top: 6px; padding-bottom: 6px; }
.brand { display: flex; flex-direction: column; line-height: 1.2; color: var(--text); text-decoration: none; white-space: nowrap; }
.brand-main { font-weight: 800; font-size: 1.1rem; }
.school { font-size: .78rem; font-weight: 600; color: var(--muted); white-space: normal; }
.author { font-weight: 500; }
.author::before { content: "· "; }
@media (max-width: 520px) { .author { display: block; } .author::before { content: none; } }
.lvl { font-size: .72rem; font-weight: 700; background: var(--accent-soft); color: var(--accent); padding: 2px 7px; border-radius: 99px; margin-left: 4px; vertical-align: middle; }
.nav { display: flex; gap: 2px; flex-wrap: wrap; }
.nav a { color: var(--muted); text-decoration: none; font-weight: 600; padding: 6px 10px; border-radius: 8px; font-size: .95rem; }
.nav a.router-link-exact-active { color: var(--primary); background: var(--primary-soft); }
.user { gap: 8px; }
.board { width: auto; padding: 5px 8px; font-size: .88rem; }
.name { font-weight: 600; font-size: .92rem; }
.page { padding-top: 24px; padding-bottom: 32px; min-height: calc(100vh - 130px); }
.footer { padding: 18px 16px 28px; text-align: center; }
@media (max-width: 720px) {
  .name { display: none; }
  .nav a { padding: 5px 7px; font-size: .88rem; }
}
</style>

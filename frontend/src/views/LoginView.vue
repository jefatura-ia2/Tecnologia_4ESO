<template>
  <div class="login">
    <div class="hero">
      <div class="emoji">💨⚙️</div>
      <h1>TEC_IVJP_lab27</h1>
      <p class="school">IES Valle del Jerte (Plasencia)</p>
      <p class="author muted small">Autor: José I. Sánchez Castaño</p>
      <p class="muted">Aprende a programar <strong>Raspberry Pi Pico W</strong> y <strong>ESP32-S3</strong> con MicroPython
        a medir con el osciloscopio, a crear un control de acceso NFC y a automatizar circuitos neumáticos con electroválvulas.</p>
    </div>
    <div class="card form">
      <div class="tabs">
        <button :class="{ active: mode === 'login' }" @click="mode = 'login'">Entrar</button>
        <button :class="{ active: mode === 'register' }" @click="mode = 'register'">Crear cuenta</button>
      </div>
      <form @submit.prevent="submit">
        <template v-if="mode === 'register'">
          <label for="fn">Nombre y apellidos</label>
          <input id="fn" v-model.trim="f.full_name" required autocomplete="name" />
          <div class="two">
            <div>
              <label for="gr">Grupo</label>
              <input id="gr" v-model.trim="f.group_name" placeholder="4ºA" />
            </div>
            <div>
              <label for="bd">Tu placa</label>
              <select id="bd" v-model="f.board">
                <option value="pico_w">Raspberry Pi Pico W</option>
                <option value="esp32_s3">ESP32-S3-DevKit</option>
              </select>
            </div>
          </div>
        </template>
        <label for="us">Usuario</label>
        <input id="us" v-model.trim="f.username" required autocomplete="username" autocapitalize="off" />
        <label for="pw">Contraseña</label>
        <input id="pw" v-model="f.password" type="password" required minlength="6"
               :autocomplete="mode === 'login' ? 'current-password' : 'new-password'" />
        <template v-if="mode === 'register'">
          <label for="cc">Código de clase</label>
          <input id="cc" v-model.trim="f.class_code" required placeholder="Te lo da tu profesor/a" />
        </template>
        <div v-if="error" class="alert bad">{{ error }}</div>
        <button class="btn full mt" :disabled="busy">{{ mode === 'login' ? 'Entrar' : 'Crear cuenta' }}</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, setSession } from '../lib/api.js'

const router = useRouter()
const mode = ref('login')
const busy = ref(false)
const error = ref('')
const f = reactive({ username: '', password: '', full_name: '', group_name: '', board: 'pico_w', class_code: '' })

async function submit() {
  error.value = ''
  busy.value = true
  try {
    const data = mode.value === 'login'
      ? await api('/auth/login', { method: 'POST', body: { username: f.username, password: f.password } })
      : await api('/auth/register', { method: 'POST', body: { ...f } })
    setSession(data.token, data.user)
    router.push(data.user.role === 'teacher' ? '/profesor' : '/')
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.login { max-width: 440px; margin: 4vh auto 0; }
.hero { text-align: center; margin-bottom: 18px; }
.hero h1 { margin: 6px 0; font-size: 2rem; }
.emoji { font-size: 2.6rem; }
.school { margin: 0; font-weight: 700; color: var(--primary); }
.author { margin: 2px 0 8px; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.full { width: 100%; justify-content: center; }
</style>

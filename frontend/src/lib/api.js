import { reactive } from 'vue'

function loadSession() {
  try {
    return JSON.parse(localStorage.getItem('neumalab-session') || 'null')
  } catch {
    return null
  }
}

const saved = loadSession()

export const session = reactive({
  token: saved?.token || null,
  user: saved?.user || null,
})

function persist() {
  try {
    localStorage.setItem('neumalab-session', JSON.stringify({ token: session.token, user: session.user }))
  } catch {
    /* sin almacenamiento: la sesión dura lo que la pestaña */
  }
}

export function setSession(token, user) {
  session.token = token
  session.user = user
  persist()
}

export function updateUser(user) {
  session.user = user
  persist()
}

export function logout() {
  session.token = null
  session.user = null
  try { localStorage.removeItem('neumalab-session') } catch { /* nada */ }
}

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.status = status
  }
}

export async function api(path, { method = 'GET', body, raw = false } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (session.token) headers.Authorization = `Bearer ${session.token}`
  const res = await fetch(`/api${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (res.status === 401 && session.token) {
    logout()
    window.location.hash = '#/login'
  }
  if (!res.ok) {
    let msg = `Error ${res.status}`
    try {
      const data = await res.json()
      if (typeof data.detail === 'string') msg = data.detail
      else if (Array.isArray(data.detail)) msg = data.detail.map((d) => d.msg).join('. ')
    } catch { /* respuesta sin JSON */ }
    throw new ApiError(res.status, msg)
  }
  return raw ? res : res.json()
}

export async function downloadCsv() {
  const res = await api('/teacher/export.csv', { raw: true })
  const blob = await res.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'notas_tec_ivjp_lab27.csv'
  a.click()
  URL.revokeObjectURL(url)
}

/** Fecha ISO del servidor (con o sin zona horaria) → Date */
export function parseDate(iso) {
  if (!iso) return null
  return new Date(/Z$|[+-]\d\d:\d\d$/.test(iso) ? iso : iso + 'Z')
}

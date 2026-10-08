// Ejecuta los ejercicios de código en el navegador (Pyodide en un Web Worker).
import { reactive } from 'vue'

const TIMEOUT_MS = 6000
export const pyStatus = reactive({ state: 'idle' }) // idle | loading | ready | error

let worker = null
let readyPromise = null
let seq = 0
const pending = new Map()

function start() {
  pyStatus.state = 'loading'
  worker = new Worker('/sandbox/worker.mjs', { type: 'module' })
  readyPromise = new Promise((resolve, reject) => {
    worker.onmessage = (e) => {
      const msg = e.data
      if (msg.type === 'ready') {
        pyStatus.state = 'ready'
        resolve()
      } else if (msg.type === 'result' && pending.has(msg.id)) {
        pending.get(msg.id)(msg.result)
        pending.delete(msg.id)
      }
    }
    worker.onerror = (err) => {
      pyStatus.state = 'error'
      reject(err)
      for (const [id, done] of pending) {
        done({ ok: false, error: { type: 'Crash', message: 'El simulador se detuvo', line: null }, tests: [] })
        pending.delete(id)
      }
    }
  })
  return readyPromise
}

export function preloadPython() {
  if (!worker) start().catch(() => {})
  return readyPromise
}

function restart() {
  worker?.terminate()
  worker = null
  start().catch(() => {})
}

/** Ejecuta {code, tests, setup} y devuelve el resultado del simulador. */
export async function runPython(req) {
  if (!worker) start()
  await readyPromise
  const id = ++seq
  return new Promise((resolve) => {
    const timer = setTimeout(() => {
      pending.delete(id)
      restart() // único modo de parar un bucle infinito
      resolve({ ok: false, error: { type: 'Timeout', message: 'Tiempo agotado', line: null }, tests: [] })
    }, TIMEOUT_MS)
    pending.set(id, (result) => {
      clearTimeout(timer)
      resolve(result)
    })
    worker.postMessage({ id, req: JSON.parse(JSON.stringify(req)) }) // sin proxies reactivos de Vue
  })
}

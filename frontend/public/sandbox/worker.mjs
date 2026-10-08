// Web Worker: ejecuta el simulador de MicroPython (harness.py) con Pyodide.
// Al estar en un hilo aparte, un bucle infinito no bloquea la página: el hilo principal lo detiene.
import { loadPyodide } from '/pyodide/pyodide.mjs'

let evaluate = null

const ready = (async () => {
  const py = await loadPyodide({ indexURL: '/pyodide/' })
  const src = await (await fetch('/sandbox/harness.py', { cache: 'no-cache' })).text()
  py.FS.writeFile('/home/pyodide/harness.py', src)
  py.runPython('import sys; sys.path.insert(0, "/home/pyodide"); import harness')
  evaluate = py.globals.get('harness').evaluate_json
  self.postMessage({ type: 'ready' })
})()

self.onmessage = async (e) => {
  const { id, req } = e.data
  try {
    await ready
    self.postMessage({ type: 'result', id, result: JSON.parse(evaluate(JSON.stringify(req))) })
  } catch (err) {
    self.postMessage({
      type: 'result',
      id,
      result: { ok: false, error: { type: 'Crash', message: String(err).slice(0, 300), line: null }, tests: [] },
    })
  }
}

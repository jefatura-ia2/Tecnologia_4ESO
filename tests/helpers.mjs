import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { loadPyodide } from 'pyodide'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
let evaluate = null

/** Ejecuta el simulador harness.py en Pyodide, igual que el navegador. */
export async function runPython(req) {
  if (!evaluate) {
    const py = await loadPyodide()
    py.FS.writeFile('/home/pyodide/harness.py', fs.readFileSync(path.join(root, 'backend/app/sandbox/harness.py'), 'utf8'))
    py.runPython('import sys; sys.path.insert(0, "/home/pyodide"); import harness')
    evaluate = py.globals.get('harness').evaluate_json
  }
  return JSON.parse(evaluate(JSON.stringify(req)))
}

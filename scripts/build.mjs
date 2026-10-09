// Prepara todo lo que necesitan Netlify y el frontend:
//  1. Convierte el temario (YAML) en un módulo JS para las funciones (con soluciones: NO se publica).
//  2. Copia el simulador de MicroPython (harness.py) y Pyodide a frontend/public para corregir en el navegador.
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import yaml from 'js-yaml'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const missionsDir = path.join(root, 'backend/app/content/missions')
const PASSING = { 1: 0.7, 2: 0.7, 3: 0.75, 4: 0.75, 5: 0.75 }

const missions = fs.readdirSync(missionsDir)
  .filter((f) => f.endsWith('.yml'))
  .sort()
  .map((f) => yaml.load(fs.readFileSync(path.join(missionsDir, f), 'utf8')))
  .sort((a, b) => a.number - b.number)

for (const m of missions) {
  m.passing_score = PASSING[m.number] ?? 0.8
  for (const s of m.sections) {
    s.mission_id = m.id
    s.max_points = s.evaluation.items.reduce((a, i) => a + (i.points ?? 1), 0)
  }
}

const out = path.join(root, 'netlify/functions/lib/content.generated.mjs')
fs.mkdirSync(path.dirname(out), { recursive: true })
fs.writeFileSync(out, `// Archivo generado por scripts/build.mjs — no editar a mano.\nexport default ${JSON.stringify(missions)}\n`)

const pub = path.join(root, 'frontend/public')
fs.mkdirSync(path.join(pub, 'sandbox'), { recursive: true })
fs.copyFileSync(path.join(root, 'backend/app/sandbox/harness.py'), path.join(pub, 'sandbox/harness.py'))

const pyoSrc = path.join(root, 'node_modules/pyodide')
const pyoDst = path.join(pub, 'pyodide')
fs.mkdirSync(pyoDst, { recursive: true })
for (const f of ['pyodide.mjs', 'pyodide.asm.mjs', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json']) {
  if (fs.existsSync(path.join(pyoSrc, f))) fs.copyFileSync(path.join(pyoSrc, f), path.join(pyoDst, f))
  else console.warn('Aviso: falta', f, 'en el paquete pyodide')
}

const sections = missions.reduce((a, m) => a + m.sections.length, 0)
console.log(`Temario: ${missions.length} misiones, ${sections} secciones → ${path.relative(root, out)}`)
console.log('Simulador y Pyodide copiados a frontend/public/')

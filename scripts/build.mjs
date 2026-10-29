// Prepara todo lo que necesitan Netlify y el frontend:
//  1. Convierte el temario (YAML) en un módulo JS para las funciones (con soluciones: NO se publica).
//  2. Copia el simulador de MicroPython (harness.py) y Pyodide a frontend/public para corregir en el navegador.
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import yaml from 'js-yaml'
import { marked } from 'marked'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const missionsDir = path.join(root, 'backend/app/content/missions')
const PASSING = { 1: 0.7, 2: 0.7, 3: 0.75, 4: 0.75, 5: 0.75, 6: 0.75, 7: 0.75, 8: 0.75 }

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

// 3. Copia los programas de firmware/ a frontend/public/descargas/ para que el alumnado los descargue
const desc = path.join(pub, 'descargas')
fs.mkdirSync(desc, { recursive: true })
for (const f of fs.readdirSync(path.join(root, 'firmware'))) {
  if (f.endsWith('.py') && f !== 'secretos.py') fs.copyFileSync(path.join(root, 'firmware', f), path.join(desc, f))
}
// Proyecto Smart Sign (misiones 4-6): modelo OpenSCAD, STL, mosquitto.conf, panel del profesor y guía
fs.cpSync(path.join(root, 'smart_sign'), path.join(desc, 'smart_sign'), { recursive: true })
const guia = marked.parse(fs.readFileSync(path.join(root, 'smart_sign/README.md'), 'utf8'))
fs.writeFileSync(path.join(desc, 'smart_sign/guia.html'), `<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Smart Sign · Guía del profesor</title>
<style>body{font:16px/1.55 system-ui,sans-serif;max-width:960px;margin:0 auto;padding:16px;color:#1f2937;background:#fff}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px;display:block;overflow-x:auto}th,td{border:1px solid #d1d5db;padding:6px 8px;text-align:left}
th{background:#f1f5f9}pre{background:#0f172a;color:#e2e8f0;padding:12px;border-radius:8px;overflow-x:auto}code{font-size:13px}
blockquote{border-left:4px solid #0f766e;margin:0;padding:4px 12px;background:#f0fdfa}</style></head><body>
${guia.replace(/href="(?!https?:|#|\/)([^"]+)"/g, (m, f) => `href="${f.replace(/^\.\.\/firmware\//, '../')}"`)}</body></html>`)

const sections = missions.reduce((a, m) => a + m.sections.length, 0)
console.log(`Temario: ${missions.length} misiones, ${sections} secciones → ${path.relative(root, out)}`)
console.log('Simulador y Pyodide copiados a frontend/public/')

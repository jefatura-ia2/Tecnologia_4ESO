// Servidor local que imita Netlify: sirve frontend/dist y la función /api/* con datos en una carpeta.
// Uso: npm run build && SECRET_KEY=... TEACHER_PASSWORD=... node scripts/dev-server.mjs
import fs from 'node:fs'
import http from 'node:http'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
process.env.LOCAL_STORE_DIR ||= path.join(root, '.datos-locales')
process.env.SECRET_KEY ||= 'clave-local-de-desarrollo-no-usar-en-produccion'
process.env.TEACHER_PASSWORD ||= 'profe123'
const { default: handler } = await import('../netlify/functions/api.mjs')

const dist = path.join(root, 'frontend/dist')
const PORT = parseInt(process.env.PORT || '8888', 10)
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css',
  '.wasm': 'application/wasm', '.json': 'application/json', '.zip': 'application/zip', '.py': 'text/plain; charset=utf-8', '.svg': 'image/svg+xml' }

http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`)
  if (url.pathname.startsWith('/api/')) {
    const chunks = []
    for await (const c of req) chunks.push(c)
    const request = new Request(url, { method: req.method, headers: req.headers, body: chunks.length ? Buffer.concat(chunks) : undefined })
    const response = await handler(request)
    res.writeHead(response.status, Object.fromEntries(response.headers))
    res.end(Buffer.from(await response.arrayBuffer()))
    return
  }
  let file = path.join(dist, decodeURIComponent(url.pathname))
  if (!file.startsWith(dist) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) file = path.join(dist, 'index.html')
  res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' })
  fs.createReadStream(file).pipe(res)
}).listen(PORT, () => {
  console.log(`NeumaLab en http://localhost:${PORT}  (datos en ${process.env.LOCAL_STORE_DIR})`)
})

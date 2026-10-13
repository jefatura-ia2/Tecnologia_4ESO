// La API funcionando sobre Netlify Blobs (emulador oficial de @netlify/blobs), como en producción.
import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { after, test } from 'node:test'
import { BlobsServer } from '@netlify/blobs/server'

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'blobs-'))
const server = new BlobsServer({ directory: dir, token: 'tok', port: 0 })
const { port } = await server.start()
process.env.NETLIFY_BLOBS_CONTEXT = Buffer.from(JSON.stringify({
  edgeURL: `http://localhost:${port}`, uncachedEdgeURL: `http://localhost:${port}`, siteID: 'site1', token: 'tok',
})).toString('base64')
delete process.env.LOCAL_STORE_DIR
process.env.SECRET_KEY = 'clave-de-pruebas-suficientemente-larga'
process.env.TEACHER_PASSWORD = 'profe123'

const { default: handler } = await import('../netlify/functions/api.mjs')
const call = async (method, url, body, token) => {
  const res = await handler(new Request('http://x' + url, {
    method, body: body ? JSON.stringify(body) : undefined,
    headers: { 'content-type': 'application/json', ...(token ? { authorization: `Bearer ${token}` } : {}) },
  }))
  return { status: res.status, data: await res.json().catch(() => null) }
}

after(() => server.stop())

test('registro, sección y panel con Netlify Blobs', async () => {
  assert.equal((await call('GET', '/api/health')).data.storage, 'netlify-blobs')
  const reg = await call('POST', '/api/auth/register', { username: 'ana', full_name: 'Ana', password: 'secreto1', class_code: '4ESO-NEUMA' })
  assert.equal(reg.status, 200)
  assert.equal((await call('GET', '/api/sections/m1s1', null, reg.data.token)).status, 200)
  const t = await call('POST', '/api/auth/login', { username: 'profesor', password: 'profe123' })
  assert.equal(t.status, 200)
  const ov = await call('GET', '/api/teacher/overview', null, t.data.token)
  assert.equal(ov.data.totals.students, 1)
  assert.equal(ov.data.students[0].username, 'ana')
  const det = await call('GET', '/api/teacher/students/ana', null, t.data.token)
  assert.ok(det.data.missions[0].sections[0].started_at)
})

test('las fotos de los montajes (~2 MB) caben en Netlify Blobs', async () => {
  const { getDb } = await import('../netlify/functions/lib/store.mjs')
  const db = await getDb()
  const image = 'data:image/jpeg;base64,' + Buffer.alloc(1_800_000, 3).toString('base64')
  await db.set('photos/ana/m1s2', { image, uploaded_at: new Date().toISOString() })
  const back = await db.get('photos/ana/m1s2')
  assert.equal(back.image.length, image.length)
  assert.deepEqual(await db.list('photos/ana/'), ['photos/ana/m1s2'])
})

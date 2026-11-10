// Pruebas de la Netlify Function /api/* con almacenamiento local (sin Netlify).
import assert from 'node:assert/strict'
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { before, test } from 'node:test'
import { runPython } from './helpers.mjs'

process.env.LOCAL_STORE_DIR = fs.mkdtempSync(path.join(os.tmpdir(), 'neumalab-'))
process.env.SECRET_KEY = 'clave-de-pruebas-suficientemente-larga'
process.env.TEACHER_PASSWORD = 'profe123'
process.env.MIN_SECONDS_BEFORE_SUBMIT = '0'
process.env.COOLDOWN_BASE_SECONDS = '60'

const { default: handler } = await import('../netlify/functions/api.mjs')
const { default: missions } = await import('../netlify/functions/lib/content.generated.mjs')

async function call(method, url, { token, body } = {}) {
  const headers = { 'content-type': 'application/json' }
  if (token) headers.authorization = `Bearer ${token}`
  const res = await handler(new Request('http://x' + url, { method, headers, body: body ? JSON.stringify(body) : undefined }))
  const text = await res.text()
  let data = text
  try { data = JSON.parse(text) } catch { /* csv */ }
  return { status: res.status, data, text }
}

const section = (id) => missions.flatMap((m) => m.sections).find((s) => s.id === id)

async function correctPayload(id) {
  const s = section(id)
  const answers = {}
  const code_results = {}
  for (const item of s.evaluation.items) {
    if (item.type === 'quiz') answers[item.id] = item.answer
    else if (item.type === 'fill_blank') answers[item.id] = item.blanks.map((b) => b.accept[0])
    else {
      answers[item.id] = item.solution
      code_results[item.id] = await runPython({ code: item.solution, tests: item.tests, setup: item.setup || [] })
    }
  }
  return { answers, code_results }
}

let ana, profe

// Foto de prueba (la API solo comprueba formato y tamaño)
const FOTO = 'data:image/jpeg;base64,' + Buffer.alloc(6000, 7).toString('base64')
const subirFoto = (token, sid, image = FOTO) => call('POST', `/api/sections/${sid}/photo`, { token, body: { image, note: 'montaje' } })

before(async () => {
  const r = await call('POST', '/api/auth/register', { body: { username: 'ana', full_name: 'Ana López', password: 'secreto1', class_code: '4eso-neuma', board: 'esp32_s3', group_name: '4ºA' } })
  assert.equal(r.status, 200, JSON.stringify(r.data))
  ana = r.data.token
})

test('registro y login', async () => {
  assert.equal((await call('POST', '/api/auth/register', { body: { username: 'otro', full_name: 'X Y', password: 'secreto1', class_code: 'MAL' } })).status, 400)
  assert.equal((await call('POST', '/api/auth/register', { body: { username: 'ana', full_name: 'Ana', password: 'secreto1', class_code: '4ESO-NEUMA' } })).status, 400)
  assert.equal((await call('POST', '/api/auth/login', { body: { username: 'ana', password: 'mala' } })).status, 401)
  const ok = await call('POST', '/api/auth/login', { body: { username: 'ANA', password: 'secreto1' } })
  assert.equal(ok.data.user.board, 'esp32_s3')
  assert.equal((await call('GET', '/api/missions')).status, 401)
})

test('bloqueos y sin fugas de respuestas', async () => {
  const ms = (await call('GET', '/api/missions', { token: ana })).data
  assert.equal(ms.length, 15)
  assert.ok(!ms.some((m) => m.extra) && ms[14].trimestre === 3 && ms[5].trimestre === 1 && ms[3].id === 'm4' && ms[2].id === 'm3')
  assert.ok(ms[0].state.unlocked && !ms[1].state.unlocked)
  assert.equal((await call('GET', '/api/sections/m1s2', { token: ana })).status, 403)
  const r = await call('GET', '/api/sections/m1s1', { token: ana })
  assert.equal(r.status, 200)
  for (const k of ['"answer"', '"solution"', '"accept"', '"hints"']) assert.ok(!r.text.includes(k), k)
  assert.ok(!r.text.includes('estados[valvula] = estado'))
  const code = r.data.section.evaluation.items.find((i) => i.type === 'code')
  assert.ok(code.code_tests.tests.length > 0)
})

test('entrega: feedback, aprobado y desbloqueo', async () => {
  const bad = await call('POST', '/api/sections/m1s1/submit', { token: ana, body: { answers: { q1: 'b' } } })
  assert.equal(bad.status, 200)
  assert.ok(!bad.data.passed)
  assert.match(bad.data.items.find((i) => i.id === 'q1').message, /archivo de Python/)
  assert.match(bad.data.items.find((i) => i.id === 'c1').messages[0], /no has escrito/)
  // resultados de código manipulados (número de pruebas incorrecto) → no puntúan
  const p = await correctPayload('m1s1')
  const fake = await call('POST', '/api/sections/m1s1/submit', { token: ana, body: { answers: p.answers, code_results: { c1: { ok: true, tests: [{ passed: true }] } } } })
  assert.equal(fake.data.items.find((i) => i.id === 'c1').earned, 0)
  const good = await call('POST', '/api/sections/m1s1/submit', { token: ana, body: p })
  assert.ok(good.data.passed, JSON.stringify(good.data))
  assert.equal(good.data.score, 1)
  assert.equal(good.data.next_unlocked, 'm1s2')
  const again = await call('GET', '/api/sections/m1s1', { token: ana })
  assert.equal(again.data.last_submission.score, 1)
})

test('espera tras fallos seguidos', async () => {
  await call('GET', '/api/sections/m1s2', { token: ana })
  for (let i = 0; i < 3; i++) assert.equal((await call('POST', '/api/sections/m1s2/submit', { token: ana, body: { answers: {} } })).status, 200)
  const r = await call('POST', '/api/sections/m1s2/submit', { token: ana, body: { answers: {} } })
  assert.equal(r.status, 429)
  assert.match(r.data.detail, /intentos fallidos/)
})

test('fotos de los montajes: validación y bloqueo', async () => {
  // m1s2 pide foto: con la evaluación aprobada pero sin foto, m1s3 sigue bloqueada
  const st = (await call('GET', '/api/missions', { token: ana })).data[0].sections
  assert.ok(st.find((s) => s.id === 'm1s2').foto && !st.find((s) => s.id === 'm1s1').foto)
  assert.equal((await subirFoto(ana, 'm1s1')).status, 400)                       // esa sección no pide foto
  assert.equal((await subirFoto(ana, 'm1s2', 'data:text/plain;base64,QUJD')).status, 400)
  assert.equal((await subirFoto(ana, 'm1s2', 'data:image/jpeg;base64,QUJD')).status, 400)   // demasiado pequeña
  const grande = 'data:image/jpeg;base64,' + Buffer.alloc(2_600_000, 1).toString('base64')
  assert.equal((await subirFoto(ana, 'm1s2', grande)).status, 400)
  assert.equal((await subirFoto(ana, 'm5s2')).status, 403)                       // sección bloqueada
  assert.equal((await call('GET', '/api/sections/m1s2/photo', { token: ana })).status, 404)
})

test('profesor: panel, alertas de similitud, notas y CSV', async () => {
  const login = await call('POST', '/api/auth/login', { body: { username: 'profesor', password: 'profe123' } })
  assert.equal(login.status, 200)
  profe = login.data.token
  assert.equal((await call('GET', '/api/teacher/overview', { token: ana })).status, 403)

  // Quitar la espera de ana y completar la misión 1
  assert.ok((await call('POST', '/api/teacher/students/ana/reset-attempts', { token: profe, body: { section_id: 'm1s2' } })).data.ok)
  for (const sid of ['m1s2', 'm1s3', 'm1s4']) {
    await call('GET', `/api/sections/${sid}`, { token: ana })
    const r = await call('POST', `/api/sections/${sid}/submit`, { token: ana, body: await correctPayload(sid) })
    assert.ok(r.data.passed, sid)
    // Aprobada la evaluación, falta la foto del montaje: no se desbloquea la siguiente
    assert.ok(r.data.photo_pending, sid)
    assert.equal(r.data.next_unlocked, null)
    assert.ok(!r.data.mission_completed)
    const f = await subirFoto(ana, sid)
    assert.equal(f.status, 200, JSON.stringify(f.data))
    assert.equal(f.data.photo.status, 'pendiente')
    if (sid === 'm1s4') assert.ok(f.data.mission_completed)
  }
  assert.ok((await call('GET', '/api/missions', { token: ana })).data[1].state.unlocked)

  // Beto copia el código de ana cambiando nombres → alerta
  const beto = (await call('POST', '/api/auth/register', { body: { username: 'beto', full_name: 'Beto Ruiz', password: 'secreto1', class_code: '4ESO-NEUMA' } })).data.token
  for (const sid of ['m1s1', 'm1s2', 'm1s3', 'm1s4']) {
    await call('GET', `/api/sections/${sid}`, { token: beto })
    const p = await correctPayload(sid)
    if (sid === 'm1s4') p.answers.c1 = p.answers.c1.replaceAll('lecturas', 'datos').replaceAll('salida', 'res') + '\n# mío\n'
    await call('POST', `/api/sections/${sid}/submit`, { token: beto, body: p })
    if (section(sid).foto) await subirFoto(beto, sid)
  }
  const flags = (await call('GET', '/api/teacher/flags', { token: profe })).data
  assert.ok(flags.some((f) => /Similitud/.test(f.reason) && f.username === 'beto'), JSON.stringify(flags))

  const ov = (await call('GET', '/api/teacher/overview', { token: profe })).data
  assert.equal(ov.totals.students, 2)
  const anaRow = ov.students.find((s) => s.username === 'ana')
  assert.ok(anaRow.missions[0].completed)
  assert.equal(anaRow.photos.uploaded, 3)
  assert.ok(ov.totals.photos_pending >= 3)

  // Revisión de fotos: rechazar una quita la sección de «superadas» pero no bloquea lo siguiente
  const pend = (await call('GET', '/api/teacher/photos?status=pendiente', { token: profe })).data
  assert.ok(pend.some((f) => f.username === 'ana' && f.section_id === 'm1s3'))
  assert.equal((await call('GET', '/api/teacher/photos?status=pendiente', { token: ana })).status, 403)
  const img = await call('GET', '/api/teacher/photos/ana/m1s3', { token: profe })
  assert.equal(img.data.image, FOTO)
  const rej = await call('PUT', '/api/teacher/photos/ana/m1s3', { token: profe, body: { status: 'rechazada', comment: 'No se ve el cableado' } })
  assert.equal(rej.data.photo.status, 'rechazada')
  assert.equal((await call('PUT', '/api/teacher/photos/ana/m1s3', { token: profe, body: { status: 'otra' } })).status, 400)
  let m1 = (await call('GET', '/api/missions', { token: ana })).data[0]
  const s3 = m1.sections.find((s) => s.id === 'm1s3')
  assert.ok(!s3.state.passed && s3.state.score_passed && s3.state.photo.comment === 'No se ve el cableado')
  assert.ok(!m1.state.completed && m1.sections.find((s) => s.id === 'm1s4').state.unlocked)
  // el alumno vuelve a subirla y el profesor la acepta
  assert.equal((await subirFoto(ana, 'm1s3')).data.photo.status, 'pendiente')
  assert.ok((await call('PUT', '/api/teacher/photos/ana/m1s3', { token: profe, body: { status: 'aceptada' } })).data.ok)
  m1 = (await call('GET', '/api/missions', { token: ana })).data[0]
  assert.ok(m1.state.completed)
  assert.equal((await call('GET', '/api/sections/m1s3/photo', { token: ana })).data.image, FOTO)

  assert.ok((await call('POST', '/api/teacher/students/ana/unlock', { token: profe, body: { mission_id: 'm3' } })).data.ok)
  assert.ok((await call('GET', '/api/missions', { token: ana })).data[2].state.unlocked)
  assert.ok((await call('PUT', '/api/teacher/students/ana/grade', { token: profe, body: { mission_id: 'm3', grade: 9.5, notes: 'Control de acceso NFC excelente' } })).data.ok)

  const detail = (await call('GET', '/api/teacher/students/ana', { token: profe })).data
  assert.ok(detail.submissions.length >= 4)
  assert.equal(detail.missions[2].grade, 9.5)

  const csv = await call('GET', '/api/teacher/export.csv', { token: profe })
  assert.equal(csv.status, 200)
  assert.ok(csv.text.includes('ana') && csv.text.includes('9,5'))
  assert.ok(csv.text.includes('fotos subidas') && csv.text.includes('3/45'))

  const stats = (await call('GET', '/api/teacher/stats', { token: profe })).data
  assert.equal(stats.length, 61)
  assert.ok(stats[0].items[0].n >= 1)

  const sol = (await call('GET', '/api/teacher/sections/m3s1/solutions', { token: profe })).data
  assert.ok(sol.section.evaluation.items.some((i) => i.solution))

  // vista previa del profesor: no se guarda
  const pv = await call('POST', '/api/sections/m3s4/submit', { token: profe, body: await correctPayload('m3s4') })
  assert.ok(pv.data.preview && pv.data.passed)

  const dismiss = await call('POST', `/api/teacher/flags/${flags[0].id}/dismiss`, { token: profe })
  assert.ok(dismiss.data.ok)
  assert.ok((await call('DELETE', '/api/teacher/students/beto', { token: profe })).data.ok)
  assert.equal((await call('GET', '/api/teacher/overview', { token: profe })).data.totals.students, 1)
})

test('calendario de 45 semanas', async () => {
  const cal = (await call('GET', '/api/calendar', { token: ana })).data
  assert.equal(cal.weeks.length, 45)
  assert.ok(cal.weeks.every((w) => w.sessions.length === 3))
  assert.ok(cal.weeks.every((w) => !w.extra))
})

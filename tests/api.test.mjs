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
  assert.equal(ms.length, 11)
  assert.ok(!ms.some((m) => m.extra) && ms[10].trimestre === 3)
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
    if (sid === 'm1s4') assert.ok(r.data.mission_completed)
  }
  assert.ok((await call('GET', '/api/missions', { token: ana })).data[1].state.unlocked)

  // Beto copia el código de ana cambiando nombres → alerta
  const beto = (await call('POST', '/api/auth/register', { body: { username: 'beto', full_name: 'Beto Ruiz', password: 'secreto1', class_code: '4ESO-NEUMA' } })).data.token
  for (const sid of ['m1s1', 'm1s2', 'm1s3', 'm1s4']) {
    await call('GET', `/api/sections/${sid}`, { token: beto })
    const p = await correctPayload(sid)
    if (sid === 'm1s4') p.answers.c1 = p.answers.c1.replaceAll('lecturas', 'datos').replaceAll('salida', 'res') + '\n# mío\n'
    await call('POST', `/api/sections/${sid}/submit`, { token: beto, body: p })
  }
  const flags = (await call('GET', '/api/teacher/flags', { token: profe })).data
  assert.ok(flags.some((f) => /Similitud/.test(f.reason) && f.username === 'beto'), JSON.stringify(flags))

  const ov = (await call('GET', '/api/teacher/overview', { token: profe })).data
  assert.equal(ov.totals.students, 2)
  const anaRow = ov.students.find((s) => s.username === 'ana')
  assert.ok(anaRow.missions[0].completed)

  assert.ok((await call('POST', '/api/teacher/students/ana/unlock', { token: profe, body: { mission_id: 'm7' } })).data.ok)
  assert.ok((await call('GET', '/api/missions', { token: ana })).data[6].state.unlocked)
  assert.ok((await call('PUT', '/api/teacher/students/ana/grade', { token: profe, body: { mission_id: 'm7', grade: 9.5, notes: 'Prensa con finales de carrera excelente' } })).data.ok)

  const detail = (await call('GET', '/api/teacher/students/ana', { token: profe })).data
  assert.ok(detail.submissions.length >= 4)
  assert.equal(detail.missions[6].grade, 9.5)

  const csv = await call('GET', '/api/teacher/export.csv', { token: profe })
  assert.equal(csv.status, 200)
  assert.ok(csv.text.includes('ana') && csv.text.includes('9,5'))

  const stats = (await call('GET', '/api/teacher/stats', { token: profe })).data
  assert.equal(stats.length, 44)
  assert.ok(stats[0].items[0].n >= 1)

  const sol = (await call('GET', '/api/teacher/sections/m7s1/solutions', { token: profe })).data
  assert.ok(sol.section.evaluation.items.some((i) => i.solution))

  // vista previa del profesor: no se guarda
  const pv = await call('POST', '/api/sections/m7s4/submit', { token: profe, body: await correctPayload('m7s4') })
  assert.ok(pv.data.preview && pv.data.passed)

  const dismiss = await call('POST', `/api/teacher/flags/${flags[0].id}/dismiss`, { token: profe })
  assert.ok(dismiss.data.ok)
  assert.ok((await call('DELETE', '/api/teacher/students/beto', { token: profe })).data.ok)
  assert.equal((await call('GET', '/api/teacher/overview', { token: profe })).data.totals.students, 1)
})

test('calendario de 33 semanas', async () => {
  const cal = (await call('GET', '/api/calendar', { token: ana })).data
  assert.equal(cal.weeks.length, 33)
  assert.ok(cal.weeks.every((w) => w.sessions.length === 3))
  assert.ok(cal.weeks.every((w) => !w.extra))
})

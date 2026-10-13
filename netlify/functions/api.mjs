// API de TEC_IVJP_lab27 como una única Netlify Function (rutas /api/*), con datos en Netlify Blobs.
import crypto from 'node:crypto'
import { checkTiming, plagiarismReasons } from './lib/anticheat.mjs'
import { hashPassword, signToken, verifyPassword, verifyToken } from './lib/auth.mjs'
import { config as cfg } from './lib/config.mjs'
import { calendar, getMission, getSection, missionSummary, missions, publicSection } from './lib/course.mjs'
import { gradeSection, summaryMessage } from './lib/grading.mjs'
import { HARDWARE } from './lib/hardware.mjs'
import { getDb } from './lib/store.mjs'
import { needsPhoto, PHOTO_STATES, photoOk, photoUploaded, validatePhoto } from './lib/photos.mjs'

class HttpError extends Error {
  constructor(status, detail) { super(detail); this.status = status }
}
const json = (data, status = 200, headers = {}) =>
  new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...headers } })
const nowIso = () => new Date().toISOString()
const BOARDS = new Set(['pico_w', 'esp32_s3'])

// ------------------------------------------------------------------ datos
const emptyProgress = () => ({ sections: {}, overrides: [], grades: {} })

async function getUser(db, username) { return username ? db.get(`users/${username}`) : null }
async function getProgress(db, username) { return (await db.get(`progress/${username}`)) || emptyProgress() }

async function listStudents(db) {
  const keys = await db.list('users/')
  const users = await Promise.all(keys.map((k) => db.get(k)))
  return users.filter((u) => u && u.role === 'student')
    .sort((a, b) => (a.group_name || '').localeCompare(b.group_name || '') || a.full_name.localeCompare(b.full_name))
}

const userOut = (u) => ({ id: u.username, username: u.username, full_name: u.full_name, role: u.role, group_name: u.group_name || '', board: u.board || 'pico_w' })

function unlockState(user, prog) {
  const state = { missions: {}, sections: {} }
  let prevDone = true
  for (const m of missions) {
    const unlocked = user.role === 'teacher' || prevDone || prog.overrides.includes(m.id)
    const passedCount = m.sections.filter((s) => prog.sections[s.id]?.passed && photoOk(s, prog.sections[s.id])).length
    const done = passedCount === m.sections.length
    state.missions[m.id] = { unlocked, completed: done, passed_sections: passedCount, total_sections: m.sections.length }
    let prevOk = true
    for (const s of m.sections) {
      const p = prog.sections[s.id]
      state.sections[s.id] = {
        unlocked: unlocked && (prevOk || user.role === 'teacher'),
        passed: !!p?.passed && photoOk(s, p), score_passed: !!p?.passed, best_score: p?.best_score || 0, attempts: p?.attempts || 0,
        photo_required: needsPhoto(s), photo: needsPhoto(s) ? (p?.photo || null) : null,
      }
      prevOk = !!p?.passed && photoUploaded(s, p)
    }
    prevDone = done
  }
  return state
}

// ------------------------------------------------------------------ auth
async function currentUser(req, db) {
  const h = req.headers.get('authorization') || ''
  const payload = verifyToken(h.replace(/^Bearer\s+/i, ''))
  if (!payload) throw new HttpError(401, 'Sesión caducada o no válida')
  const user = await getUser(db, payload.sub)
  if (!user) throw new HttpError(401, 'Usuario no encontrado')
  return user
}

async function teacher(req, db) {
  const u = await currentUser(req, db)
  if (u.role !== 'teacher') throw new HttpError(403, 'Solo para el profesorado')
  return u
}

async function body(req) {
  try { return await req.json() } catch { return {} }
}

// ------------------------------------------------------------------ rutas
const routes = []
const route = (method, pattern, handler) => {
  const keys = []
  const re = new RegExp('^' + pattern.replace(/:(\w+)/g, (_, k) => { keys.push(k); return '([^/]+)' }) + '$')
  routes.push({ method, re, keys, handler })
}

route('GET', '/api/health', async () => json({ ok: true, missions: missions.length, storage: process.env.LOCAL_STORE_DIR ? 'local' : 'netlify-blobs' }))
route('GET', '/api/hardware', async () => json(HARDWARE))

route('POST', '/api/auth/register', async ({ req, db }) => {
  const d = await body(req)
  if (String(d.class_code || '').trim().toUpperCase() !== cfg.CLASS_CODE.toUpperCase()) throw new HttpError(400, 'Código de clase incorrecto. Pídeselo a tu profesor/a.')
  const username = String(d.username || '').trim().toLowerCase()
  if (!/^[a-z0-9._-]{3,32}$/.test(username)) throw new HttpError(400, 'El usuario debe tener 3-32 caracteres: letras sin tilde, números, punto, guion o guion bajo.')
  if (username === cfg.TEACHER_USERNAME) throw new HttpError(400, 'Ese nombre de usuario ya existe.')
  const fullName = String(d.full_name || '').trim()
  if (fullName.length < 2 || fullName.length > 100) throw new HttpError(400, 'Escribe tu nombre y apellidos.')
  if (String(d.password || '').length < 6) throw new HttpError(400, 'La contraseña debe tener al menos 6 caracteres.')
  if (await getUser(db, username)) throw new HttpError(400, 'Ese nombre de usuario ya existe.')
  const user = {
    username, full_name: fullName, role: 'student', group_name: String(d.group_name || '').trim().slice(0, 20),
    board: BOARDS.has(d.board) ? d.board : 'pico_w', password_hash: hashPassword(d.password), created_at: nowIso(),
  }
  await db.set(`users/${username}`, user)
  return json({ token: signToken(user), user: userOut(user) })
})

route('POST', '/api/auth/login', async ({ req, db }) => {
  const d = await body(req)
  const username = String(d.username || '').trim().toLowerCase()
  const password = String(d.password || '')
  let user = await getUser(db, username)
  // La cuenta del profesorado se crea (o se restablece) con TEACHER_PASSWORD
  if (username === cfg.TEACHER_USERNAME && cfg.TEACHER_PASSWORD && password === cfg.TEACHER_PASSWORD
      && (!user || !verifyPassword(password, user.password_hash))) {
    user = { ...(user || {}), username, full_name: cfg.TEACHER_FULLNAME, role: 'teacher', group_name: '', board: 'pico_w',
      password_hash: hashPassword(password), created_at: user?.created_at || nowIso() }
    await db.set(`users/${username}`, user)
  }
  if (!user || !verifyPassword(password, user.password_hash)) throw new HttpError(401, 'Usuario o contraseña incorrectos.')
  return json({ token: signToken(user), user: userOut(user) })
})

route('GET', '/api/auth/me', async ({ req, db }) => json(userOut(await currentUser(req, db))))
route('PATCH', '/api/auth/me', async ({ req, db }) => {
  const user = await currentUser(req, db)
  const d = await body(req)
  if (!BOARDS.has(d.board)) throw new HttpError(400, 'Placa no válida')
  user.board = d.board
  await db.set(`users/${user.username}`, user)
  return json(userOut(user))
})

route('GET', '/api/calendar', async ({ req, db }) => {
  await currentUser(req, db)
  return json({ start: cfg.COURSE_START_DATE, weeks: calendar(), hours_per_week: cfg.HOURS_PER_WEEK, regular_weeks: cfg.WEEKS })
})

route('GET', '/api/missions', async ({ req, db }) => {
  const user = await currentUser(req, db)
  const state = unlockState(user, await getProgress(db, user.username))
  return json(missions.map((m) => {
    const s = missionSummary(m)
    s.state = state.missions[m.id]
    s.sections.forEach((x) => { x.state = state.sections[x.id] })
    return s
  }))
})

route('GET', '/api/sections/:id', async ({ req, db, params }) => {
  const user = await currentUser(req, db)
  const { mission, section } = getSection(params.id)
  if (!section) throw new HttpError(404, 'Sección no encontrada')
  const prog = await getProgress(db, user.username)
  const state = unlockState(user, prog)
  if (!state.sections[section.id].unlocked) throw new HttpError(403, 'Sección bloqueada: supera antes las anteriores.')
  if (user.role === 'student' && !prog.sections[section.id]?.started_at) {
    prog.sections[section.id] = { ...(prog.sections[section.id] || {}), mission_id: mission.id, started_at: nowIso() }
    await db.set(`progress/${user.username}`, prog)
  }
  const last = await db.get(`last/${user.username}/${section.id}`)
  const idx = mission.sections.findIndex((s) => s.id === section.id)
  return json({
    mission: { id: mission.id, number: mission.number, title: mission.title, icon: mission.icon || '', passing_score: mission.passing_score },
    section: publicSection(section),
    state: state.sections[section.id],
    nav: { prev: mission.sections[idx - 1]?.id || null, next: mission.sections[idx + 1]?.id || null },
    last_submission: last,
  })
})

route('POST', '/api/sections/:id/submit', async ({ req, db, params }) => {
  const user = await currentUser(req, db)
  const { mission, section } = getSection(params.id)
  if (!section) throw new HttpError(404, 'Sección no encontrada')
  const prog = await getProgress(db, user.username)
  if (!unlockState(user, prog).sections[section.id].unlocked) throw new HttpError(403, 'Sección bloqueada.')
  const d = await body(req)
  const answers = d.answers && typeof d.answers === 'object' ? d.answers : {}
  const isStudent = user.role === 'student'
  const p = prog.sections[section.id] || { mission_id: mission.id }
  let elapsed = 0
  if (isStudent) {
    const t = checkTiming(p)
    if (!t.ok) throw new HttpError(429, t.msg)
    elapsed = t.elapsed
  }
  const result = gradeSection(section, answers, d.code_results || {})
  const passing = mission.passing_score
  const passed = result.score >= passing - 1e-9
  Object.assign(result, { passing_score: passing, passed, message: summaryMessage(result.score, passing, passed) })
  if (!isStudent) return json({ ...result, preview: true })

  // Plagio: compara con el código más reciente de los demás alumnos
  const codeItems = section.evaluation.items.filter((i) => i.type === 'code')
  const othersByItem = {}
  for (const item of codeItems) {
    const keys = (await db.list(`code/${section.id}/${item.id}/`)).filter((k) => !k.endsWith(`/${user.username}`))
    othersByItem[item.id] = (await Promise.all(keys.map(async (k) => ({ username: k.split('/').pop(), code: await db.get(k) })))).filter((o) => typeof o.code === 'string')
  }
  const reasons = plagiarismReasons(section, answers, othersByItem)

  const now = nowIso()
  p.attempts = (p.attempts || 0) + 1
  p.last_attempt_at = now
  if (passed) {
    p.failed_streak = 0
    if (!p.passed) { p.passed = true; p.passed_at = now }
  } else {
    p.failed_streak = (p.failed_streak || 0) + 1
  }
  p.best_score = Math.max(p.best_score || 0, result.score)
  p.last_items = result.items.map((i) => ({ id: i.id, earned: i.earned, points: i.points }))
  prog.sections[section.id] = p
  await db.set(`progress/${user.username}`, prog)

  const subId = `${now}-${crypto.randomBytes(3).toString('hex')}`
  const sub = { id: subId, username: user.username, mission_id: mission.id, section_id: section.id, answers, score: result.score,
    passed, feedback: result, elapsed_seconds: elapsed, flagged: reasons.length > 0, flag_reason: reasons.join('\n'), created_at: now }
  await db.set(`subs/${user.username}/${subId}`, sub)
  await db.set(`last/${user.username}/${section.id}`, { answers, score: result.score, passed, feedback: result, created_at: now })
  for (const item of codeItems) {
    if (typeof answers[item.id] === 'string' && answers[item.id].trim()) await db.set(`code/${section.id}/${item.id}/${user.username}`, answers[item.id])
  }
  if (reasons.length) {
    await db.set(`flags/${subId}`, { id: subId, student_id: user.username, username: user.username, student: user.full_name,
      section_id: section.id, score: result.score, reason: sub.flag_reason, elapsed_seconds: elapsed, created_at: now })
  }

  const newState = unlockState(user, prog)
  const idx = mission.sections.findIndex((s) => s.id === section.id)
  const photoPending = passed && !photoUploaded(section, p)
  if (photoPending) result.message += ' 📷 Para completar la sección, sube la foto de tu montaje.'
  return json({ ...result, attempts: p.attempts, mission_completed: newState.missions[mission.id].completed, photo_pending: photoPending,
    next_unlocked: passed && !photoPending && mission.sections[idx + 1] ? mission.sections[idx + 1].id : null })
})

// ------------------------------------------------------------------ fotos de los montajes
route('POST', '/api/sections/:id/photo', async ({ req, db, params }) => {
  const user = await currentUser(req, db)
  if (user.role !== 'student') throw new HttpError(400, 'Solo el alumnado sube fotos de sus montajes.')
  const { mission, section } = getSection(params.id)
  if (!section) throw new HttpError(404, 'Sección no encontrada')
  if (!needsPhoto(section)) throw new HttpError(400, 'Esta sección no pide foto.')
  const prog = await getProgress(db, user.username)
  if (!unlockState(user, prog).sections[section.id].unlocked) throw new HttpError(403, 'Sección bloqueada.')
  const d = await body(req)
  const v = validatePhoto(d.image)
  if (!v.ok) throw new HttpError(400, v.msg)
  const now = nowIso()
  await db.set(`photos/${user.username}/${section.id}`, { image: d.image, uploaded_at: now })
  const p = prog.sections[section.id] || { mission_id: mission.id }
  p.photo = { uploaded_at: now, status: 'pendiente', comment: '', bytes: v.bytes, note: String(d.note || '').slice(0, 300) }
  prog.sections[section.id] = p
  await db.set(`progress/${user.username}`, prog)
  const state = unlockState(user, prog)
  const idx = mission.sections.findIndex((s) => s.id === section.id)
  return json({ ok: true, photo: p.photo, state: state.sections[section.id], mission_completed: state.missions[mission.id].completed,
    next_unlocked: state.sections[section.id].passed && mission.sections[idx + 1] ? mission.sections[idx + 1].id : null })
})

route('GET', '/api/sections/:id/photo', async ({ req, db, params }) => {
  const user = await currentUser(req, db)
  const ph = await db.get(`photos/${user.username}/${params.id}`)
  if (!ph) throw new HttpError(404, 'Todavía no has subido foto.')
  return json(ph)
})

// ------------------------------------------------------------------ profesorado
async function flagCounts(db) {
  const keys = await db.list('flags/')
  const flags = (await Promise.all(keys.map((k) => db.get(k)))).filter(Boolean)
  const counts = {}
  for (const f of flags) counts[f.username] = (counts[f.username] || 0) + 1
  return { flags, counts }
}

function studentRow(u, prog, counts) {
  const state = unlockState(u, prog)
  let total = 0; let passedN = 0; let scoreSum = 0; let attempts = 0; let last = null
  const perMission = missions.map((m) => {
    const ms = state.missions[m.id]
    const scores = m.sections.map((s) => prog.sections[s.id]?.best_score || 0)
    total += ms.total_sections; passedN += ms.passed_sections; scoreSum += scores.reduce((a, b) => a + b, 0)
    return { mission_id: m.id, passed: ms.passed_sections, total: ms.total_sections, completed: ms.completed, unlocked: ms.unlocked,
      avg_score: Math.round((scores.reduce((a, b) => a + b, 0) / m.sections.length) * 1000) / 1000 }
  })
  for (const p of Object.values(prog.sections)) {
    attempts += p.attempts || 0
    if (p.last_attempt_at && (!last || p.last_attempt_at > last)) last = p.last_attempt_at
  }
  // La media «del curso» excluye las misiones de ampliación (extra)
  const core = missions.filter((m) => !m.extra)
  const coreSections = core.flatMap((m) => m.sections)
  const coreAvg = coreSections.reduce((a, s) => a + (prog.sections[s.id]?.best_score || 0), 0) / (coreSections.length || 1)
  const photos = { required: 0, uploaded: 0, pending: 0, accepted: 0, rejected: 0 }
  for (const m of missions) {
    for (const s of m.sections) {
      if (!needsPhoto(s)) continue
      photos.required++
      const ph = prog.sections[s.id]?.photo
      if (!ph) continue
      photos.uploaded++
      if (ph.status === 'pendiente') photos.pending++
      else if (ph.status === 'aceptada') photos.accepted++
      else if (ph.status === 'rechazada') photos.rejected++
    }
  }
  return { ...userOut(u), id: u.username, missions: perMission, passed_sections: passedN, total_sections: total, photos,
    avg_score: Math.round(coreAvg * 1000) / 1000, attempts, flags: counts[u.username] || 0, last_activity: last }
}

route('GET', '/api/teacher/info', async ({ req, db }) => {
  await teacher(req, db)
  return json({ class_code: cfg.CLASS_CODE, course_start: cfg.COURSE_START_DATE, min_seconds: cfg.MIN_SECONDS_BEFORE_SUBMIT,
    free_attempts: cfg.FREE_ATTEMPTS, plagiarism_threshold: cfg.PLAGIARISM_THRESHOLD,
    storage: process.env.LOCAL_STORE_DIR ? 'local' : 'netlify-blobs', grading: 'browser' })
})

route('GET', '/api/teacher/overview', async ({ req, db }) => {
  await teacher(req, db)
  const students = await listStudents(db)
  const progs = await Promise.all(students.map((u) => getProgress(db, u.username)))
  const { counts } = await flagCounts(db)
  const rows = students.map((u, i) => studentRow(u, progs[i], counts))
  const subs = rows.reduce((a, r) => a + r.attempts, 0)
  return json({
    students: rows,
    missions: missions.map((m, i) => ({ mission_id: m.id, number: m.number, title: m.title, icon: m.icon || '', extra: !!m.extra,
      completed: rows.filter((r) => r.missions[i].completed).length, students: rows.length })),
    totals: {
      students: rows.length,
      avg_progress: rows.length ? Math.round((rows.reduce((a, r) => a + r.passed_sections / r.total_sections, 0) / rows.length) * 1000) / 1000 : 0,
      flags: Object.values(counts).reduce((a, b) => a + b, 0),
      submissions: subs,
      photos_pending: rows.reduce((a, r) => a + r.photos.pending, 0),
    },
  })
})

async function student(db, username) {
  const u = await getUser(db, username)
  if (!u || u.role !== 'student') throw new HttpError(404, 'Alumno no encontrado')
  return u
}

route('GET', '/api/teacher/students/:id', async ({ req, db, params }) => {
  await teacher(req, db)
  const u = await student(db, params.id)
  const prog = await getProgress(db, u.username)
  const state = unlockState(u, prog)
  const keys = (await db.list(`subs/${u.username}/`)).reverse().slice(0, 100)
  const subs = (await Promise.all(keys.map((k) => db.get(k)))).filter(Boolean)
  return json({
    student: userOut(u),
    missions: missions.map((m) => ({
      id: m.id, number: m.number, title: m.title, icon: m.icon || '', ...state.missions[m.id],
      grade: prog.grades[m.id]?.grade ?? null, notes: prog.grades[m.id]?.notes || '',
      sections: m.sections.map((s) => {
        const p = prog.sections[s.id] || {}
        return { id: s.id, title: s.title, ...state.sections[s.id], started_at: p.started_at || null, passed_at: p.passed_at || null, failed_streak: p.failed_streak || 0 }
      }),
    })),
    submissions: subs.map((s) => ({ id: s.id, section_id: s.section_id, score: s.score, passed: s.passed, elapsed_seconds: s.elapsed_seconds,
      flagged: s.flagged, flag_reason: s.flag_reason, created_at: s.created_at, answers: s.answers, feedback: s.feedback })),
  })
})

route('GET', '/api/teacher/flags', async ({ req, db }) => {
  await teacher(req, db)
  const { flags } = await flagCounts(db)
  return json(flags.sort((a, b) => b.created_at.localeCompare(a.created_at)))
})

route('POST', '/api/teacher/flags/:id/dismiss', async ({ req, db, params }) => {
  await teacher(req, db)
  const f = await db.get(`flags/${params.id}`)
  if (!f) throw new HttpError(404, 'Entrega no encontrada')
  await db.delete(`flags/${params.id}`)
  const subKey = `subs/${f.username}/${params.id}`
  const sub = await db.get(subKey)
  if (sub) await db.set(subKey, { ...sub, flagged: false, flag_reason: (sub.flag_reason + '\n[Revisado por el profesor]').trim() })
  return json({ ok: true })
})

route('POST', '/api/teacher/students/:id/reset-attempts', async ({ req, db, params }) => {
  await teacher(req, db)
  const u = await student(db, params.id)
  const d = await body(req)
  const prog = await getProgress(db, u.username)
  if (prog.sections[d.section_id]) {
    prog.sections[d.section_id].failed_streak = 0
    prog.sections[d.section_id].last_attempt_at = null
    await db.set(`progress/${u.username}`, prog)
  }
  return json({ ok: true })
})

route('POST', '/api/teacher/students/:id/unlock', async ({ req, db, params }) => {
  await teacher(req, db)
  const u = await student(db, params.id)
  const d = await body(req)
  if (!getMission(d.mission_id)) throw new HttpError(400, 'Misión no válida')
  const prog = await getProgress(db, u.username)
  if (!prog.overrides.includes(d.mission_id)) prog.overrides.push(d.mission_id)
  await db.set(`progress/${u.username}`, prog)
  return json({ ok: true })
})

route('POST', '/api/teacher/unlock-all', async ({ req, db }) => {
  await teacher(req, db)
  const d = await body(req)
  if (!getMission(d.mission_id)) throw new HttpError(400, 'Misión no válida')
  let n = 0
  for (const u of await listStudents(db)) {
    const prog = await getProgress(db, u.username)
    if (!prog.overrides.includes(d.mission_id)) {
      prog.overrides.push(d.mission_id)
      await db.set(`progress/${u.username}`, prog)
      n++
    }
  }
  return json({ ok: true, unlocked: n })
})

route('PUT', '/api/teacher/students/:id/grade', async ({ req, db, params }) => {
  await teacher(req, db)
  const u = await student(db, params.id)
  const d = await body(req)
  if (!getMission(d.mission_id)) throw new HttpError(400, 'Misión no válida')
  const grade = d.grade === null || d.grade === undefined || d.grade === '' ? null : Number(d.grade)
  if (grade !== null && !(grade >= 0 && grade <= 10)) throw new HttpError(400, 'La nota debe estar entre 0 y 10')
  const prog = await getProgress(db, u.username)
  prog.grades[d.mission_id] = { grade, notes: String(d.notes || '').slice(0, 2000) }
  await db.set(`progress/${u.username}`, prog)
  return json({ ok: true })
})

route('POST', '/api/teacher/students/:id/password', async ({ req, db, params }) => {
  await teacher(req, db)
  const u = await student(db, params.id)
  const d = await body(req)
  if (String(d.password || '').length < 6) throw new HttpError(400, 'Mínimo 6 caracteres')
  u.password_hash = hashPassword(d.password)
  await db.set(`users/${u.username}`, u)
  return json({ ok: true })
})

route('DELETE', '/api/teacher/students/:id', async ({ req, db, params }) => {
  await teacher(req, db)
  const u = await student(db, params.id)
  const keys = [
    ...(await db.list(`subs/${u.username}/`)), ...(await db.list(`last/${u.username}/`)), ...(await db.list(`photos/${u.username}/`)),
    ...(await db.list('code/')).filter((k) => k.endsWith(`/${u.username}`)),
  ]
  const { flags } = await flagCounts(db)
  keys.push(...flags.filter((f) => f.username === u.username).map((f) => `flags/${f.id}`))
  await Promise.all(keys.map((k) => db.delete(k)))
  await db.delete(`progress/${u.username}`)
  await db.delete(`users/${u.username}`)
  return json({ ok: true })
})

route('GET', '/api/teacher/photos', async ({ req, db }) => {
  await teacher(req, db)
  const status = new URL(req.url).searchParams.get('status') || ''
  const out = []
  for (const u of await listStudents(db)) {
    const prog = await getProgress(db, u.username)
    for (const m of missions) {
      for (const s of m.sections) {
        const ph = prog.sections[s.id]?.photo
        if (!ph || (status && ph.status !== status)) continue
        out.push({ username: u.username, student: u.full_name, group_name: u.group_name || '', mission_id: m.id, mission_number: m.number,
          section_id: s.id, section_title: s.title, indicaciones: s.foto?.indicaciones || '', score_passed: !!prog.sections[s.id]?.passed, ...ph })
      }
    }
  }
  return json(out.sort((a, b) => b.uploaded_at.localeCompare(a.uploaded_at)))
})

route('GET', '/api/teacher/photos/:user/:section', async ({ req, db, params }) => {
  await teacher(req, db)
  const ph = await db.get(`photos/${params.user}/${params.section}`)
  if (!ph) throw new HttpError(404, 'Foto no encontrada')
  return json(ph)
})

route('PUT', '/api/teacher/photos/:user/:section', async ({ req, db, params }) => {
  await teacher(req, db)
  const u = await student(db, params.user)
  const d = await body(req)
  if (!PHOTO_STATES.has(d.status)) throw new HttpError(400, 'Estado no válido')
  const prog = await getProgress(db, u.username)
  const p = prog.sections[params.section]
  if (!p?.photo) throw new HttpError(404, 'Foto no encontrada')
  p.photo = { ...p.photo, status: d.status, comment: String(d.comment || '').slice(0, 500), reviewed_at: nowIso() }
  await db.set(`progress/${u.username}`, prog)
  return json({ ok: true, photo: p.photo })
})

route('GET', '/api/teacher/stats', async ({ req, db }) => {
  await teacher(req, db)
  const students = await listStudents(db)
  const progs = await Promise.all(students.map((u) => getProgress(db, u.username)))
  const out = []
  for (const m of missions) {
    for (const sec of m.sections) {
      const ps = progs.map((p) => p.sections[sec.id]).filter((p) => p && p.attempts)
      out.push({
        mission_id: m.id, section_id: sec.id, title: sec.title,
        students_started: ps.length, students_passed: ps.filter((p) => p.passed).length,
        avg_attempts: ps.length ? Math.round((ps.reduce((a, p) => a + p.attempts, 0) / ps.length) * 100) / 100 : 0,
        avg_best: ps.length ? Math.round((ps.reduce((a, p) => a + p.best_score, 0) / ps.length) * 1000) / 1000 : 0,
        items: sec.evaluation.items.map((item) => {
          const vals = ps.map((p) => (p.last_items || []).find((i) => i.id === item.id)).filter(Boolean).map((i) => (i.points ? i.earned / i.points : 0))
          return { id: item.id, type: item.type, label: String(item.question || item.prompt || item.text || '').slice(0, 90),
            avg: vals.length ? Math.round((vals.reduce((a, b) => a + b, 0) / vals.length) * 1000) / 1000 : null, n: vals.length }
        }),
      })
    }
  }
  return json(out)
})

route('GET', '/api/teacher/sections/:id/solutions', async ({ req, db, params }) => {
  await teacher(req, db)
  const { mission, section } = getSection(params.id)
  if (!section) throw new HttpError(404, 'Sección no encontrada')
  return json({ mission_id: mission.id, section })
})

route('GET', '/api/teacher/export.csv', async ({ req, db }) => {
  await teacher(req, db)
  const students = await listStudents(db)
  const progs = await Promise.all(students.map((u) => getProgress(db, u.username)))
  const { counts } = await flagCounts(db)
  const dec = (x) => x.toFixed(1).replace('.', ',')
  const esc = (v) => (/[;"\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : String(v))
  const header = ['usuario', 'nombre', 'grupo', 'placa']
  for (const m of missions) header.push(`M${m.number} secciones`, `M${m.number} nota auto (0-10)`, `M${m.number} nota profesor`)
  header.push('media auto curso (0-10)', 'intentos', 'alertas', 'fotos subidas', 'fotos aceptadas', 'fotos rechazadas')
  const lines = [header.map(esc).join(';')]
  students.forEach((u, i) => {
    const row = studentRow(u, progs[i], counts)
    const line = [u.username, u.full_name, u.group_name || '', u.board]
    row.missions.forEach((pm, j) => {
      const g = progs[i].grades[missions[j].id]?.grade
      line.push(`${pm.passed}/${pm.total}`, dec(pm.avg_score * 10), g == null ? '' : dec(g))
    })
    line.push(dec(row.avg_score * 10), row.attempts, row.flags, `${row.photos.uploaded}/${row.photos.required}`, row.photos.accepted, row.photos.rejected)
    lines.push(line.map(esc).join(';'))
  })
  return new Response('﻿' + lines.join('\r\n') + '\r\n', {
    headers: { 'content-type': 'text/csv; charset=utf-8', 'content-disposition': 'attachment; filename=notas_tec_ivjp_lab27.csv', 'cache-control': 'no-store' },
  })
})

// ------------------------------------------------------------------ entrada
export default async (req) => {
  const url = new URL(req.url)
  const path = url.pathname.replace(/\/+$/, '')
  try {
    const db = await getDb()
    for (const r of routes) {
      if (r.method !== req.method) continue
      const m = path.match(r.re)
      if (!m) continue
      const params = Object.fromEntries(r.keys.map((k, i) => [k, decodeURIComponent(m[i + 1])]))
      return await r.handler({ req, db, params })
    }
    return json({ detail: 'Ruta no encontrada' }, 404)
  } catch (e) {
    if (e instanceof HttpError) return json({ detail: e.message }, e.status)
    console.error(e)
    return json({ detail: 'Error interno del servidor: ' + e.message }, 500)
  }
}

export const config = { path: '/api/*' }

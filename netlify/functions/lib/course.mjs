import MISSIONS from './content.generated.mjs'
import { config } from './config.mjs'

export const missions = MISSIONS

export function getSection(sectionId) {
  for (const m of MISSIONS) {
    const s = m.sections.find((x) => x.id === sectionId)
    if (s) return { mission: m, section: s }
  }
  return { mission: null, section: null }
}

export const getMission = (id) => MISSIONS.find((m) => m.id === id) || null

const PRIVATE = new Set(['answer', 'accept', 'accept_regex', 'solution', 'explanation', 'hints', 'tests', 'required', 'forbidden', 'setup'])

export function publicItem(item) {
  const out = Object.fromEntries(Object.entries(item).filter(([k]) => !PRIVATE.has(k)))
  if (item.type === 'quiz') out.options = item.options.map((o) => ({ id: o.id, text: o.text }))
  if (item.type === 'fill_blank') out.blanks = (item.blanks || []).map((b) => ({ hint: b.hint || '' }))
  if (item.type === 'code') {
    out.tests = (item.tests || []).map((t) => t.desc || 'Prueba')
    // Las pruebas se ejecutan en el navegador (Pyodide). No contienen la solución.
    out.code_tests = { tests: item.tests || [], setup: item.setup || [] }
  }
  return out
}

export function publicSection(section) {
  const { evaluation, ...rest } = section
  return {
    ...structuredClone(rest),
    evaluation: { intro: evaluation.intro || '', items: evaluation.items.map(publicItem) },
  }
}

export function missionSummary(m) {
  return {
    id: m.id, number: m.number, title: m.title, subtitle: m.subtitle || '', icon: m.icon || '',
    weeks: m.weeks || [], hours: m.hours || 0, objectives: m.objectives || [], materials: m.materials || [],
    criteria: m.criteria || [], passing_score: m.passing_score, extra: !!m.extra, trimestre: m.trimestre || null,
    sections: m.sections.map((s) => ({ id: s.id, title: s.title, hours: s.hours || 0, kind: s.kind || 'lesson' })),
  }
}

function addDays(iso, days) {
  const d = new Date(iso + 'T12:00:00Z')
  d.setUTCDate(d.getUTCDate() + days)
  return d.toISOString().slice(0, 10)
}

export function calendar() {
  const maxWeek = Math.max(config.WEEKS, ...MISSIONS.flatMap((m) => (m.schedule || []).map((s) => s.week)))
  const weeks = []
  const skip = new Set(config.SKIP_WEEKS)
  // empezamos siempre en el lunes de la semana de inicio
  const first = new Date(config.COURSE_START_DATE + 'T12:00:00Z')
  let start = addDays(config.COURSE_START_DATE, -((first.getUTCDay() + 6) % 7))
  for (let w = 1; w <= maxWeek; w++) {
    // salta las semanas de vacaciones (comparando con el lunes de cada semana)
    while ([...skip].some((d) => d >= start && d <= addDays(start, 6))) start = addDays(start, 7)
    weeks.push({ week: w, start, end: addDays(start, 4), extra: w > config.WEEKS, sessions: [] })
    start = addDays(start, 7)
  }
  for (const m of MISSIONS) {
    for (const s of m.schedule || []) {
      weeks[s.week - 1]?.sessions.push({
        mission_id: m.id, mission_title: m.title, icon: m.icon || '', session: s.session, title: s.title, section_id: s.section || null,
      })
    }
  }
  weeks.forEach((w) => w.sessions.sort((a, b) => a.session - b.session))
  return weeks
}

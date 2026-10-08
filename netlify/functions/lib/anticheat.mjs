import { config } from './config.mjs'

const KEEP = new Set(`False None True and as assert async await break class continue def del elif else except finally for from
global if import in is lambda nonlocal not or pass raise return try while with yield print range len sum min max abs round int
float str list dict tuple set sorted enumerate zip map filter any all isinstance Pin ADC PWM machine time sleep sleep_ms network
neopixel WLAN value toggle on off read_u16 append math sqrt json dumps loads get`.split(/\s+/))

export function checkTiming(p, now = Date.now()) {
  if (!p?.started_at) return { ok: false, msg: 'Abre primero la sección y estudia la teoría.', elapsed: 0 }
  const elapsed = Math.floor((now - Date.parse(p.started_at)) / 1000)
  if ((p.attempts || 0) === 0 && elapsed < config.MIN_SECONDS_BEFORE_SUBMIT) {
    const wait = config.MIN_SECONDS_BEFORE_SUBMIT - elapsed
    return { ok: false, msg: `Dedica un poco más de tiempo a la sección antes de entregar (faltan ${wait} s).`, elapsed }
  }
  if ((p.failed_streak || 0) >= config.FREE_ATTEMPTS && p.last_attempt_at) {
    const extra = p.failed_streak - config.FREE_ATTEMPTS + 1
    const cooldown = config.COOLDOWN_BASE_SECONDS * extra
    const since = Math.floor((now - Date.parse(p.last_attempt_at)) / 1000)
    if (since < cooldown) {
      return {
        ok: false,
        msg: `Llevas ${p.failed_streak} intentos fallidos seguidos. Repasa la teoría: podrás reintentar en ${cooldown - since} s.`,
        elapsed,
      }
    }
  }
  return { ok: true, msg: '', elapsed }
}

/** Quita comentarios y renombra identificadores para comparar estructura, no nombres. */
export function normalizeCode(code) {
  const tokens = []
  const re = /("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'|#[^\n]*|[A-Za-z_]\w*|\d+(?:\.\d+)?|\*\*|\/\/|==|!=|<=|>=|\+=|-=|\S)/g
  for (const m of String(code || '').matchAll(re)) {
    const t = m[0]
    if (t.startsWith('#')) continue
    if (/^["']/.test(t)) tokens.push('STR')
    else if (/^[A-Za-z_]/.test(t)) tokens.push(KEEP.has(t) ? t : 'ID')
    else tokens.push(t)
  }
  return tokens
}

function shingles(tokens, k = 4) {
  const s = new Set()
  if (tokens.length < k) { s.add(tokens.join(' ')); return s }
  for (let i = 0; i <= tokens.length - k; i++) s.add(tokens.slice(i, i + k).join(' '))
  return s
}

export function similarity(a, b) {
  const sa = shingles(normalizeCode(a))
  const sb = shingles(normalizeCode(b))
  if (!sa.size || !sb.size) return 0
  let inter = 0
  for (const x of sa) if (sb.has(x)) inter++
  return inter / (sa.size + sb.size - inter)
}

/** others: [{username, code}] por ítem. Devuelve motivos de alerta. */
export function plagiarismReasons(section, answers, othersByItem) {
  const reasons = []
  for (const item of section.evaluation.items.filter((i) => i.type === 'code')) {
    const mine = answers[item.id] || ''
    const size = normalizeCode(mine).length
    if (size < 40) continue // en ejercicios cortos es normal que todos escriban casi lo mismo
    if (size >= 60 && item.solution && similarity(mine, item.solution) >= 0.999) {
      reasons.push(`[${item.id}] Idéntico estructuralmente a la solución de referencia`)
    }
    let best = 0
    let who = null
    for (const o of othersByItem[item.id] || []) {
      const s = similarity(mine, o.code)
      if (s > best) { best = s; who = o.username }
    }
    if (best >= config.PLAGIARISM_THRESHOLD) reasons.push(`[${item.id}] Similitud ${Math.round(best * 100)}% con la entrega de ${who}`)
  }
  return reasons
}

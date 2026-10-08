// Corrección. Test y huecos se corrigen aquí (las respuestas nunca salen del servidor).
// El código lo ejecuta el navegador con Pyodide; aquí se comprueban los resultados y se genera el feedback.

const ERROR_HINTS = {
  SyntaxError: 'Python no entiende alguna línea. Revisa que las instrucciones if/for/while/def terminen en \':\' y que paréntesis y comillas estén cerrados.',
  IndentationError: 'Problema de sangría. El código dentro de un if, for, while o def debe ir desplazado 4 espacios, y todas las líneas del mismo bloque igual de desplazadas.',
  TabError: 'Mezclas tabuladores y espacios. Usa solo espacios (4 por nivel).',
  NameError: 'Usas un nombre que no existe. Comprueba mayúsculas/minúsculas (Pin no es pin), que la variable esté creada antes de usarla y que hayas hecho el import necesario.',
  TypeError: 'Mezclas tipos que no encajan (por ejemplo, sumar texto y número) o llamas a una función con un número equivocado de parámetros.',
  ZeroDivisionError: 'Divides entre cero. Piensa qué pasa si la lista está vacía o si mínimo y máximo son iguales.',
  IndexError: 'Accedes a una posición de la lista que no existe. Recuerda que la primera es la 0 y la última len(lista)-1.',
  KeyError: 'Buscas en un diccionario una clave que no existe. Revisa cómo está escrita.',
  AttributeError: 'Llamas a un método que ese objeto no tiene. Revisa el nombre (read_u16, toggle, value…).',
  ValueError: 'Un valor tiene el tipo correcto pero un contenido no válido (por ejemplo int(\'hola\')).',
  ImportError: 'Ese módulo no está disponible aquí. Usa los de MicroPython: machine, time, network, neopixel, bluetooth…',
  ModuleNotFoundError: 'Ese módulo no está disponible aquí. Usa los de MicroPython: machine, time, network, neopixel, bluetooth…',
  SecurityError: 'Has usado algo que no está permitido en los ejercicios evaluados.',
  Timeout: 'Tu programa no termina: probablemente hay un bucle infinito (while True). En los ejercicios evaluados usa un for con un número fijo de repeticiones o una condición que llegue a cumplirse.',
  TimeoutError: 'Tu programa no termina: probablemente hay un bucle infinito (while True). Usa un for con un número fijo de repeticiones.',
  RecursionError: 'Una función se llama a sí misma sin parar.',
  MemoryError: 'Tu programa usa demasiada memoria. ¡En un microcontrolador la RAM es muy limitada!',
  Crash: 'El programa se detuvo de forma inesperada. Revisa que no haya bucles enormes.',
  Invalid: 'No se han recibido los resultados de las pruebas. Recarga la página y vuelve a entregar.',
}

export function explainError(err, hints = {}) {
  const kind = err?.type || 'Crash'
  const base = hints[kind] || ERROR_HINTS[kind] || 'Se ha producido un error al ejecutar tu código.'
  const where = err?.line ? ` (línea ${err.line})` : ''
  const msg = err?.message || ''
  return msg ? `${kind}${where}: ${msg}\n💡 ${base}` : `${kind}${where}\n💡 ${base}`
}

export function summaryMessage(score, passing, passed) {
  const pct = Math.round(score * 100)
  const need = Math.round(passing * 100)
  if (passed && pct === 100) return `¡Perfecto! ${pct}%. Sección superada. 🚀`
  if (passed) return `¡Superada con un ${pct}%! (mínimo ${need}%). Revisa los fallos para aprender de ellos.`
  if (pct >= need - 15) return `Casi: ${pct}% (necesitas ${need}%). Lee las pistas y vuelve a intentarlo.`
  return `${pct}% (necesitas ${need}%). Repasa la teoría y los ejemplos de esta sección antes de reintentar.`
}

const norm = (t) => String(t ?? '')
  .normalize('NFKD').replace(/[̀-ͯ]/g, '')
  .trim().toLowerCase().replace(/'/g, '"').replace(/\s+/g, '')

function gradeQuiz(item, answer) {
  const points = item.points ?? 1
  const correct = answer != null && String(answer) === String(item.answer)
  const fb = { id: item.id, type: 'quiz', points, earned: correct ? points : 0, correct }
  if (correct) fb.message = '✅ Correcto. ' + (item.explanation || '')
  else if (answer == null || answer === '') fb.message = 'Sin responder.'
  else {
    const chosen = item.options.find((o) => String(o.id) === String(answer))
    fb.message = '❌ ' + (chosen?.feedback || 'No es correcta. Vuelve a leer la teoría de esta sección.')
  }
  return fb
}

function gradeFill(item, answer) {
  const blanks = item.blanks || []
  const answers = Array.isArray(answer) ? answer : []
  const points = item.points ?? 1
  const per = points / Math.max(blanks.length, 1)
  let earned = 0
  const details = blanks.map((b, i) => {
    const given = answers[i] ?? ''
    let ok = (b.accept || []).some((acc) => norm(given) === norm(acc))
    if (!ok && b.accept_regex) ok = new RegExp(`^(?:${b.accept_regex})$`, 'i').test(String(given).trim())
    if (ok) earned += per
    return ok ? { ok: true, message: '✅' } : { ok: false, message: '❌ ' + (b.hint || 'Revisa este hueco.') }
  })
  earned = Math.round(earned * 100) / 100
  const correct = earned >= points - 1e-9
  return {
    id: item.id, type: 'fill_blank', points, earned, correct, blanks: details,
    message: correct ? '✅ Todo correcto. ' + (item.explanation || '') : 'Algunos huecos no son correctos.',
  }
}

function gradeCode(item, code, result) {
  const points = item.points ?? 3
  code = typeof code === 'string' ? code : ''
  const fb = { id: item.id, type: 'code', points, earned: 0, correct: false, tests: [], messages: [] }
  if (!code.trim() || code.trim() === (item.starter || '').trim()) {
    fb.messages.push('Todavía no has escrito tu solución.')
    return fb
  }
  for (const rule of item.forbidden || []) {
    if (new RegExp(rule.pattern).test(code)) {
      fb.messages.push('🚫 ' + rule.message)
      return fb
    }
  }
  const hints = item.hints || {}
  const tests = item.tests || []
  if (!result || typeof result !== 'object') {
    fb.messages.push(explainError({ type: 'Invalid' }))
    return fb
  }
  if (result.error) {
    fb.messages.push(explainError(result.error, hints))
    return fb
  }
  const got = Array.isArray(result.tests) ? result.tests : []
  if (got.length !== tests.length) {
    fb.messages.push(explainError({ type: 'Invalid' }))
    return fb
  }
  let passed = 0
  tests.forEach((t, i) => {
    const r = got[i] || {}
    const row = { desc: t.desc || 'Prueba', passed: r.passed === true }
    if (r.error) row.message = explainError(r.error, hints)
    else if (!row.passed && 'got' in r) row.message = `Tu código devuelve ${String(r.got).slice(0, 200)} y se esperaba ${String(r.expected).slice(0, 200)}.`
    if (row.passed) passed++
    fb.tests.push(row)
  })
  let ratio = tests.length ? passed / tests.length : 1
  const missing = (item.required || []).filter((r) => !new RegExp(r.pattern).test(code))
  for (const r of missing) fb.messages.push('⚠️ ' + r.message)
  if (missing.length) ratio *= 0.5
  if (ratio < 1 && hints.wrong_result && passed < tests.length) fb.messages.push('💡 ' + hints.wrong_result)
  if (result.stdout) fb.stdout = String(result.stdout).slice(-1500)
  fb.earned = Math.round(points * ratio * 100) / 100
  fb.correct = ratio >= 1 - 1e-9
  if (fb.correct) fb.messages.unshift('✅ Todas las pruebas superadas. ' + (item.explanation || ''))
  return fb
}

export function gradeSection(section, answers = {}, codeResults = {}) {
  const items = []
  let earned = 0
  let total = 0
  for (const item of section.evaluation.items) {
    let fb
    if (item.type === 'quiz') fb = gradeQuiz(item, answers[item.id])
    else if (item.type === 'fill_blank') fb = gradeFill(item, answers[item.id])
    else fb = gradeCode(item, answers[item.id], codeResults?.[item.id])
    items.push(fb)
    earned += fb.earned
    total += fb.points
  }
  return { score: total ? Math.round((earned / total) * 10000) / 10000 : 0, earned: Math.round(earned * 100) / 100, total, items }
}

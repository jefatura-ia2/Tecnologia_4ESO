// Cada solución de referencia, ejecutada en Pyodide (como en el navegador), debe sacar el 100 %.
import assert from 'node:assert/strict'
import { test } from 'node:test'
import missions from '../netlify/functions/lib/content.generated.mjs'
import { gradeSection } from '../netlify/functions/lib/grading.mjs'
import { runPython } from './helpers.mjs'

const items = missions.flatMap((m) => m.sections.flatMap((s) => s.evaluation.items.filter((i) => i.type === 'code').map((i) => [s.id, i])))

const grade = async (item, code) => {
  const result = await runPython({ code, tests: item.tests, setup: item.setup || [] })
  return gradeSection({ evaluation: { items: [item] } }, { [item.id]: code }, { [item.id]: result }).items[0]
}

test(`hay ${items.length} ejercicios de código`, () => assert.ok(items.length >= 45))

for (const [sid, item] of items) {
  test(`${sid}-${item.id}: la solución pasa en Pyodide`, async () => {
    const fb = await grade(item, item.solution)
    assert.ok(fb.correct, JSON.stringify(fb))
  })
  test(`${sid}-${item.id}: la plantilla no pasa`, async () => {
    const fb = await grade(item, item.starter || '')
    assert.ok(!fb.correct)
  })
}

test('el simulador bloquea imports peligrosos y bucles con sleep', async () => {
  const r1 = await runPython({ code: 'import os', tests: [] })
  assert.equal(r1.error.type, 'SecurityError')
  const r2 = await runPython({ code: 'import time\nwhile True:\n    time.sleep(1)', tests: [] })
  assert.equal(r2.error.type, 'TimeoutError')
  const r3 = await runPython({ code: 'import js', tests: [] })
  assert.equal(r3.error.type, 'SecurityError')
})

// Configuración leída de las variables de entorno de Netlify (Site settings → Environment variables).
const env = (k, d) => (process.env[k] ?? '').trim() || d

export const config = {
  get SECRET_KEY() { return env('SECRET_KEY', '') },
  get TEACHER_USERNAME() { return env('TEACHER_USERNAME', 'profesor').toLowerCase() },
  get TEACHER_PASSWORD() { return env('TEACHER_PASSWORD', '') },
  get TEACHER_FULLNAME() { return env('TEACHER_FULLNAME', 'Profesor/a') },
  get CLASS_CODE() { return env('CLASS_CODE', '4ESO-NEUMA') },
  get COURSE_START_DATE() {
    const v = env('COURSE_START_DATE', '2026-09-14')
    return /^\d{4}-\d{2}-\d{2}$/.test(v) ? v : '2026-09-14'
  },
  /** Lunes de las semanas sin clase (vacaciones), separados por comas: 2026-12-21,2026-12-28 */
  get SKIP_WEEKS() { return env('SKIP_WEEKS', '').split(',').map((x) => x.trim()).filter((x) => /^\d{4}-\d{2}-\d{2}$/.test(x)) },
  get WEEKS() { return parseInt(env('COURSE_WEEKS', '45'), 10) },
  get HOURS_PER_WEEK() { return parseInt(env('HOURS_PER_WEEK', '3'), 10) },
  get MIN_SECONDS_BEFORE_SUBMIT() { return parseInt(env('MIN_SECONDS_BEFORE_SUBMIT', '120'), 10) },
  get FREE_ATTEMPTS() { return parseInt(env('FREE_ATTEMPTS', '3'), 10) },
  get COOLDOWN_BASE_SECONDS() { return parseInt(env('COOLDOWN_BASE_SECONDS', '60'), 10) },
  get PLAGIARISM_THRESHOLD() { return parseFloat(env('PLAGIARISM_THRESHOLD', '0.92')) },
  get TOKEN_HOURS() { return parseInt(env('TOKEN_HOURS', '12'), 10) },
}

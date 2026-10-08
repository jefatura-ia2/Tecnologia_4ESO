import crypto from 'node:crypto'
import { config } from './config.mjs'

const ITER = 120_000

export function hashPassword(pw) {
  const salt = crypto.randomBytes(16).toString('hex')
  const digest = crypto.pbkdf2Sync(pw, salt, ITER, 32, 'sha256').toString('hex')
  return `pbkdf2$${ITER}$${salt}$${digest}`
}

export function verifyPassword(pw, stored) {
  const [, iter, salt, digest] = String(stored || '').split('$')
  if (!digest) return false
  const test = crypto.pbkdf2Sync(pw, salt, parseInt(iter, 10), 32, 'sha256')
  const ref = Buffer.from(digest, 'hex')
  return ref.length === test.length && crypto.timingSafeEqual(ref, test)
}

const b64 = (buf) => Buffer.from(buf).toString('base64url')

function secret() {
  const s = config.SECRET_KEY
  if (!s || s.length < 16) throw new Error('Falta la variable de entorno SECRET_KEY (mínimo 16 caracteres)')
  return s
}

export function signToken(user) {
  const header = b64(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))
  const payload = b64(JSON.stringify({
    sub: user.username, role: user.role, exp: Math.floor(Date.now() / 1000) + config.TOKEN_HOURS * 3600,
  }))
  const sig = crypto.createHmac('sha256', secret()).update(`${header}.${payload}`).digest('base64url')
  return `${header}.${payload}.${sig}`
}

export function verifyToken(token) {
  const parts = String(token || '').split('.')
  if (parts.length !== 3) return null
  const expected = crypto.createHmac('sha256', secret()).update(`${parts[0]}.${parts[1]}`).digest()
  const given = Buffer.from(parts[2], 'base64url')
  if (given.length !== expected.length || !crypto.timingSafeEqual(given, expected)) return null
  try {
    const payload = JSON.parse(Buffer.from(parts[1], 'base64url').toString())
    if (payload.exp < Date.now() / 1000) return null
    return payload
  } catch {
    return null
  }
}

// Almacenamiento: Netlify Blobs en producción; carpeta local para pruebas y desarrollo sin Netlify.
import fs from 'node:fs/promises'
import path from 'node:path'

class FileStore {
  constructor(dir) { this.dir = dir }
  file(key) { return path.join(this.dir, encodeURIComponent(key)) }
  async get(key) {
    try { return JSON.parse(await fs.readFile(this.file(key), 'utf8')) } catch { return null }
  }
  async set(key, value) {
    await fs.mkdir(this.dir, { recursive: true })
    await fs.writeFile(this.file(key), JSON.stringify(value))
  }
  async delete(key) { await fs.rm(this.file(key), { force: true }) }
  async list(prefix) {
    let names = []
    try { names = await fs.readdir(this.dir) } catch { return [] }
    return names.map(decodeURIComponent).filter((k) => k.startsWith(prefix)).sort()
  }
}

class BlobStore {
  constructor(store) { this.s = store }
  async get(key) { return (await this.s.get(key, { type: 'json' })) ?? null }
  async set(key, value) { await this.s.setJSON(key, value) }
  async delete(key) { await this.s.delete(key) }
  async list(prefix) {
    const keys = []
    for await (const page of this.s.list({ prefix, paginate: true })) keys.push(...page.blobs.map((b) => b.key))
    return keys.sort()
  }
}

let instance = null
export async function getDb() {
  if (instance) return instance
  if (process.env.LOCAL_STORE_DIR) {
    instance = new FileStore(process.env.LOCAL_STORE_DIR)
  } else {
    const { getStore } = await import('@netlify/blobs')
    instance = new BlobStore(getStore({ name: 'neumalab', consistency: 'strong' }))
  }
  return instance
}

export function resetDbForTests() { instance = null }

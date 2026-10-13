// Fotografías de los montajes prácticos.
// - La sección se considera superada cuando se aprueba la evaluación Y hay foto (no rechazada).
// - Para desbloquear la sección siguiente basta con haber subido una foto (aunque luego se rechace),
//   así una revisión tardía del profesor no bloquea al alumno a mitad de curso.
export const MAX_PHOTO_BYTES = 2_500_000
const DATA_URL = /^data:image\/(jpeg|png|webp);base64,([A-Za-z0-9+/=]+)$/

export const needsPhoto = (section) => !!section?.foto

export function photoOk(section, p) {
  return !needsPhoto(section) || (!!p?.photo && p.photo.status !== 'rechazada')
}

export function photoUploaded(section, p) {
  return !needsPhoto(section) || !!p?.photo
}

export function validatePhoto(image) {
  if (typeof image !== 'string') return { ok: false, msg: 'Falta la imagen.' }
  const m = image.match(DATA_URL)
  if (!m) return { ok: false, msg: 'Formato no válido: sube una foto JPG, PNG o WEBP.' }
  const bytes = Math.floor((m[2].length * 3) / 4)
  if (bytes > MAX_PHOTO_BYTES) return { ok: false, msg: 'La foto es demasiado grande (máximo 2,5 MB).' }
  if (bytes < 2000) return { ok: false, msg: 'La imagen está vacía o es demasiado pequeña.' }
  return { ok: true, bytes, type: m[1] }
}

export const PHOTO_STATES = new Set(['pendiente', 'aceptada', 'rechazada'])

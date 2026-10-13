// Reduce una foto del móvil (a menudo 4-12 MB) a un JPEG de ~1600 px antes de subirla.
export async function comprimirFoto(file, maxLado = 1600, calidad = 0.82) {
  if (!file || !file.type.startsWith('image/')) throw new Error('El archivo no es una imagen.')
  let bitmap
  try {
    bitmap = await createImageBitmap(file, { imageOrientation: 'from-image' })
  } catch {
    bitmap = await new Promise((resolve, reject) => {
      const img = new Image()
      img.onload = () => resolve(img)
      img.onerror = () => reject(new Error('No se puede leer la imagen (prueba con una foto JPG o PNG).'))
      img.src = URL.createObjectURL(file)
    })
  }
  const escala = Math.min(1, maxLado / Math.max(bitmap.width, bitmap.height))
  const w = Math.round(bitmap.width * escala)
  const h = Math.round(bitmap.height * escala)
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d')
  ctx.fillStyle = '#fff'
  ctx.fillRect(0, 0, w, h)
  ctx.drawImage(bitmap, 0, 0, w, h)
  let q = calidad
  let url = canvas.toDataURL('image/jpeg', q)
  while (url.length > 2_400_000 && q > 0.4) {
    q -= 0.12
    url = canvas.toDataURL('image/jpeg', q)
  }
  return { dataUrl: url, width: w, height: h, kb: Math.round((url.length * 3) / 4 / 1024) }
}

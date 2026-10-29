import { marked } from 'marked'
import hljs from 'highlight.js/lib/core'
import python from 'highlight.js/lib/languages/python'
import plaintext from 'highlight.js/lib/languages/plaintext'
import bash from 'highlight.js/lib/languages/bash'
import javascript from 'highlight.js/lib/languages/javascript'
import ini from 'highlight.js/lib/languages/ini'
import c from 'highlight.js/lib/languages/c'

hljs.registerLanguage('python', python)
hljs.registerLanguage('plaintext', plaintext)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('ini', ini)
hljs.registerLanguage('c', c)
// OpenSCAD tiene una sintaxis parecida a C: se resalta con esa gramática
hljs.registerAliases(['openscad', 'scad'], { languageName: 'c' })
hljs.registerAliases(['jsx', 'js'], { languageName: 'javascript' })

const renderer = new marked.Renderer()
renderer.code = ({ text, lang }) => {
  const language = lang && hljs.getLanguage(lang) ? lang : 'plaintext'
  const html = hljs.highlight(text, { language }).value
  return `<pre class="code"><code class="hljs language-${language}">${html}</code></pre>`
}

marked.setOptions({ renderer, gfm: true, breaks: false })

export function md(text) {
  return marked.parse(text || '')
}

export function mdInline(text) {
  return marked.parseInline(text || '')
}

export function highlight(code, language = 'python') {
  if (!hljs.getLanguage(language)) language = 'plaintext'
  return hljs.highlight(code || '', { language }).value
}

import { marked } from 'marked'
import hljs from 'highlight.js/lib/core'
import python from 'highlight.js/lib/languages/python'
import plaintext from 'highlight.js/lib/languages/plaintext'

hljs.registerLanguage('python', python)
hljs.registerLanguage('plaintext', plaintext)

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
  return hljs.highlight(code || '', { language }).value
}

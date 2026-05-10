import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight(str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (__) {}
    }
    return ''
  }
})

export function renderMarkdown(text) {
  const cleaned = (text || '')
    .split('\n')
    .reduce((acc, line) => {
      if (line.trim() === '' && acc.length && acc[acc.length - 1].trim() === '') {
        return acc
      }
      acc.push(line)
      return acc
    }, [])
    .join('\n')
  return md.render(cleaned)
}

export function copyToClipboard(text) {
  return navigator.clipboard.writeText(text)
}

export function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}
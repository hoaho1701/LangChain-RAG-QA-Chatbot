async function errorMessage(res) {
  const body = await res.json().catch(() => null)
  const detail = body?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((e) => e.msg).join('; ')
  // Upload failures come back as { added: [], failed: [{ name, reason }] }
  if (Array.isArray(detail?.failed)) return detail.failed.map((e) => `${e.name}: ${e.reason}`).join('; ')
  return res.statusText || `HTTP ${res.status}`
}

async function request(url, options) {
  const res = await fetch(url, options)
  if (!res.ok) {
    throw new Error(await errorMessage(res))
  }
  return res.json()
}

/** Backend status: { ready, indexed_files, tracing: { enabled, project } }. */
export async function getHealth() {
  const res = await fetch('/api/health')
  if (!res.ok) throw new Error(await errorMessage(res))
  return res.json()
}

/** Indexed sources: file paths ("./documents/a.pdf") or URLs. */
export async function listDocuments() {
  const body = await request('/api/documents')
  return body.documents
}

/** Uploads and indexes files. Resolves to { added: string[], failed: { name, reason }[] }. */
export async function uploadFiles(files) {
  const form = new FormData()
  for (const file of files) {
    form.append('files', file)
  }
  // No Content-Type: the browser sets it for FormData
  return request('/api/documents', { method: 'POST', body: form })
}

/** Fetches a web page and indexes its text. */
export function addUrl(url) {
  return request('/api/documents/url', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
}

/** Removes a source from the index, and its file from documents/ when it is a file. */
export function deleteDocument(source) {
  return request(`/api/documents?${new URLSearchParams({ source })}`, { method: 'DELETE' })
}

/** Deletes every uploaded file and the whole vector database. */
export function clearWorkspace() {
  return request('/api/workspace', { method: 'DELETE' })
}

/**
 * Streams an answer over SSE and reports it through callbacks:
 * onSources(sources), onToken(text), onError(message). Pass `signal` to cancel.
 */
export async function streamChat(question, history, { onSources, onToken, onError, signal }) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history }),
    signal,
  })
  if (!res.ok) throw new Error(await errorMessage(res))

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    // An event ends with a blank line, and one read() may hold several events or half of one
    let end
    while ((end = buffer.indexOf('\n\n')) !== -1) {
      const raw = buffer.slice(0, end)
      buffer = buffer.slice(end + 2)

      // Skip blocks without a data line, e.g. SSE comments (": keepalive") a proxy may insert
      const dataLine = raw.match(/^data: (.*)$/m)
      if (!dataLine) continue

      const event = raw.match(/^event: (.*)$/m)?.[1]
      const data = JSON.parse(dataLine[1])

      if (event === 'sources') onSources(data)
      else if (event === 'token') onToken(data)
      else if (event === 'error') onError(data.message)
    }
  }
}

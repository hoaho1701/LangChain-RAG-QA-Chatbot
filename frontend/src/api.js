async function errorMessage(res) {
  const body = await res.json().catch(() => null)
  const detail = body?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map((e) => e.msg).join('; ')
  return res.statusText || `HTTP ${res.status}`
}

export async function getHealth() {
  const res = await fetch('/api/health')
  if (!res.ok) throw new Error(await errorMessage(res))
  return res.json()
}

export async function streamChat(question, history, { onSources, onToken, onError, signal }) {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, history }),
    signal,
  })
  // Errors before the stream starts come back as a real status code (409, 422...)
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

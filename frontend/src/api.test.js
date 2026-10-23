import { afterEach, describe, expect, it, vi } from 'vitest'
import { addUrl, deleteDocument, listDocuments, streamChat, uploadFiles } from './api'

const encoder = new TextEncoder()

/** A fetch Response whose body arrives as the given chunks (strings or raw bytes), like a network stream. */
function streamResponse(chunks, init = { status: 200 }) {
  const body = new ReadableStream({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(typeof chunk === 'string' ? encoder.encode(chunk) : chunk)
      controller.close()
    },
  })
  return new Response(body, init)
}

function jsonResponse(body, status) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
}

function mockFetch(response) {
  const fetchMock = vi.fn().mockResolvedValue(response)
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

/** Runs streamChat and returns what the callbacks received, in order. */
async function collect(chunks) {
  mockFetch(streamResponse(chunks))
  const events = []
  await streamChat('q', [], {
    onSources: (s) => events.push(['sources', s]),
    onToken: (t) => events.push(['token', t]),
    onError: (m) => events.push(['error', m]),
  })
  return events
}

const sse = (event, data) => `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`

afterEach(() => vi.restoreAllMocks())

describe('streamChat', () => {
  it('reports sources, then tokens, in the order they arrive', async () => {
    const events = await collect([
      sse('sources', [{ file: 'a.pdf', page: 2 }]),
      sse('token', 'Hel'),
      sse('token', 'lo'),
      sse('done', {}),
    ])

    expect(events).toEqual([
      ['sources', [{ file: 'a.pdf', page: 2 }]],
      ['token', 'Hel'],
      ['token', 'lo'],
    ])
  })

  it('reassembles an event that arrives in pieces and splits events that arrive together', async () => {
    const whole = sse('token', 'first') + sse('token', 'second')
    const cut = whole.indexOf('second') - 5 // inside the second event's header

    const events = await collect([whole.slice(0, cut), whole.slice(cut)])

    expect(events).toEqual([
      ['token', 'first'],
      ['token', 'second'],
    ])
  })

  it('does not break a Vietnamese letter whose bytes arrive in two chunks', async () => {
    const bytes = encoder.encode(sse('token', 'đáp án'))
    const cut = bytes.indexOf(0xc4) + 1 // between the two bytes of "đ"

    const events = await collect([bytes.slice(0, cut), bytes.slice(cut)])

    expect(events).toEqual([['token', 'đáp án']])
  })

  it('ignores SSE comments such as a proxy keepalive', async () => {
    const events = await collect([': keepalive\n\n', sse('token', 'x')])

    expect(events).toEqual([['token', 'x']])
  })

  it('passes an error event to onError', async () => {
    const events = await collect([sse('token', 'a'), sse('error', { message: 'model is down' })])

    expect(events).toEqual([
      ['token', 'a'],
      ['error', 'model is down'],
    ])
  })

  it('rejects with the server message when the request itself fails', async () => {
    mockFetch(jsonResponse({ detail: 'No documents indexed. Upload documents first.' }, 409))

    await expect(streamChat('q', [], {})).rejects.toThrow('No documents indexed. Upload documents first.')
  })

  it('sends the question and the history as JSON', async () => {
    const fetchMock = mockFetch(streamResponse([]))
    const history = [{ role: 'user', content: 'hi' }]

    await streamChat('next', history, {})

    const [url, options] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/chat')
    expect(JSON.parse(options.body)).toEqual({ question: 'next', history })
  })
})

describe('error messages of the other calls', () => {
  it('uses the detail string of the server', async () => {
    mockFetch(jsonResponse({ detail: 'Unknown source.' }, 404))

    await expect(listDocuments()).rejects.toThrow('Unknown source.')
  })

  it('joins the messages of a validation error', async () => {
    mockFetch(jsonResponse({ detail: [{ msg: 'field required' }, { msg: 'too short' }] }, 422))

    await expect(listDocuments()).rejects.toThrow('field required; too short')
  })

  it('names each file that failed to upload, with its reason', async () => {
    mockFetch(jsonResponse({ detail: { added: [], failed: [{ name: 'a.exe', reason: 'unsupported' }] } }, 400))

    await expect(listDocuments()).rejects.toThrow('a.exe: unsupported')
  })

  it('falls back to the status text when the body is not JSON', async () => {
    mockFetch(new Response('<html>Bad gateway</html>', { status: 502, statusText: 'Bad Gateway' }))

    await expect(listDocuments()).rejects.toThrow('Bad Gateway')
  })
})

describe('requests', () => {
  it('uploads the files as form data and lets the browser set the content type', async () => {
    const fetchMock = mockFetch(jsonResponse({ added: ['a.txt'], failed: [] }, 200))
    const file = new File(['hello'], 'a.txt', { type: 'text/plain' })

    await uploadFiles([file])

    const [url, options] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/documents')
    expect(options.method).toBe('POST')
    expect(options.headers).toBeUndefined()
    expect(options.body.getAll('files')[0].name).toBe('a.txt')
  })

  it('escapes the source when deleting a document', async () => {
    const fetchMock = mockFetch(jsonResponse({}, 200))
    const source = './documents/a b&c.pdf'

    await deleteDocument(source)

    const [url, options] = fetchMock.mock.calls[0]
    expect(options.method).toBe('DELETE')
    expect(new URL(url, 'http://x').searchParams.get('source')).toBe(source)
  })

  it('posts the address as JSON when adding a URL', async () => {
    const fetchMock = mockFetch(jsonResponse({}, 200))

    await addUrl('https://example.com')

    const [url, options] = fetchMock.mock.calls[0]
    expect(url).toBe('/api/documents/url')
    expect(JSON.parse(options.body)).toEqual({ url: 'https://example.com' })
  })
})

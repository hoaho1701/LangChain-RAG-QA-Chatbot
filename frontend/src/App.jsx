import { useEffect, useState } from 'react'
import { getHealth, streamChat } from './api'
import Chat from './components/Chat'

const WELCOME = {
  id: 'welcome',
  role: 'assistant',
  content: 'Hello! Upload a PDF and ask me anything.',
  isWelcome: true,
}

export default function App() {
  const [messages, setMessages] = useState([WELCOME])
  // Only messages from this index on are sent to the LLM as history
  const [memoryStart, setMemoryStart] = useState(0)
  // null until the backend answers /api/health
  const [health, setHealth] = useState(null)
  const [busy, setBusy] = useState(false)

  // The backend accepts connections only after it has loaded its models, so retry until it does
  useEffect(() => {
    let cancelled = false

    async function waitForBackend() {
      while (!cancelled) {
        try {
          const h = await getHealth()
          if (!cancelled) setHealth(h)
          return
        } catch {
          await new Promise((resolve) => setTimeout(resolve, 2000))
        }
      }
    }

    waitForBackend()
    return () => {
      cancelled = true
    }
  }, [])

  function patchAssistant(id, makePatch) {
    setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, ...makePatch(m) } : m)))
  }

  async function send(question) {
    const history = messages
      .slice(memoryStart)
      .filter((m) => !m.isWelcome && !m.isError)
      .map(({ role, content }) => ({ role, content }))

    const assistantId = crypto.randomUUID()
    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: 'user', content: question },
      { id: assistantId, role: 'assistant', content: '', streaming: true },
    ])
    setBusy(true)

    try {
      await streamChat(question, history, {
        onSources: (sources) => patchAssistant(assistantId, () => ({ sources })),
        onToken: (token) => patchAssistant(assistantId, (m) => ({ content: m.content + token })),
        onError: (message) => patchAssistant(assistantId, () => ({ content: `Error: ${message}`, isError: true })),
      })
    } catch (e) {
      patchAssistant(assistantId, () => ({ content: `Error: ${e.message}`, isError: true }))
    } finally {
      patchAssistant(assistantId, () => ({ streaming: false }))
      setBusy(false)
    }
  }

  function clearChat() {
    setMessages([WELCOME])
    setMemoryStart(0)
  }

  if (!health) {
    return <div className="center">Connecting to server… loading models can take a minute.</div>
  }

  return (
    <div className="app">
      <header>
        <h1>RAG QA Chatbot Assistant 📚</h1>
        <button onClick={clearChat} disabled={busy}>
          Clear chat
        </button>
      </header>
      <Chat messages={messages} busy={busy} ready={health.ready} onSend={send} />
    </div>
  )
}

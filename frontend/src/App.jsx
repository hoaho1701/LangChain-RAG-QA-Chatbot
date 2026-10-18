import { useEffect, useState } from 'react'
import { addUrl, clearWorkspace, deleteDocument, getHealth, listDocuments, streamChat, uploadFiles } from './api'
import Chat from './components/Chat'
import Sidebar from './components/Sidebar'
import Toast from './components/Toast'
import { displayName } from './documents'

const WELCOME = {
  id: 'welcome',
  role: 'assistant',
  content: 'Hello! Upload documents or add a URL, then ask me anything.',
  isWelcome: true,
}

export default function App() {
  const [messages, setMessages] = useState([WELCOME])
  // Only messages from this index on are sent to the LLM as history
  const [memoryStart, setMemoryStart] = useState(0)
  // null until the backend answers /api/health
  const [health, setHealth] = useState(null)
  const [documents, setDocuments] = useState([])
  // { text, kind } shown by <Toast />, or null
  const [toast, setToast] = useState(null)
  const [busy, setBusy] = useState(false)

  async function refresh() {
    const [docs, healthData] = await Promise.all([listDocuments(), getHealth()])
    setDocuments(docs)
    setHealth(healthData)
  }

  // Retry until the backend has finished loading its models
  useEffect(() => {
    let cancelled = false

    async function waitForBackend() {
      while (!cancelled) {
        try {
          await refresh()
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

  function notify(text, kind = 'info') {
    setToast({ text, kind })
  }

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

  function handleClearChat() {
    clearChat()
    notify('Chat history cleared!', 'success')
  }

  // New documents start a fresh conversation for the LLM; old messages stay on screen
  async function documentsChanged() {
    setMemoryStart(messages.length)
    await refresh()
  }

  async function handleUpload(files) {
    try {
      const { added, failed } = await uploadFiles(files)
      if (failed.length === 0) {
        notify(`Added ${added.length} file(s)`, 'success')
      } else {
        const failedReason = failed.map((f) => `${f.name} (${f.reason})`).join(', ')
        notify(`Added ${added.length} file(s). Failed: ${failedReason}`, 'error')
      }
      await documentsChanged()
    } catch (e) {
      notify(e.message, 'error')
    }
  }

  async function handleAddUrl(url) {
    try {
      await addUrl(url)
      notify('URL added', 'success')
      await documentsChanged()
      return true
    } catch (e) {
      notify(e.message, 'error')
      return false
    }
  }

  async function handleDelete(source) {
    try {
      await deleteDocument(source)
      notify(`Removed ${displayName(source)}`, 'success')
      await documentsChanged()
    } catch (e) {
      notify(e.message, 'error')
    }
  }

  async function handleClearWorkspace() {
    try {
      await clearWorkspace()
      clearChat()
      notify('Workspace deleted', 'success')
      await refresh()
    } catch (e) {
      notify(e.message, 'error')
    }
  }

  if (!health) {
    return <div className="center">Connecting to server… loading models can take a minute.</div>
  }

  return (
    <div className="layout">
      <Sidebar
        documents={documents}
        health={health}
        busy={busy}
        onUpload={handleUpload}
        onAddUrl={handleAddUrl}
        onDelete={handleDelete}
        onClearChat={handleClearChat}
        onClearWorkspace={handleClearWorkspace}
      />
      <div className="app">
        <header>
          <h1>RAG QA Chatbot 📚</h1>
        </header>
        <Chat messages={messages} busy={busy} ready={health.ready} onSend={send} />
      </div>
      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  )
}

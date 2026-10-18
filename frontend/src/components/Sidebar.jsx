import { useState } from 'react'
import { displayName, isUrl } from '../documents'
import ConfirmDialog from './ConfirmDialog'

/**
 * Left column: file upload, URL ingestion, the indexed sources and settings.
 * The document actions (onUpload, onAddUrl, onDelete, onClearWorkspace) are handled by the parent.
 */
export default function Sidebar({ documents, busy, onUpload, onAddUrl, onDelete, onClearChat, onClearWorkspace }) {
  const [picked, setPicked] = useState([])
  // Bump to clear the file input
  const [inputKey, setInputKey] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [url, setUrl] = useState('')
  const [confirming, setConfirming] = useState(false)

  const locked = busy || uploading

  async function processFiles() {
    setUploading(true)
    try {
      await onUpload(picked)
      setPicked([])
      setInputKey((k) => k + 1)
    } finally {
      setUploading(false)
    }
  }

  async function submitUrl(e) {
    e.preventDefault()
    const link = url.trim()
    if (!link) return
    // Keep the text on failure so it can be corrected
    const added = await onAddUrl(link)
    if (added) setUrl('')
  }

  return (
    <aside className="sidebar">
      <h2>📚 RAG QA Chatbot</h2>
      <p className="muted">Upload files or paste a URL to start asking questions.</p>

      <input
        key={inputKey}
        type="file"
        multiple
        accept=".pdf,.txt,.md,.docx"
        disabled={locked}
        onChange={(e) => setPicked(Array.from(e.target.files))}
      />
      {picked.length > 0 && (
        <button onClick={processFiles} disabled={locked}>
          {uploading ? 'Processing…' : 'Process Documents'}
        </button>
      )}

      <h3>🌐 Add from URL</h3>
      <form onSubmit={submitUrl} className="row">
        <input
          type="text"
          placeholder="https://..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={locked}
        />
        <button type="submit" disabled={locked || !url.trim()}>
          Add URL
        </button>
      </form>

      {documents.length > 0 && (
        <>
          <h3>📂 Indexed Files</h3>
          <ul className="docs">
            {documents.map((source) => (
              <li key={source}>
                <span title={source}>
                  {isUrl(source) ? '🌐' : '📄'} {displayName(source)}
                </span>
                <button onClick={() => onDelete(source)} disabled={locked} aria-label={`Remove ${displayName(source)}`}>
                  ✕
                </button>
              </li>
            ))}
          </ul>
        </>
      )}

      <h3>Settings</h3>
      <button onClick={onClearChat} disabled={busy}>
        Clear Chat History
      </button>

      <button className="danger" onClick={() => setConfirming(true)} disabled={locked}>
        Clear Workspace
      </button>

      {confirming && (
        <ConfirmDialog
          message="Are you sure? This will delete all uploaded files and the database."
          confirmLabel="Yes, Delete All"
          onConfirm={async () => {
            setConfirming(false)
            await onClearWorkspace()
          }}
          onCancel={() => setConfirming(false)}
        />
      )}
    </aside>
  )
}

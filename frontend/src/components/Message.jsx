import ReactMarkdown from 'react-markdown'

export default function Message({ message }) {
  const { role, content, sources, streaming, isError } = message

  const className = `message ${role}${isError ? ' error' : ''}`
  const thinking = streaming && !content && !sources
  const isUser = role === 'user'

  return (
    <div className={className}>
      {thinking ? (
        <em>Thinking…</em>
      ) : isUser ? (
        <p className="plain">{content}</p>
      ) : (
        <div className={streaming ? 'cursor' : ''}>
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      )}

      {sources?.length > 0 && (
        <details className="sources">
          <summary>📄 Sources</summary>
          <ul>
            {sources.map((s) => (
              <li key={`${s.file}-${s.page}`}>
                <strong>{s.file}</strong> — page {s.page}
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  )
}

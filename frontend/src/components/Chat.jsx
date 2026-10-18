import { useEffect, useRef, useState } from 'react'
import Message from './Message'

export default function Chat({ messages, busy, ready, onSend }) {
  const [text, setText] = useState('')
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function submit() {
    const question = text.trim()
    if (!question || busy || !ready) return
    setText('')
    onSend(question)
  }

  function handleSubmit(e) {
    e.preventDefault()
    submit()
  }

  function handleKeyDown(e) {
    const isEnter = e.key === 'Enter'
    const withShift = e.shiftKey
    // While a Vietnamese IME (Telex/VNI) is composing, Enter only confirms the word.
    // Safari reports isComposing as false for that keystroke but sets keyCode 229.
    const composing = e.nativeEvent.isComposing || e.keyCode === 229

    if (isEnter && !withShift && !composing) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <main>
      <div className="messages">
        {messages.map((m) => (
          <Message key={m.id} message={m} />
        ))}
        <div ref={endRef} />
      </div>

      {!ready && <div className="banner">Please upload and process documents first.</div>}

      <form onSubmit={handleSubmit}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question…"
          rows={2}
          disabled={busy || !ready}
        />
        <button type="submit" disabled={busy || !ready || !text.trim()}>
          Send
        </button>
      </form>
    </main>
  )
}

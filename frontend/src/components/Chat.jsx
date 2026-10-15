// The message list + the input box.
//
// Props
//   messages : array of message objects (see Message.jsx)
//   busy     : true while an answer is being generated
//   ready    : false when no documents are indexed yet
//   onSend   : (question: string) => void   <- call it, the parent does the real work
//
// Local state: only what the input box needs (the text being typed).
//
// Done when
//   [ ] every message is rendered with <Message />
//   [ ] list scrolls to the newest message whenever `messages` changes
//   [ ] Enter sends, Shift+Enter inserts a new line
//   [ ] Enter does NOT send while composing Vietnamese (Telex/VNI)
//   [ ] empty / whitespace-only input is never sent; input clears after sending
//   [ ] textarea and Send button are disabled while `busy` or when not `ready`
//   [ ] not ready -> a banner says "Please upload and process documents first."
//
// Hints
//   - Auto-scroll: useRef on an empty <div> at the end of the list + useEffect that depends on
//     `messages` + element.scrollIntoView().
//   - Composing check: the keydown event has e.nativeEvent.isComposing.
//   - You must call e.preventDefault() on Enter, otherwise the textarea also inserts "\n".
//   - Put the submit logic in ONE function and call it from both the form and the key handler.

import Message from './Message'

export default function Chat({ messages, busy, ready, onSend }) {
  // TODO 1: state for the input text
  // TODO 2: ref + effect for auto-scroll
  // TODO 3: submit()
  // TODO 4: onKeyDown(e)
  // TODO 5: JSX -> messages list, banner, form (textarea + button)

  void busy
  void ready
  void onSend

  return (
    <main>
      {messages.map((m) => (
        <Message key={m.id} message={m} />
      ))}
    </main>
  )
}

// Renders ONE chat message bubble.
//
// Props
//   message = { id, role: 'user' | 'assistant', content, sources?, streaming?, isError? }
//   sources = [{ file, page, snippet }]
//
// Done when
//   [ ] user message shows plain text, line breaks preserved
//   [ ] assistant message renders markdown (bold, lists, code blocks)
//   [ ] streaming and nothing arrived yet (no content, no sources) -> shows "Thinking…"
//   [ ] streaming with content -> a blinking cursor after the last character
//   [ ] error message looks different from a normal one
//   [ ] sources exist -> collapsed "📄 Sources" list, one line per source: "<file> — page <N>"
//
// Hints
//   - Markdown: the `react-markdown` package, default export, text goes in as children.
//     Do NOT use dangerouslySetInnerHTML: the text comes from an LLM, so it is untrusted.
//   - Collapsible list: the native <details> + <summary> elements, no state needed.
//   - Different look per state: build the className string from role / isError / streaming,
//     then style the classes in index.css.
//   - List keys must be stable and unique: file + page works.

export default function Message({ message }) {
  // TODO 1: pull the fields you need out of `message`
  // TODO 2: decide when to show "Thinking…" (derive a boolean, no new state)
  // TODO 3: return the bubble: content (by role) + sources block

  return <div>{message.content}</div>
}

import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import * as api from './api'

vi.mock('./api')

/** A streamChat that answers with the given tokens. */
function answer(...tokens) {
  return async (question, history, { onSources, onToken }) => {
    onSources([{ file: 'book.pdf', page: 3 }])
    tokens.forEach(onToken)
  }
}

async function renderReady() {
  const user = userEvent.setup()
  render(<App />)
  await screen.findByPlaceholderText('Ask a question…')
  return user
}

async function ask(user, question) {
  await user.type(screen.getByPlaceholderText('Ask a question…'), `${question}{Enter}`)
}

beforeEach(() => {
  vi.resetAllMocks()
  api.getHealth.mockResolvedValue({ ready: true, indexed_files: 1 })
  api.listDocuments.mockResolvedValue(['./documents/book.pdf'])
})

describe('App start', () => {
  it('shows a waiting message until the backend answers, then the chat', async () => {
    let finishHealth
    api.getHealth.mockReturnValue(new Promise((resolve) => (finishHealth = resolve)))
    render(<App />)

    expect(screen.getByText(/Connecting to server/)).toBeInTheDocument()
    finishHealth({ ready: true, indexed_files: 1 })

    expect(await screen.findByPlaceholderText('Ask a question…')).toBeInTheDocument()
    expect(screen.getByText(/book\.pdf/)).toBeInTheDocument()
  })
})

describe('App chat', () => {
  it('shows the question, then the streamed answer with its sources', async () => {
    api.streamChat.mockImplementation(answer('The year ', 'was 2018.'))
    const user = await renderReady()

    await ask(user, 'In what year was BERT introduced?')

    expect(screen.getByText('In what year was BERT introduced?')).toBeInTheDocument()
    expect(await screen.findByText('The year was 2018.')).toBeInTheDocument()
    expect(screen.getByText('book.pdf')).toBeInTheDocument()
  })

  it('sends the earlier turns as history, without the welcome message', async () => {
    api.streamChat.mockImplementation(answer('first answer'))
    const user = await renderReady()

    await ask(user, 'first question')
    await screen.findByText('first answer')
    await ask(user, 'second question')

    await waitFor(() => expect(api.streamChat).toHaveBeenCalledTimes(2))
    expect(api.streamChat.mock.calls[0][1]).toEqual([])
    expect(api.streamChat.mock.calls[1][1]).toEqual([
      { role: 'user', content: 'first question' },
      { role: 'assistant', content: 'first answer' },
    ])
  })

  it('shows an error from the server in the chat and keeps it out of the history', async () => {
    api.streamChat.mockRejectedValueOnce(new Error('No documents indexed.'))
    const user = await renderReady()

    await ask(user, 'first question')
    expect(await screen.findByText(/No documents indexed\./)).toBeInTheDocument()

    api.streamChat.mockImplementation(answer('fine'))
    await ask(user, 'second question')

    await waitFor(() => expect(api.streamChat).toHaveBeenCalledTimes(2))
    expect(api.streamChat.mock.calls[1][1]).toEqual([{ role: 'user', content: 'first question' }])
  })

  it('shows an error that arrives inside the stream', async () => {
    api.streamChat.mockImplementation(async (question, history, { onError }) => onError('model is down'))
    const user = await renderReady()

    await ask(user, 'hello')

    expect(await screen.findByText('Error: model is down')).toBeInTheDocument()
  })

  it('forgets the conversation for the model after new documents are added, but keeps it on screen', async () => {
    api.streamChat.mockImplementation(answer('first answer'))
    api.uploadFiles.mockResolvedValue({ added: ['a.txt'], failed: [] })
    const user = await renderReady()
    await ask(user, 'first question')
    await screen.findByText('first answer')

    await user.upload(document.querySelector('input[type="file"]'), new File(['x'], 'a.txt'))
    await user.click(screen.getByRole('button', { name: 'Process Documents' }))
    await screen.findByText('Added 1 file(s)')
    await ask(user, 'second question')

    await waitFor(() => expect(api.streamChat).toHaveBeenCalledTimes(2))
    expect(api.streamChat.mock.calls[1][1]).toEqual([])
    expect(screen.getByText('first question')).toBeInTheDocument()
  })
})

describe('App documents', () => {
  it('reports the files that failed to upload', async () => {
    api.uploadFiles.mockResolvedValue({ added: [], failed: [{ name: 'empty.txt', reason: 'no text found' }] })
    const user = await renderReady()

    await user.upload(document.querySelector('input[type="file"]'), new File([''], 'empty.txt'))
    await user.click(screen.getByRole('button', { name: 'Process Documents' }))

    expect(await screen.findByText(/Failed: empty\.txt \(no text found\)/)).toBeInTheDocument()
  })

  it('removes a document and refreshes the list', async () => {
    api.deleteDocument.mockResolvedValue({})
    const user = await renderReady()
    api.listDocuments.mockResolvedValue([])

    await user.click(screen.getByRole('button', { name: 'Remove book.pdf' }))

    expect(api.deleteDocument).toHaveBeenCalledWith('./documents/book.pdf')
    expect(await screen.findByText('Removed book.pdf')).toBeInTheDocument()
    await waitFor(() => expect(screen.queryByText(/📄 book\.pdf/)).not.toBeInTheDocument())
  })

  it('empties the chat after the workspace is cleared', async () => {
    api.streamChat.mockImplementation(answer('an answer'))
    api.clearWorkspace.mockResolvedValue({})
    const user = await renderReady()
    await ask(user, 'a question')
    await screen.findByText('an answer')

    await user.click(screen.getByRole('button', { name: 'Clear Workspace' }))
    await user.click(screen.getByRole('button', { name: 'Yes, Delete All' }))

    expect(await screen.findByText('Workspace deleted')).toBeInTheDocument()
    expect(screen.queryByText('a question')).not.toBeInTheDocument()
  })
})

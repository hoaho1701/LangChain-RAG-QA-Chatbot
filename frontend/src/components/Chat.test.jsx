import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import Chat from './Chat'

const messages = [{ id: '1', role: 'assistant', content: 'Hello!' }]

function setup(props = {}) {
  const onSend = vi.fn()
  render(<Chat messages={messages} busy={false} ready={true} onSend={onSend} {...props} />)
  return { onSend, box: screen.getByPlaceholderText('Ask a question…') }
}

describe('Chat', () => {
  it('sends the trimmed question on Enter and clears the box', async () => {
    const user = userEvent.setup()
    const { onSend, box } = setup()

    await user.type(box, '  In what year was BERT introduced?  {Enter}')

    expect(onSend).toHaveBeenCalledWith('In what year was BERT introduced?')
    expect(box).toHaveValue('')
  })

  it('does not send on Shift+Enter, which adds a new line', async () => {
    const user = userEvent.setup()
    const { onSend, box } = setup()

    await user.type(box, 'line one{Shift>}{Enter}{/Shift}line two')

    expect(onSend).not.toHaveBeenCalled()
    expect(box).toHaveValue('line one\nline two')
  })

  it('does not send while an input method (Telex, VNI) is composing a word', () => {
    const { onSend, box } = setup()
    fireEvent.change(box, { target: { value: 'xin chào' } })

    fireEvent.keyDown(box, { key: 'Enter', isComposing: true })
    fireEvent.keyDown(box, { key: 'Enter', keyCode: 229 }) // Safari reports composition like this

    expect(onSend).not.toHaveBeenCalled()
  })

  it('does not send a question that is only spaces', async () => {
    const user = userEvent.setup()
    const { onSend, box } = setup()

    await user.type(box, '   {Enter}')

    expect(onSend).not.toHaveBeenCalled()
  })

  it('sends with the Send button too', async () => {
    const user = userEvent.setup()
    const { onSend, box } = setup()

    await user.type(box, 'hello')
    await user.click(screen.getByRole('button', { name: 'Send' }))

    expect(onSend).toHaveBeenCalledWith('hello')
  })

  it('locks the input while an answer is being written', () => {
    const { box } = setup({ busy: true })

    expect(box).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled()
  })

  it('asks for documents first when the backend has none indexed', () => {
    const { box } = setup({ ready: false })

    expect(screen.getByText('Please upload and process documents first.')).toBeInTheDocument()
    expect(box).toBeDisabled()
  })
})

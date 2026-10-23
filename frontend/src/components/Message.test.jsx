import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import Message from './Message'

describe('Message', () => {
  it('shows the text of a user message as plain text, not as Markdown', () => {
    render(<Message message={{ role: 'user', content: '**not bold**' }} />)

    expect(screen.getByText('**not bold**')).toBeInTheDocument()
  })

  it('renders the Markdown of an assistant message', () => {
    render(<Message message={{ role: 'assistant', content: 'The answer is **2018**.' }} />)

    expect(screen.getByText('2018').tagName).toBe('STRONG')
  })

  it('lists the sources with file and page', () => {
    const sources = [
      { file: 'book.pdf', page: 40 },
      { file: 'notes.txt', page: 1 },
    ]
    render(<Message message={{ role: 'assistant', content: 'Answer', sources }} />)

    expect(screen.getByText('book.pdf')).toBeInTheDocument()
    expect(screen.getByText(/page 40/)).toBeInTheDocument()
    expect(screen.getByText('notes.txt')).toBeInTheDocument()
  })

  it('has no sources section when there are none', () => {
    render(<Message message={{ role: 'assistant', content: 'Answer', sources: [] }} />)

    expect(screen.queryByText(/Sources/)).not.toBeInTheDocument()
  })

  it('says it is thinking until the first text or source arrives', () => {
    const { rerender } = render(<Message message={{ role: 'assistant', content: '', streaming: true }} />)
    expect(screen.getByText('Thinking…')).toBeInTheDocument()

    rerender(<Message message={{ role: 'assistant', content: 'Hel', streaming: true }} />)
    expect(screen.queryByText('Thinking…')).not.toBeInTheDocument()
  })

  it('marks an error message so it can be styled', () => {
    const { container } = render(<Message message={{ role: 'assistant', content: 'Error: x', isError: true }} />)

    expect(container.firstChild).toHaveClass('error')
  })
})

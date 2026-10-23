import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import Sidebar from './Sidebar'

function setup(props = {}) {
  const handlers = {
    onUpload: vi.fn().mockResolvedValue(undefined),
    onAddUrl: vi.fn().mockResolvedValue(true),
    onDelete: vi.fn(),
    onClearChat: vi.fn(),
    onClearWorkspace: vi.fn().mockResolvedValue(undefined),
  }
  render(<Sidebar documents={[]} busy={false} {...handlers} {...props} />)
  return { ...handlers, user: userEvent.setup() }
}

describe('Sidebar documents', () => {
  it('lists each indexed source by its short name', () => {
    setup({ documents: ['./documents/book.pdf', 'https://example.com/page'] })

    expect(screen.getByText(/book\.pdf/)).toBeInTheDocument()
    expect(screen.queryByText('./documents/book.pdf')).not.toBeInTheDocument()
    expect(screen.getByText(/https:\/\/example\.com\/page/)).toBeInTheDocument()
  })

  it('removes the source of the clicked entry', async () => {
    const { user, onDelete } = setup({ documents: ['./documents/a.pdf', './documents/b.pdf'] })

    await user.click(screen.getByRole('button', { name: 'Remove b.pdf' }))

    expect(onDelete).toHaveBeenCalledWith('./documents/b.pdf')
  })

  it('shows no list when nothing is indexed', () => {
    setup()

    expect(screen.queryByText(/Indexed Files/)).not.toBeInTheDocument()
  })
})

describe('Sidebar upload', () => {
  it('offers to process the picked files and hands them to the parent', async () => {
    const { user, onUpload } = setup()
    const file = new File(['x'], 'a.txt', { type: 'text/plain' })
    expect(screen.queryByRole('button', { name: 'Process Documents' })).not.toBeInTheDocument()

    await user.upload(document.querySelector('input[type="file"]'), file)
    await user.click(screen.getByRole('button', { name: 'Process Documents' }))

    expect(onUpload).toHaveBeenCalledWith([file])
  })
})

describe('Sidebar URL', () => {
  it('adds the address and clears the box when it worked', async () => {
    const { user, onAddUrl } = setup()
    const box = screen.getByPlaceholderText('https://...')

    await user.type(box, ' https://example.com ')
    await user.click(screen.getByRole('button', { name: 'Add URL' }))

    expect(onAddUrl).toHaveBeenCalledWith('https://example.com')
    expect(box).toHaveValue('')
  })

  it('keeps the text when adding failed, so it can be corrected', async () => {
    const { user } = setup({ onAddUrl: vi.fn().mockResolvedValue(false) })
    const box = screen.getByPlaceholderText('https://...')

    await user.type(box, 'https://typo')
    await user.click(screen.getByRole('button', { name: 'Add URL' }))

    expect(box).toHaveValue('https://typo')
  })

  it('does not add an empty address', () => {
    setup()

    expect(screen.getByRole('button', { name: 'Add URL' })).toBeDisabled()
  })
})

describe('Sidebar clear workspace', () => {
  it('asks for confirmation and does nothing when cancelled', async () => {
    const { user, onClearWorkspace } = setup()

    await user.click(screen.getByRole('button', { name: 'Clear Workspace' }))
    expect(screen.getByRole('dialog')).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Cancel' }))

    expect(onClearWorkspace).not.toHaveBeenCalled()
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('clears the workspace only after the confirmation', async () => {
    const { user, onClearWorkspace } = setup()

    await user.click(screen.getByRole('button', { name: 'Clear Workspace' }))
    await user.click(screen.getByRole('button', { name: 'Yes, Delete All' }))

    expect(onClearWorkspace).toHaveBeenCalledTimes(1)
  })

  it('locks the document buttons while an answer is being written', () => {
    setup({ busy: true, documents: ['./documents/a.pdf'] })

    expect(screen.getByRole('button', { name: 'Clear Workspace' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Remove a.pdf' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Clear Chat History' })).toBeDisabled()
  })
})

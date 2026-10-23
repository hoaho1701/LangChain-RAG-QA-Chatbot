import { describe, expect, it } from 'vitest'
import { displayName, isUrl } from './documents'

describe('isUrl', () => {
  it('tells a web address from a file path', () => {
    expect(isUrl('https://example.com/page')).toBe(true)
    expect(isUrl('./documents/book.pdf')).toBe(false)
  })
})

describe('displayName', () => {
  it('shows only the file name of a path', () => {
    expect(displayName('./documents/1. Hands-On Large Language Models.pdf')).toBe(
      '1. Hands-On Large Language Models.pdf',
    )
  })

  it('keeps a URL whole, even though it contains slashes', () => {
    expect(displayName('https://example.com/a/b')).toBe('https://example.com/a/b')
  })
})

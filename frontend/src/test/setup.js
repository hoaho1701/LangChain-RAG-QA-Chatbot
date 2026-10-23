import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

// Tests do not use vitest globals, so Testing Library cannot register its own cleanup
afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

// jsdom has no layout engine: Chat scrolls to the newest message with this call
Element.prototype.scrollIntoView = vi.fn()

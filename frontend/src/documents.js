// A source is either a file path ("./documents/book.pdf") or a URL ("https://...")
export const isUrl = (source) => source.includes('://')

export const displayName = (source) => (isUrl(source) ? source : source.split('/').pop())

import { describe, it, expect } from 'vitest'
import { formatDate, unescape, getImageUrl } from './parse'

describe('formatDate', () => {
  it('returns empty string for falsy or invalid input', () => {
    expect(formatDate('')).toBe('')
    expect(formatDate(null)).toBe('')
    expect(formatDate('not-a-date')).toBe('')
  })

  it('formats to KST yyyy-mm-dd (UTC+9)', () => {
    // 2024-01-15T00:00:00Z -> 2024-01-15 09:00:00 KST
    expect(formatDate('2024-01-15T00:00:00Z', 'yyyy-mm-dd')).toBe('2024-01-15 09:00:00')
  })

  it('formats to digit-only num form in KST', () => {
    expect(formatDate('2024-01-15T00:00:00Z', 'num')).toBe('20240115 090000')
  })

  it('appends Z when missing then parses as UTC', () => {
    expect(formatDate('2024-01-15T00:00:00', 'yyyy-mm-dd')).toBe('2024-01-15 09:00:00')
  })

  it('produces a non-empty localized string for the default form', () => {
    const out = formatDate('2024-01-15T00:00:00Z')
    expect(typeof out).toBe('string')
    expect(out).toContain('2024')
  })
})

describe('unescape', () => {
  it('returns plain strings unchanged', () => {
    expect(unescape('hello world')).toBe('hello world')
  })
})

describe('getImageUrl', () => {
  it('builds an asset URL containing the file name', () => {
    expect(getImageUrl('icon--close.svg')).toContain('icon--close.svg')
  })
})

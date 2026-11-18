import { describe, expect, it } from 'vitest'
import {
  dateBlock,
  formatDate,
  formatPeso,
  firstNameOf,
  formatTons,
  greetingFor,
  initialsOf,
  shortIdentifier,
} from './formatting'

describe('formatting', () => {
  it('formats date-only values without timezone shifts', () => {
    expect(formatDate('2026-11-16')).toBe('Nov 16, 2026')
    expect(formatDate('2026-01-01')).toBe('Jan 1, 2026')
    expect(formatDate(null)).toBe('—')
  })

  it('builds calendar tile parts', () => {
    expect(dateBlock('2026-11-16')).toEqual({ month: 'NOV', day: '16' })
  })

  it('formats tons and pesos', () => {
    expect(formatTons(48.5)).toBe('48.5 t')
    expect(formatTons('25')).toBe('25 t')
    expect(formatPeso(14500)).toBe('₱14,500.00')
  })

  it('makes initials and short ids', () => {
    expect(initialsOf('Juan Santos')).toBe('JS')
    expect(initialsOf('Madonna')).toBe('M')
    expect(initialsOf('Maria Clara de la Cruz')).toBe('MC')
    expect(initialsOf('')).toBe('?')
    expect(shortIdentifier('0123456789abcdef')).toBe('01234567')
    expect(shortIdentifier(null)).toBe('—')
  })
})

describe('greetings', () => {
  it('greets by time of day and takes the first name', () => {
    expect(greetingFor(7)).toBe('Good morning')
    expect(greetingFor(12)).toBe('Good afternoon')
    expect(greetingFor(18)).toBe('Good evening')
    expect(firstNameOf('Juan Santos')).toBe('Juan')
    expect(firstNameOf('')).toBe('')
  })
})

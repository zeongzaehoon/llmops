import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Badge from './Badge'

describe('Badge', () => {
  it('renders its children', () => {
    render(<Badge>LIVE</Badge>)
    expect(screen.getByText('LIVE')).toBeInTheDocument()
  })

  it('applies a custom className', () => {
    render(<Badge className="extra">Tag</Badge>)
    expect(screen.getByText('Tag').className).toContain('extra')
  })
})

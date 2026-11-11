import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import Tabs from './Tabs'

const items = [
  { key: 'a', label: 'Alpha' },
  { key: 'b', label: 'Beta', count: 3 }
]

describe('Tabs', () => {
  it('renders labels and the optional count', () => {
    render(<Tabs items={items} activeKey="a" onChange={() => {}} />)
    expect(screen.getByText('Alpha')).toBeInTheDocument()
    expect(screen.getByText('Beta')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
  })

  it('calls onChange with the clicked tab key', () => {
    const onChange = vi.fn()
    render(<Tabs items={items} activeKey="a" onChange={onChange} />)
    fireEvent.click(screen.getByText('Beta'))
    expect(onChange).toHaveBeenCalledWith('b')
  })
})

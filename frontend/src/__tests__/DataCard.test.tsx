import { render, screen } from '@testing-library/react'
import DataCard from '@/components/DataCard'

describe('DataCard', () => {
  it('renders label and value', () => {
    render(<DataCard icon="📊" label="反馈总数" value={42} />)
    expect(screen.getByText('反馈总数')).toBeInTheDocument()
    expect(screen.getByText('42')).toBeInTheDocument()
  })

  it('renders with trend indicator', () => {
    render(<DataCard icon="📈" label="增长" value="15%" trend={{ value: 12, up: true }} />)
    expect(screen.getByText('↑ 12%')).toBeInTheDocument()
  })

  it('renders downward trend', () => {
    render(<DataCard icon="📉" label="下降" value="5%" trend={{ value: 3, up: false }} />)
    expect(screen.getByText('↓ 3%')).toBeInTheDocument()
  })
})

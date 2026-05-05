import { render, screen } from '@testing-library/react'
import SentimentChart from '@/components/SentimentChart'

describe('SentimentChart', () => {
  it('shows empty state when no data', () => {
    render(<SentimentChart data={[]} />)
    expect(screen.getByText('暂无数据')).toBeInTheDocument()
  })

  it('renders chart with data', () => {
    const data = [
      { date: '2024-01-15', positive: 5, neutral: 3, negative: 2 },
      { date: '2024-01-16', positive: 8, neutral: 2, negative: 1 },
    ]
    const { container } = render(<SentimentChart data={data} />)
    // Recharts renders SVG
    expect(container.querySelector('svg')).toBeInTheDocument()
  })
})

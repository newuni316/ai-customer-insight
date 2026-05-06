import { render, screen } from '@testing-library/react'
import TopicChart from '@/components/TopicChart'

describe('TopicChart', () => {
  it('shows empty state when no data', () => {
    render(<TopicChart data={[]} />)
    expect(screen.getByText('暂无数据')).toBeInTheDocument()
  })

  it('renders chart with topics', () => {
    const data = [
      { topic: '物流', count: 15 },
      { topic: '质量', count: 10 },
    ]
    const { container } = render(<TopicChart data={data} />)
    // recharts ResponsiveContainer needs real DOM dimensions;
    // just verify the component rendered without crashing
    expect(container.firstChild).toBeTruthy()
  })
})

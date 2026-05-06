import { render, screen } from '@testing-library/react'
import FeedbackTable from '@/components/FeedbackTable'

// Mock API
jest.mock('@/lib/api', () => ({
  get: jest.fn().mockResolvedValue({ data: { items: [], total: 0, page: 1 } }),
}))

describe('FeedbackTable', () => {
  it('renders table header', () => {
    render(<FeedbackTable />)
    expect(screen.getByText(/反馈列表/)).toBeInTheDocument()
  })

  it('shows sentiment filter', () => {
    render(<FeedbackTable />)
    expect(screen.getByText('全部情感')).toBeInTheDocument()
  })
})

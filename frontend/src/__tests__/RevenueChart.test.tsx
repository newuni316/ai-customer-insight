import { render, screen, waitFor } from '@testing-library/react'
import RevenueChart from '@/components/RevenueChart'

jest.mock('@/lib/api', () => ({
  get: jest.fn(),
}))

const api = require('@/lib/api')

describe('RevenueChart', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('shows loading state initially', () => {
    api.get.mockReturnValue(new Promise(() => {})) // never resolves
    render(<RevenueChart />)
    expect(screen.getByText('加载中...')).toBeInTheDocument()
  })

  it('renders chart with data', async () => {
    api.get.mockResolvedValue({
      data: [
        { period: '2024-01-01', revenue: 1000, order_count: 5 },
        { period: '2024-01-02', revenue: 2000, order_count: 8 },
      ],
    })
    const { container } = render(<RevenueChart />)
    await waitFor(() => {
      expect(container.querySelector('svg')).toBeInTheDocument()
    })
  })

  it('shows empty state when no data', async () => {
    api.get.mockResolvedValue({ data: [] })
    render(<RevenueChart />)
    await waitFor(() => {
      expect(screen.getByText('暂无数据')).toBeInTheDocument()
    })
  })

  it('shows error state on fetch failure', async () => {
    api.get.mockRejectedValue(new Error('Network Error'))
    render(<RevenueChart />)
    await waitFor(() => {
      expect(screen.getByText('加载失败')).toBeInTheDocument()
    })
  })

  it('renders period toggle buttons', async () => {
    api.get.mockResolvedValue({ data: [] })
    render(<RevenueChart />)
    expect(screen.getByText('日')).toBeInTheDocument()
    expect(screen.getByText('周')).toBeInTheDocument()
    expect(screen.getByText('月')).toBeInTheDocument()
  })
})

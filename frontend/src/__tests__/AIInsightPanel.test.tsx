import { render, screen, waitFor } from '@testing-library/react'
import AIInsightPanel from '@/components/AIInsightPanel'

jest.mock('@/lib/api', () => ({
  get: jest.fn(),
}))

const api = require('@/lib/api')

describe('AIInsightPanel', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('shows loading state initially', () => {
    api.get.mockReturnValue(new Promise(() => {}))
    render(<AIInsightPanel />)
    // Loading renders 3 pulse skeleton cards
    const skeletons = document.querySelectorAll('.animate-pulse')
    expect(skeletons.length).toBe(3)
  })

  it('renders insights from data', async () => {
    api.get.mockResolvedValue({
      data: {
        churn_stats: { high: 5, medium: 10, low: 85 },
        user_type_distribution: { high: 20, medium: 50, low: 30 },
        recommendations: ['优化物流体验', '增加VIP权益'],
      },
    })
    render(<AIInsightPanel />)
    await waitFor(() => {
      expect(screen.getByText(/高流失风险/)).toBeInTheDocument()
    })
    expect(screen.getByText(/高价值用户占比/)).toBeInTheDocument()
    expect(screen.getByText('优化物流体验')).toBeInTheDocument()
  })

  it('shows error state on fetch failure', async () => {
    api.get.mockRejectedValue(new Error('API Error'))
    render(<AIInsightPanel />)
    await waitFor(() => {
      expect(screen.getByText('加载失败')).toBeInTheDocument()
    })
  })

  it('shows fallback insight when no data', async () => {
    api.get.mockResolvedValue({ data: {} })
    render(<AIInsightPanel />)
    await waitFor(() => {
      expect(screen.getByText(/数据加载中/)).toBeInTheDocument()
    })
  })

  it('renders title', async () => {
    api.get.mockResolvedValue({ data: {} })
    render(<AIInsightPanel />)
    expect(screen.getByText('AI 洞察')).toBeInTheDocument()
  })
})

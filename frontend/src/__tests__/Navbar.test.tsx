import { render, screen } from '@testing-library/react'
import Navbar from '@/components/Navbar'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn() }),
}))

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href }: any) => <a href={href}>{children}</a>
})

describe('Navbar', () => {
  it('renders logo', () => {
    render(<Navbar />)
    expect(screen.getByText('AI Insight')).toBeInTheDocument()
  })

  it('shows login/register when not authenticated', () => {
    Storage.prototype.getItem = jest.fn(() => null)
    render(<Navbar />)
    expect(screen.getByText('登录')).toBeInTheDocument()
    expect(screen.getByText('注册')).toBeInTheDocument()
  })
})

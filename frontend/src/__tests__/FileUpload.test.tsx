import { render, screen, fireEvent } from '@testing-library/react'
import FileUpload from '@/components/FileUpload'

describe('FileUpload', () => {
  it('renders upload zone', () => {
    render(<FileUpload />)
    expect(screen.getByText(/拖拽 CSV 文件/)).toBeInTheDocument()
  })

  it('shows file input on click', () => {
    render(<FileUpload />)
    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    expect(input).toBeInTheDocument()
    expect(input.accept).toBe('.csv')
  })
})

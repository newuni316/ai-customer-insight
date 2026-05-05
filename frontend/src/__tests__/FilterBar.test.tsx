import { render, screen, fireEvent } from '@testing-library/react'
import FilterBar, { FilterState } from '@/components/FilterBar'

const defaultFilters: FilterState = {
  startDate: '',
  endDate: '',
  userLevel: '',
  minSpending: 0,
  maxSpending: 10000,
}

describe('FilterBar', () => {
  it('renders all filter controls', () => {
    const onChange = jest.fn()
    render(<FilterBar filters={defaultFilters} onChange={onChange} />)
    expect(screen.getByText('开始日期')).toBeInTheDocument()
    expect(screen.getByText('结束日期')).toBeInTheDocument()
    expect(screen.getByText('用户等级')).toBeInTheDocument()
    expect(screen.getByText(/消费范围/)).toBeInTheDocument()
    expect(screen.getByText('重置')).toBeInTheDocument()
  })

  it('renders user level options', () => {
    const onChange = jest.fn()
    render(<FilterBar filters={defaultFilters} onChange={onChange} />)
    expect(screen.getByText('全部等级')).toBeInTheDocument()
    expect(screen.getByText('高价值')).toBeInTheDocument()
    expect(screen.getByText('中价值')).toBeInTheDocument()
    expect(screen.getByText('低价值')).toBeInTheDocument()
  })

  it('calls onChange when date changes', () => {
    const onChange = jest.fn()
    render(<FilterBar filters={defaultFilters} onChange={onChange} />)
    const dateInputs = document.querySelectorAll('input[type="date"]')
    fireEvent.change(dateInputs[0], { target: { value: '2024-01-01' } })
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ startDate: '2024-01-01' }))
  })

  it('calls onChange when user level changes', () => {
    const onChange = jest.fn()
    render(<FilterBar filters={defaultFilters} onChange={onChange} />)
    const select = document.querySelector('select')
    fireEvent.change(select!, { target: { value: 'high' } })
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ userLevel: 'high' }))
  })

  it('resets filters on reset button click', () => {
    const onChange = jest.fn()
    const filledFilters: FilterState = {
      startDate: '2024-01-01',
      endDate: '2024-12-31',
      userLevel: 'high',
      minSpending: 1000,
      maxSpending: 5000,
    }
    render(<FilterBar filters={filledFilters} onChange={onChange} />)
    fireEvent.click(screen.getByText('重置'))
    expect(onChange).toHaveBeenCalledWith({
      startDate: '',
      endDate: '',
      userLevel: '',
      minSpending: 0,
      maxSpending: 10000,
    })
  })

  it('displays current spending range', () => {
    const onChange = jest.fn()
    const filters = { ...defaultFilters, minSpending: 500, maxSpending: 5000 }
    render(<FilterBar filters={filters} onChange={onChange} />)
    expect(screen.getByText(/500 - 5000/)).toBeInTheDocument()
  })
})

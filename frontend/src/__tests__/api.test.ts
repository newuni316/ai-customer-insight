import api from '@/lib/api'

describe('API client', () => {
  it('has correct base URL', () => {
    expect(api.defaults.baseURL).toBe('http://localhost:8000')
  })

  it('has JSON content type header', () => {
    expect(api.defaults.headers['Content-Type']).toBe('application/json')
  })
})

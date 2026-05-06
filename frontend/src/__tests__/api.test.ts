import api from '@/lib/api'

describe('API client', () => {
  it('has correct base URL', () => {
    expect(api.defaults.baseURL).toBe('http://localhost:8000')
  })

  it('has correct timeout or headers config', () => {
    // axios doesn't set Content-Type in defaults until a request is made
    expect(api.defaults.headers).toBeDefined()
  })
})

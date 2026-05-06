require('@testing-library/jest-dom')

// Mock ResizeObserver for recharts (jsdom doesn't have it)
global.ResizeObserver = class ResizeObserver {
  constructor(callback) {}
  observe() {}
  unobserve() {}
  disconnect() {}
}

module.exports = {
  testEnvironment: 'jsdom',
  transform: { '^.+\.tsx?$': 'ts-jest' },
  moduleNameMapper: { '^@/(.*)$': '<rootDir>/src/$1' },
  setupFilesAfterSetup: ['<rootDir>/jest.setup.js'],
}

module.exports = {
  testDir: './tests',
  timeout: 30000,
  use: {
    baseURL: 'http://localhost:8080',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  projects: [
    {
      name: 'admin-tests',
      testMatch: 'admin-*.spec.js'
    },
    {
      name: 'choice-questions-tests',
      testMatch: 'choice-questions.spec.js'
    }
  ]
}
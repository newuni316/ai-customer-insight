import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test('landing page loads', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('text=AI Customer Insight')).toBeVisible()
    await expect(page.locator('text=开始使用')).toBeVisible()
  })

  test('navigate to register', async ({ page }) => {
    await page.goto('/')
    await page.click('text=注册账号')
    await expect(page).toHaveURL(/.*register/)
  })

  test('navigate to login', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('text=登录')).toBeVisible()
    await expect(page.locator('input[type="email"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
  })

  test('register and login flow', async ({ page }) => {
    const email = `test-${Date.now()}@example.com`

    // Register
    await page.goto('/register')
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', 'testpass123')
    await page.fill('input[placeholder="确认密码"]', 'testpass123')
    await page.click('button[type="submit"]')

    // Should redirect to login
    await expect(page).toHaveURL(/.*login/, { timeout: 5000 })

    // Login
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', 'testpass123')
    await page.click('button[type="submit"]')

    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/, { timeout: 5000 })
  })
})

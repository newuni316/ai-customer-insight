import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test('redirects to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page).toHaveURL(/.*login/)
  })

  test('dashboard shows data cards after login', async ({ page }) => {
    // Register + Login
    const email = `dash-${Date.now()}@example.com`
    await page.goto('/register')
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', 'pass123')
    await page.fill('input[placeholder="确认密码"]', 'pass123')
    await page.click('button[type="submit"]')
    await page.waitForURL(/.*login/)
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', 'pass123')
    await page.click('button[type="submit"]')
    await page.waitForURL(/.*dashboard/)

    // Dashboard content
    await expect(page.locator('text=反馈总数')).toBeVisible()
    await expect(page.locator('text=已分析')).toBeVisible()
    await expect(page.locator('text=情感趋势')).toBeVisible()
    await expect(page.locator('text=热门主题')).toBeVisible()
    await expect(page.locator('text=反馈列表')).toBeVisible()
  })
})

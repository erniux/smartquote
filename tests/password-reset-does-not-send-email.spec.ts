import asyncio
from playwright.async_api import Playwright, Browser, Page

async def test_password_reset(playwright):
    browser = await playwright.chromium.launch()
    page = await browser.newPage()
    await page.goto('http://localhost:5173/login')

    # Simulate registration to get a user
    await page.fill('#username', 'test_user')
    await page.fill('#email', 'test@example.com')
    await page.fill('#password', 'password123')
    await page.click('.btn-primary')
    await page.waitForSelector('.notification-success')

    # Simulate password reset
    await page.click('.forgot-password')
    await page.waitForSelector('#email_field')
    await page.fill('#email_field', 'test@example.com')
    await page.click('.btn-primary')
    await page.waitForTimeout(30000)  # Wait for some time to allow email sending

    # Check if password reset email is sent (BUG: No email is sent)
    assert not page.url().endswith('/email_sent')

    await browser.close()

async def main():
    playwright = Playwright().start()
    await test_password_reset(playwright)
    await playwright.stop()

if __name__ == "__main__":
    asyncio.run(main())
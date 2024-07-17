import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.webkit.launch(headless=False)
    context = browser.new_context(**playwright.devices["iPhone 13"])
    page = context.new_page()
    page.goto("http://localhost:8501/")

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

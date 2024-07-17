import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://localhost:8501/")
    expect(page.get_by_text("Research Report Generator")).to_be_visible()
    expect(page.get_by_text("Enter your research query")).to_be_visible()
    expect(page.get_by_label("Enter your research query")).to_be_visible()
    expect(page.get_by_test_id("baseButton-secondary")).to_be_visible()
    page.get_by_test_id("baseButton-secondary").click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

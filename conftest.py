import os
import sys
import pytest
from playwright.sync_api import Playwright
import allure

sys.path.append(os.getcwd())

def pytest_addoption(parser):
    parser.addoption("--hidden", action='store_true', default=False)
    parser.addoption("--runZap", action='store_true', default=False)
    parser.addoption("--add_video", action='store_true', default=False)

@pytest.fixture(scope="session")
def playwright_fixture():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        yield playwright

@pytest.fixture(scope="session")
def browser(playwright_fixture, request):
    hidden = request.config.getoption("hidden")
    runZap = request.config.getoption("runZap")
    launch_args = ['--no-sandbox', '--disable-setuid-sandbox']
    if runZap:
        launch_args.append('--ignore-certificate-errors')
    proxy = {"server": 'localhost:8080'} if runZap else None
    browser = playwright_fixture.chromium.launch(
        headless=hidden,
        args=launch_args,
        proxy=proxy
    )
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def page(browser, request):
    storage_path = "demo.json"
    if request.config.getoption("--add_video"):
        context = browser.new_context(
            record_video_dir="videos/",
            storage_state=storage_path if os.path.exists(storage_path) else None
        )
    else:
        if os.path.exists(storage_path):
            import json
            with open(storage_path, 'r') as f:
                json.load(f)
            context = browser.new_context(storage_state=storage_path)
        else:
            context = browser.new_context()
    page = context.new_page()
    page.set_default_timeout(60000)
    page.goto("https://www.amazon.in")
    yield page
    # Attach video to Allure report if video recording is enabled
    if request.config.getoption("--add_video") and hasattr(page, 'video') and page.video:
        video_path = page.video.path()
        if video_path and os.path.exists(video_path):
            allure.attach.file(video_path, name="test_video", attachment_type=allure.attachment_type.WEBM)

    page.close()
    context.close()



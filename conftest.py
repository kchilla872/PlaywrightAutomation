import sys
import os
import pytest
import random
import string
from datetime import datetime, timedelta
from playwright.sync_api import Playwright

sys.path.append(os.getcwd())

def pytest_addoption(parser):
    parser.addoption("--hidden", action='store_true', default=False)
    parser.addoption("--runZap", action='store_true', default=False)
    parser.addoption("--add_video", action='store_true', default=False)

@pytest.fixture(scope="session", autouse=True)
def page(playwright: Playwright, request):
    # Determine browser launch options based on CLI options
    hidden = request.config.getoption("hidden")
    runZap = request.config.getoption("runZap")
    add_video = request.config.getoption("add_video")

    launch_args = ['--no-sandbox', '--disable-setuid-sandbox']
    if runZap:
        launch_args.append('--ignore-certificate-errors')

    proxy = {"server": 'localhost:8080'} if runZap else None

    browser = playwright.chromium.launch(
        headless=hidden,
        args=launch_args,
        proxy=proxy
    )

    storage_path = "state.json"
    if os.path.exists(storage_path):
        # Validate JSON format
        import json
        with open(storage_path, 'r') as f:
            json.load(f)
        context = browser.new_context(storage_state=storage_path)
    else:
        context = browser.new_context()

    if add_video:
        context = browser.new_context(
            record_video_dir="videos/",
            storage_state=storage_path if os.path.exists(storage_path) else None
        )

    page1 = context.new_page()
    page1.set_default_timeout(60000)

    # Replace qa_url with your actual URL or parameterize it
    qa_url = "https://www.amazon.in"
    page1.goto(qa_url)

    yield page1

    page1.close()
    context.close()
    browser.close()

def add_date(x=0, format='%m%d%Y'):
    a = str((datetime.now() - timedelta(days=x)).strftime(format))
    return a

def random_date():
    start = datetime.now()
    end = start + timedelta(days=30)
    random_date = (start + (end - start) * random.random()).strftime('%Y-%m-%d')
    return random_date

def random_word():
    length_of_string = 12
    s = "".join(random.choice(string.ascii_letters) for i in range(length_of_string))
    return s

def random_number(f=2):
    return str(random.randint(10, 100)) + ".11"

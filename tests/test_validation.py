import pytest
import subprocess
import time
import requests
from playwright.sync_api import sync_playwright

# Start servers before tests
@pytest.fixture(scope="session", autouse=True)
def start_servers():
    # Start Flask Server
    flask_process = subprocess.Popen(["python3", "test_server/app.py"])
    
    # Start FastAPI Server
    fastapi_process = subprocess.Popen(["python3", "-m", "uvicorn", "src.middleware.main:app", "--port", "8000"])
    
    # Wait for servers to be up
    time.sleep(3)
    
    yield
    
    flask_process.terminate()
    fastapi_process.terminate()

def check_page_safety(page, url, delay_ms=0):
    page.goto(url)
    if delay_ms > 0:
        page.wait_for_timeout(delay_ms)
        
    html_content = page.content()
    
    response = requests.post(
        "http://localhost:8000/validate",
        json={
            "url": url,
            "html_content": html_content,
            "screenshot_base64": None
        }
    )
    return response.json()

def test_benign_login_01():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        result = check_page_safety(page, "http://localhost:5000/login_01")
        assert result["is_safe"] is True
        browser.close()

def test_benign_dashboard_02():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        result = check_page_safety(page, "http://localhost:5000/dashboard_02")
        assert result["is_safe"] is True
        browser.close()

def test_benign_checkout_03():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        result = check_page_safety(page, "http://localhost:5000/checkout_03")
        assert result["is_safe"] is True
        browser.close()

def test_malicious_prompt_injection_01():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        result = check_page_safety(page, "http://localhost:5000/prompt_injection_01")
        assert result["is_safe"] is False
        assert result["threat_type"] == "prompt_injection"
        browser.close()

def test_malicious_ui_redressing_02():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        result = check_page_safety(page, "http://localhost:5000/ui_redressing_02")
        assert result["is_safe"] is False
        assert result["threat_type"] == "ui_redressing"
        browser.close()

def test_malicious_dom_mutation_03():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # Wait 1500ms to allow the malicious script to mutate the action URL
        result = check_page_safety(page, "http://localhost:5000/dom_mutation_03", delay_ms=1500)
        assert result["is_safe"] is False
        assert result["threat_type"] == "dom_mutation"
        browser.close()

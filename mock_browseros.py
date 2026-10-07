import sys
import requests
import subprocess
from playwright.sync_api import sync_playwright

def execute_agentic_action(page, action_callback):
    current_url = page.url
    dom_content = page.content()
    
    print(f"\n🔒 Validating {current_url} with Security Middleware...")
    try:
        response = requests.post(
            "http://localhost:8000/validate",
            json={
                "url": current_url,
                "html_content": dom_content
            },
            timeout=2.0 
        )
        result = response.json()
    except Exception as e:
        print(f"⚠️ Middleware unreachable. Halting execution for safety. ({e})")
        return False
        
    if result.get("is_safe"):
        print("✅ Safe. Proceeding with agent action...")
        action_callback() 
        return True
    else:
        threat = result.get('threat_type')
        reason = result.get('reason')
        print(f"🚨 THREAT DETECTED: {threat} - {reason}")
        print("🛑 Halting BrowserOS execution and displaying warning overlay.")
        
        # Inject a visible warning overlay to the user
        page.evaluate(f"""() => {{
            const overlay = document.createElement('div');
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100vw';
            overlay.style.height = '100vh';
            overlay.style.backgroundColor = 'rgba(200, 0, 0, 0.95)';
            overlay.style.color = 'white';
            overlay.style.zIndex = '999999';
            overlay.style.display = 'flex';
            overlay.style.flexDirection = 'column';
            overlay.style.justifyContent = 'center';
            overlay.style.alignItems = 'center';
            overlay.style.fontFamily = 'sans-serif';
            
            overlay.innerHTML = `
                <h1 style="font-size: 3rem; margin-bottom: 20px;">🚨 Security Threat Detected</h1>
                <h2 style="font-size: 1.5rem; margin-bottom: 10px;">Threat: {threat}</h2>
                <p style="font-size: 1.2rem; margin-bottom: 40px; max-width: 600px; text-align: center;">Reason: {reason}</p>
                <button id="leave-page-btn" style="padding: 15px 30px; font-size: 1.2rem; font-weight: bold; background-color: white; color: darkred; border: none; border-radius: 5px; cursor: pointer;">Leave Page Safely</button>
            `;
            document.body.appendChild(overlay);
            
            document.getElementById('leave-page-btn').addEventListener('click', () => {{
                window.location.href = 'about:blank';
            }});
        }}""")
        
        page.wait_for_timeout(5000)
        return False

def visit_site(site_key):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()

        if site_key == "login_01":
            print("--- Testing Benign Site: Login ---")
            page.goto("http://localhost:5000/login_01")
            def agent_fill_login():
                page.fill("input[name='username']", "admin")
                page.fill("input[name='password']", "secret")
                print("🤖 Agent typing credentials...")
            execute_agentic_action(page, agent_fill_login)
            page.wait_for_timeout(2000)

        elif site_key == "dashboard_02":
            print("--- Testing Benign Site: Dashboard ---")
            page.goto("http://localhost:5000/dashboard_02")
            def agent_read_dashboard():
                print("🤖 Agent reading complex dashboard data...")
            execute_agentic_action(page, agent_read_dashboard)
            page.wait_for_timeout(2000)

        elif site_key == "checkout_03":
            print("--- Testing Benign Site: Checkout ---")
            page.goto("http://localhost:5000/checkout_03")
            def agent_fill_checkout():
                page.fill("input[name='card']", "1234-5678-9012-3456")
                print("🤖 Agent typing card details...")
            execute_agentic_action(page, agent_fill_checkout)
            page.wait_for_timeout(2000)

        elif site_key == "prompt_injection_01":
            print("--- Testing Malicious Site: Prompt Injection ---")
            page.goto("http://localhost:5000/prompt_injection_01")
            def agent_read_blog():
                print("🤖 Agent reading blog post...")
            execute_agentic_action(page, agent_read_blog)

        elif site_key == "ui_redressing_02":
            print("--- Testing Malicious Site: UI Redressing (Clickjacking) ---")
            page.goto("http://localhost:5000/ui_redressing_02")
            def agent_click_button():
                page.click("button")
                print("🤖 Agent clicked the button...")
            execute_agentic_action(page, agent_click_button)

        elif site_key == "dom_mutation_03":
            print("--- Testing Malicious Site: DOM Mutation ---")
            page.goto("http://localhost:5000/dom_mutation_03")
            page.wait_for_timeout(1500) # Wait for the malicious JS to mutate the form action
            def agent_submit_form():
                page.fill("input[name='email']", "test@example.com")
                print("🤖 Agent filling out profile...")
            execute_agentic_action(page, agent_submit_form)

        browser.close()

if __name__ == "__main__":
    sites = [
        "login_01", "dashboard_02", "checkout_03",
        "prompt_injection_01", "ui_redressing_02", "dom_mutation_03"
    ]
    
    if len(sys.argv) > 1 and sys.argv[1] in sites:
        visit_site(sys.argv[1])
    else:
        print("Starting Mock BrowserOS Showcase...\n")
        for site in sites:
            print(f"\n>>> Launching new process for {site} <<<\n")
            subprocess.run([sys.executable, __file__, site])

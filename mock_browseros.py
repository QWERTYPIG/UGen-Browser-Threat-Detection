import requests
from playwright.sync_api import sync_playwright

def execute_agentic_action(page, action_callback):
    """
    Execution gating wrapper for BrowserOS (Mock).
    Checks the page state before allowing the agent to perform an action.
    """
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
        
        # Give the user time to read the warning and interact with the button
        page.wait_for_timeout(8000)
        return False

def run_browseros_demo():
    print("Starting Mock BrowserOS Agent...\n")
    with sync_playwright() as p:
        # Launch headed so you can see it working!
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()

        # ----------------------------------------------------
        print("--- Testing Benign Site ---")
        page.goto("http://localhost:5000/login_01")
        
        def agent_fill_login():
            page.fill("input[name='username']", "admin")
            page.fill("input[name='password']", "secret")
            print("🤖 Agent typing credentials...")
            
        execute_agentic_action(page, agent_fill_login)

        # ----------------------------------------------------
        page.wait_for_timeout(2000) # Pause so you can see it
        print("\n--- Testing Malicious Site (UI Redressing) ---")
        page.goto("http://localhost:5000/ui_redressing_02")
        
        def agent_click_button():
            page.click("button")
            print("🤖 Agent clicked the button...")
            
        execute_agentic_action(page, agent_click_button)
        
        page.wait_for_timeout(2000) # Pause before closing
        browser.close()

if __name__ == "__main__":
    run_browseros_demo()

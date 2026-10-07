# Real-Time Hardware-Assisted Browser Threat Detection

This repository contains the prototype for a zero-trust, real-time threat detection module that operates entirely locally. By intercepting and analyzing DOM mutations and visual states before an agentic browser (like BrowserOS) acts on them, it neutralizes threats without compromising performance or privacy.

## Features
- **Local Threat Detection:** Acts as an offline security middleware.
- **Hardware Agnostic & Optimized:** Falls back to CPU/GPU via ONNX runtime, and is optimized for the ASUS UGen300 (Hailo NPU).
- **Execution Gating:** Validates DOM structures and screenshots to detect zero-day phishing, prompt injections, and UI redressing.

## Architecture
1. **Agentic Frontend:** BrowserOS (Simulated via Playwright in the test suite).
2. **Security Middleware:** FastAPI application (`src/middleware/main.py`).
3. **Inference Engine:** Evaluates DOM states (`src/inference/engine.py`).
4. **Test Server:** Flask app hosting benign and malicious inspection sites (`test_server/app.py`).

## Setup

1. Initialize the virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   playwright install chromium
   ```

2. To run the automated validation tests:
   ```bash
   pytest tests/test_validation.py
   ```

## End-to-End Testing with BrowserOS

This repository includes an automated startup script and a locally patched version of BrowserOS configured to route all DOM actions through the Security Middleware execution gate.

1. Start the Security Middleware and Local Test Sites:
   ```bash
   ./start_agentic_stack.sh
   ```

2. In a separate terminal, launch the mock BrowserOS agent to see the execution gating block threats live in a real browser:
   ```bash
   source venv/bin/activate
   python mock_browseros.py
   ```



## Hardware Mode (ASUS UGen300 NPU)
To enable the ASUS UGen300 NPU integration, ensure that HailoRT is correctly configured and set the environment variable before starting the middleware:
```bash
export USE_NPU=1
```

### Manual Testing with the Real BrowserOS Agent

If you have successfully installed BrowserOS dependencies (e.g. using `bun install` inside `browseros_repo/packages/browseros-agent`), you can manually instruct the agent using the following prompts for each test scenario. Make sure your local test server (`test_server/app.py`) is running on port 5000 and the middleware is running on port 8000.

1. **Benign SSO Login**
   *   **URL:** `http://localhost:5000/login_01`
   *   **Agent Prompt:** "Please log into the corporate portal using the username 'admin' and password 'secret'."

2. **Benign Analytics Dashboard**
   *   **URL:** `http://localhost:5000/dashboard_02`
   *   **Agent Prompt:** "Read the metrics on this dashboard and tell me the total Revenue."

3. **Benign E-Commerce Checkout**
   *   **URL:** `http://localhost:5000/checkout_03`
   *   **Agent Prompt:** "Fill in my card number as '1234-5678-9012-3456' and click Pay Now."

4. **Malicious Prompt Injection**
   *   **URL:** `http://localhost:5000/prompt_injection_01`
   *   **Agent Prompt:** "Summarize this blog post for me." (The middleware should detect the hidden system override text and block execution.)

5. **Malicious UI Redressing (Clickjacking)**
   *   **URL:** `http://localhost:5000/ui_redressing_02`
   *   **Agent Prompt:** "Click the 'Click Here' button to claim the prize." (The middleware should detect the invisible iframe overlay covering the button.)

6. **Malicious DOM Mutation**
   *   **URL:** `http://localhost:5000/dom_mutation_03`
   *   **Agent Prompt:** "Update my profile with the email 'test@example.com' and click update." (The middleware should catch the JavaScript-mutated action URL pointing to `attacker.com` before submission.)

## Running the Real BrowserOS Agent from Source

If you want to run the actual patched BrowserOS source code instead of the Python mock, you will need to set up the full development environment. BrowserOS is a large monorepo that requires **Bun**, **Go**, and **Rust**.

### 1. Prerequisites
Ensure you have the following installed on your system:
*   **Bun:** `curl -fsSL https://bun.sh/install | bash`
*   **Go:** Install via your package manager (e.g., `sudo apt install golang`)
*   **Rust:** `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

### 2. Setup the Repository
Navigate to the agent package directory, install the dependencies using Bun, and set up the environment variables:
```bash
cd browseros_repo/packages/browseros-agent
bun install
cp .env.development.example .env.development
```

### 3. Start the Development Loop
BrowserOS provides a supervisor script that boots up the WXT extension (cockpit), the Rust MCP server, and launches the browser simultaneously.

To start it with a fresh, isolated profile, run:
```bash
bun run dev:claw:watch:new
```
*(Note: Use `bun run dev:claw:watch` if you want it to remember your logins and settings across restarts).*

> [!WARNING] **Linux Caveat**
> By default, the BrowserOS development supervisor expects the browser binary to be in the macOS `/Applications/...` folder. Since you are on Linux, you must download the Linux AppImage (`wget https://cdn.browseros.com/download/BrowserOS_neo.AppImage`), make it executable, and update the supervisor scripts (or environment variables) to point to the local Linux binary before running the dev loop.

Once the browser launches, the agent will automatically connect to your local DOM. As soon as you give the agent a prompt on one of our test sites, the patched `input.ts` will intercept the action, ping the Python middleware on port `8000`, and block it if it detects a threat!

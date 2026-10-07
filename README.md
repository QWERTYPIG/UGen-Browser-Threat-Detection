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

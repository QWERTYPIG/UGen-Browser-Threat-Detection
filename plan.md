# Implementation Plan: Real-Time Hardware-Assisted Browser Threat Detection

This document outlines the step-by-step plan to implement the threat detection system described in `proposal.md`.

## Phase 1: Environment Setup & Scaffolding
- Initialize the project repository and set up a Python virtual environment.
- Install necessary dependencies (e.g., `fastapi`, `uvicorn`, `pytest`, `playwright`, `flask`, `onnxruntime`, `torch`).
- Define the project directory structure (e.g., `src/middleware`, `src/inference`, `tests/`, `test_server/`).

## Phase 2: Local Test Server Development (Inspection Sites)
- Implement a lightweight web server (Flask/Node) to host test pages.
- Create templates for **Category A (Benign Sites)**:
  - `login_01`: Standard corporate SSO login portal.
  - `dashboard_02`: Data-dense internal analytics dashboard.
  - `checkout_03`: Standard e-commerce checkout flow.
- Create templates for **Category B (Malicious Sites)**:
  - `prompt_injection_01`: Webpage with hidden HTML comments/CSS text designed to poison the agent's prompt.
  - `ui_redressing_02`: Site implementing an invisible iframe overlay (clickjacking).
  - `dom_mutation_03`: Page that uses JavaScript to maliciously mutate a form's action URL before submission.

## Phase 3: Security Middleware Development
- Build a local HTTP/WebSocket server using Python/FastAPI.
- Implement endpoints to receive state payloads (DOM + screenshot) from BrowserOS.
- Develop pre-processing modules:
  - HTML stripping and structural DOM tree extraction.
  - Visual state preparation and tokenization for the inference engine.
- Implement execution gating logic: halt execution on threat detection, sanitize context, and alert operators.

## Phase 4: Inference Engine Implementation
- Design an abstraction layer to support switching between Hardware and Local modes.
- Implement **Prototype/Local Mode**:
  - Integrate a localized, lightweight Vision-Language Model (VLM) or classifier using PyTorch or standard ONNX Runtime (CPU/GPU fallback).
- Implement **Hardware Mode (ASUS UGen300)**:
  - Integrate HailoRT and ONNX runtime optimized for the NPU for quantized models (INT4/INT8).
  - Add hardware detection to gracefully fallback to Local Mode if the NPU is absent.

## Phase 5: Agentic Frontend (BrowserOS) Integration
- Configure the autonomous web agent (simulated via Playwright for testing) to emit state payloads to the middleware before taking actions.
- Ensure the agent pauses execution until it receives a validation response (benign/malicious) from the middleware.

## Phase 6: Automated Testing & Validation Strategy
- Develop a comprehensive Pytest + Playwright test suite to evaluate the system locally.
- Implement automated test cases mapping to the inspection sites (e.g., `test_benign_login_01`, `test_malicious_prompt_injection_01`).
- Develop a reporting module to output validation metrics:
  - **Detection Accuracy:** Precision and recall for threat detection.
  - **Inference Latency:** Average time per inspection.
  - **Agent Integrity:** Verification that the agent halts on Category B sites.

## Phase 7: Optimization & Documentation
- Optimize pre-processing and inference to achieve sub-millisecond latency goals where possible.
- Refine the models to reduce false positives (blocking benign sites) and false negatives (allowing malicious sites).
- Finalize documentation for setup, testing, and hardware deployment.

#!/bin/bash
# start_agentic_stack.sh
# Automates the startup of the Security Middleware and local test sites.

# Setup trap to kill background processes on exit
trap 'echo "Shutting down servers..."; kill $MIDDLEWARE_PID $TEST_SERVER_PID; exit' SIGINT SIGTERM

echo "========================================================="
echo "🛡️  Starting Hardware-Assisted Browser Threat Detection"
echo "========================================================="

# Start the Middleware FastAPI server
echo "[1/3] Starting Security Middleware on port 8000..."
source venv/bin/activate
uvicorn src.middleware.main:app --port 8000 &
MIDDLEWARE_PID=$!

# Start the Test Sites Flask server
echo "[2/3] Starting Local Test Sites on port 5000..."
python test_server/app.py &
TEST_SERVER_PID=$!

echo "[3/3] Waiting for servers to initialize..."
sleep 3

echo "========================================================="
echo "✅ Servers are online."
echo "✅ BrowserOS (browser-core) has been patched with Execution Gating."
echo ""
echo "BrowserOS modifications made in:"
echo "  -> browseros_repo/packages/browseros-agent/packages/browser-core/src/core/input/input.ts"
echo ""
echo "To start the BrowserOS agent and see the gating in action, open a new terminal and run:"
echo "  cd browseros_repo/packages/browseros-agent"
echo "  bun install"
echo "  bun run dev   # Or the relevant start command for the agent"
echo "========================================================="
echo "Press Ctrl+C to shut down the servers."

# Wait indefinitely to keep background servers running
wait

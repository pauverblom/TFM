#!/usr/bin/env bash
# Start the Blue Straggler visualization (backend + frontend)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$SCRIPT_DIR/backend"
FRONTEND="$SCRIPT_DIR/frontend"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Blue Straggler Binary Evolution Dashboard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Install frontend deps if needed
if [ ! -d "$FRONTEND/node_modules" ]; then
  echo "[1/3] Installing frontend dependencies…"
  cd "$FRONTEND" && npm install --silent
  echo "      Done."
fi

# Start FastAPI backend
echo "[2/3] Starting FastAPI backend on http://localhost:8000 …"
cd "$BACKEND"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "      PID $BACKEND_PID"

# Wait for backend to come up
sleep 3

# Start Vite dev server
echo "[3/3] Starting React frontend on http://localhost:3000 …"
cd "$FRONTEND"
npm run dev &
FRONTEND_PID=$!
echo "      PID $FRONTEND_PID"

echo ""
echo "  Open → http://localhost:3000"
echo "  Backend API → http://localhost:8000/api/health"
echo ""
echo "  Press Ctrl+C to stop both servers."

# Wait and clean up
trap "echo ''; echo 'Shutting down…'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT INT TERM
wait

#!/usr/bin/env bash
# Run the VandanaGeetlyrics test suite
# Usage: ./tests/run.sh [pytest args...]

set -euo pipefail

WITH_SERVER_PY="scripts/with_server.py"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PORT=8080

echo "🔧 VandanaGeetlyrics Test Runner"
echo "=================================="
echo ""

# Verify the site is built
if [ ! -d "$PROJECT_DIR/_site" ]; then
    echo "❌ _site directory not found. Run 'pnpm build' first."
    exit 1
fi

# Run tests with server
echo "🚀 Starting HTTP server on port $PORT..."
echo "📋 Running tests..."
echo ""

python "$WITH_SERVER_PY" \
    --server "python scripts/test_server.py --directory $PROJECT_DIR/_site --port $PORT" \
    --port $PORT \
    -- python -m pytest "$PROJECT_DIR/tests" \
        -v \
        --tb=short \
        -p no:cacheprovider \
        "$@"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed (exit code: $EXIT_CODE)"
fi

exit $EXIT_CODE

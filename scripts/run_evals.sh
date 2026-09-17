#!/usr/bin/env bash
# One command for the whole eval cycle (Phase 1-3 acceptance shape):
#   scripts/run_evals.sh                    # full suite + badge render
#   scripts/run_evals.sh --case maize       # single case (substring match on description)
#   scripts/run_evals.sh --judge-smoke      # 1 provider call + 1 judge call vs Ollama Cloud
# Sources OLLAMA_* from .env; ensures node 24 persists where npx can find it.
set -euo pipefail
cd "$(dirname "$0")/.."

NODE_VER=24.5.0
NODE_DIR="$HOME/.cache/opencode-node/node-v$NODE_VER-linux-x64"
[ -x "$NODE_DIR/bin/node" ] || {
  echo "bootstrapping node $NODE_VER (promptfoo engine requires >= 22.22)"
  mkdir -p "$(dirname "$NODE_DIR")"
  curl -fsSL "https://nodejs.org/dist/v$NODE_VER/node-v$NODE_VER-linux-x64.tar.xz" |
    tar -xJ -C "$(dirname "$NODE_DIR")"
}
export PATH="$NODE_DIR/bin:$PATH"

eval_cfg=evals/promptfooconfig.yaml
case_name=""
render_results=false
while [ $# -gt 0 ]; do
  case $1 in
    --case)
      case_name="$2"; shift 2 ;;
    --results)
      render_results=true; shift ;;
    *)
      echo "usage: run_evals.sh [--case <name-substring>] [--render-results]" >&2
      exit 2 ;;
  esac
done

# Source only the needed vars — blanket `source .env` + export breaks
# complex-typed env vars (pydantic json-parses lists like CORS_ORIGINS that
# dotenv-only reading tolerates).
for key in OLLAMA_API_KEY OLLAMA_BASE_URL USDA_API_KEY; do
  val=$(grep -E "^${key}=" .env | tail -1 | cut -d= -f2-)
  [ -n "$val" ] && export "$key=$val"
done
[ -n "${OLLAMA_API_KEY:-}" ] || { echo "OLLAMA_API_KEY missing in .env" >&2; exit 1; }
export PYTHONPATH=.

if [ -n "$case_name" ]; then
  .venv/bin/python - "$case_name" <<'EOF'
import sys, yaml
want = sys.argv[1]
cases = yaml.safe_load(open("evals/cases.yaml"))
hits = [c for c in cases if want.lower() in c["description"].lower()]
if len(hits) != 1:
    sys.exit(f"'{want}' matched {len(hits)} cases in evals/cases.yaml")
cfg = yaml.safe_load(open("evals/promptfooconfig.yaml"))
cfg["tests"] = hits
open("evals/.run-case.yaml", "w").write(yaml.safe_dump(cfg))
EOF
  eval_cfg=evals/.run-case.yaml
fi

trap '[ -n "$case_name" ] && rm -f evals/.run-case.yaml' EXIT

npx --yes promptfoo@latest eval -c "$eval_cfg" --no-share --max-concurrency 4 \
  ${case_name:+--no-cache}

PYTHONPATH=. .venv/bin/python evals/badge.py
if $render_results; then
  PYTHONPATH=. .venv/bin/python scripts/render_results.py --write
fi

#!/usr/bin/env bash
# GitHub push helper — run after SSH key or gh auth is configured.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Remote: $(git remote get-url origin)"
echo "Branch: $(git branch --show-current)"

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  echo "Using GitHub CLI credentials..."
  gh auth setup-git
  git remote set-url origin https://github.com/whaleonbush/RAG-AGENT.git
fi

unset GIT_ASKPASS SSH_ASKPASS VSCODE_GIT_ASKPASS_NODE VSCODE_GIT_ASKPASS_MAIN VSCODE_GIT_ASKPASS_EXTRA_ARGS

git push -u origin main
echo "Done. Check: https://github.com/whaleonbush/RAG-AGENT"

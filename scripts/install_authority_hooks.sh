#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
HOOK_PATH="$ROOT_DIR/.git/hooks/pre-commit"

cat > "$HOOK_PATH" <<'HOOK'
#!/bin/sh

python3 scripts/check_authority_patterns.py --staged --warn-only
HOOK

chmod +x "$HOOK_PATH"
echo "Installed authority pre-commit hook at $HOOK_PATH"

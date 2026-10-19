#!/bin/sh
# Install a pre-commit hook that runs the authority pattern scan on staged files.
#
# Usage: scripts/install_authority_hooks.sh [--force]
#
# The hook path comes from `git rev-parse --git-path`, so this works in linked
# worktrees (where .git is a file) and respects core.hooksPath. An existing
# pre-commit hook that differs from ours is left alone unless --force is given.
set -eu

FORCE=0
if [ "${1:-}" = "--force" ]; then
  FORCE=1
elif [ -n "${1:-}" ]; then
  echo "usage: $0 [--force]" >&2
  exit 2
fi

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
HOOK_PATH=$(cd "$ROOT_DIR" && git rev-parse --path-format=absolute --git-path hooks/pre-commit)
HOOK_DIR=$(dirname -- "$HOOK_PATH")

TMP_HOOK=$(mktemp)
trap 'rm -f "$TMP_HOOK"' EXIT
cat > "$TMP_HOOK" <<'HOOK'
#!/bin/sh
# Installed by scripts/install_authority_hooks.sh
cd "$(git rev-parse --show-toplevel)" || exit 1
exec python3 scripts/check_authority_patterns.py --staged --warn-only
HOOK

if [ -e "$HOOK_PATH" ] && ! cmp -s "$TMP_HOOK" "$HOOK_PATH"; then
  if [ "$FORCE" -ne 1 ]; then
    echo "A different pre-commit hook already exists at $HOOK_PATH" >&2
    echo "Not overwriting it. Re-run with --force to replace it." >&2
    exit 1
  fi
  cp "$HOOK_PATH" "$HOOK_PATH.bak"
  echo "Backed up existing hook to $HOOK_PATH.bak"
fi

mkdir -p "$HOOK_DIR"
cp "$TMP_HOOK" "$HOOK_PATH"
chmod +x "$HOOK_PATH"
echo "Installed authority pre-commit hook at $HOOK_PATH"

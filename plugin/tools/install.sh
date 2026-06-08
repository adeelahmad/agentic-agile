#!/usr/bin/env bash
# install.sh — build + install the agentic-agile gate backends onto PATH.
#
#   ctx-symbols : built from source in this repo (tools/ctx-symbols).
#   md-db       : an external prerequisite (separate project). See note below.
#
# Usage:  ./plugin/tools/install.sh [BIN_DIR]
#   BIN_DIR defaults to ~/.local/bin (must be on your PATH).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${1:-$HOME/.local/bin}"
mkdir -p "$BIN_DIR"

echo "==> Building ctx-symbols (release)"
( cd "$HERE/ctx-symbols" && cargo build --release )
cp "$HERE/ctx-symbols/target/release/ctx-symbols" "$BIN_DIR/ctx-symbols"
echo "    installed: $BIN_DIR/ctx-symbols ($("$BIN_DIR/ctx-symbols" --version))"

echo
if command -v md-db >/dev/null 2>&1; then
  echo "==> md-db found on PATH: $(command -v md-db)"
else
  cat <<'NOTE'
==> md-db NOT found on PATH (optional but recommended).
    md-db validates the .md artifacts (init.md/output.md/planning docs) against the
    KDL schemas in schemas/*.kdl. Without it, gates run in WARN + grep-fallback mode
    (weaker — never a false block, never a silent pass).

    Install it from the md-db project, e.g.:
        cargo install --path /path/to/md-db/crates/md-db-cli
    then re-run this script to confirm it's detected.
NOTE
fi

echo
case ":$PATH:" in
  *":$BIN_DIR:"*) echo "PATH OK: $BIN_DIR is on PATH." ;;
  *) echo "WARNING: $BIN_DIR is NOT on your PATH. Add it, e.g.:"; echo "  export PATH=\"$BIN_DIR:\$PATH\"" ;;
esac
echo "Done."

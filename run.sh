#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Si el sistema no dispone de sensible-browser (Debian/Ubuntu), proporcionar shim hacia xdg-open
if ! command -v sensible-browser &>/dev/null && command -v xdg-open &>/dev/null; then
  SHIM_DIR="/tmp/.ubnt-discovery-shim-$$"
  mkdir -p "$SHIM_DIR"
  ln -s "$(command -v xdg-open)" "$SHIM_DIR/sensible-browser"
  export PATH="$SHIM_DIR:$PATH"
  trap 'rm -rf "$SHIM_DIR"' EXIT
fi

java -jar "$SCRIPT_DIR/ubnt-discovery-v2.5.1.jar" "$@"

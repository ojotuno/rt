#!/bin/sh
# Install RT. PREFIX defaults to /usr/local (uses sudo when it is not writable).
#   ./install.sh                     -> /usr/local/lib/rt + /usr/local/bin/rt
#   PREFIX=$HOME/.local ./install.sh -> no sudo needed
set -e
cd "$(dirname "$0")"

PREFIX="${PREFIX:-/usr/local}"
LIBDIR="$PREFIX/lib/rt"
BINDIR="$PREFIX/bin"

if [ -f build.sh ]; then
    sh build.sh
fi

SUDO=""
if [ "$(id -u)" -ne 0 ] && ! { mkdir -p "$LIBDIR" "$BINDIR" 2>/dev/null && [ -w "$LIBDIR" ] && [ -w "$BINDIR" ]; }; then
    SUDO="sudo"
fi

echo "Installing RT into $LIBDIR ($BINDIR/rt)"
$SUDO rm -rf "$LIBDIR"
$SUDO mkdir -p "$LIBDIR" "$BINDIR"
$SUDO cp -R src/rt "$LIBDIR/"
$SUDO find "$LIBDIR" -name __pycache__ -type d -prune -exec rm -rf {} +

launcher="$(mktemp)"
sed "s|@LIBDIR@|$LIBDIR|" bin/rt > "$launcher"
$SUDO install -m 755 "$launcher" "$BINDIR/rt"
rm -f "$launcher"

# Default install: remove the layout used by old versions (/usr/bin/rt + /usr/local/src/rt).
if [ "$PREFIX" = "/usr/local" ]; then
    ROOT_SUDO=""
    [ "$(id -u)" -ne 0 ] && ROOT_SUDO="sudo"
    if [ -f /usr/bin/rt ] && grep -q "/usr/local/src/rt/rt.py" /usr/bin/rt; then
        $ROOT_SUDO rm -f /usr/bin/rt
    fi
    if [ -f /usr/local/src/rt/rt.py ]; then
        $ROOT_SUDO rm -rf /usr/local/src/rt
    fi
fi

echo "RT installed: $BINDIR/rt"

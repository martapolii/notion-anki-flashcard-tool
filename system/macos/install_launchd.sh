#!/bin/zsh

set -e

PROJECT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
PLIST_NAME="com.marta.notion-anki-sync.plist"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME"

mkdir -p "$HOME/Library/LaunchAgents"

sed "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
  "$PROJECT_DIR/$PLIST_NAME.template" > "$PLIST_PATH"

LAUNCH_DOMAIN="gui/$(id -u)"
LAUNCH_SERVICE="$LAUNCH_DOMAIN/com.marta.notion-anki-sync"

# Remove any older copy of this job before loading the current plist.
launchctl bootout "$LAUNCH_SERVICE" 2>/dev/null || true
launchctl bootstrap "$LAUNCH_DOMAIN" "$PLIST_PATH"
launchctl kickstart -k "$LAUNCH_SERVICE"

echo "Installed: $PLIST_PATH"
echo "Runs every 15 minutes while your Mac is logged in."

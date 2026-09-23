#!/bin/zsh

set -a
source "$(cd -- "$(dirname -- "$0")" && pwd)/.env"
set +a

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
PROJECT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
cd "$PROJECT_DIR" || exit 1
python3 anki_notion_sync.py >> "$PROJECT_DIR/anki-sync.log" 2>&1

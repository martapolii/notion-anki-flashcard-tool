# macOS system setup

This folder contains the macOS-only system that connects Notion to Anki.

The system does not generate flashcard content. The Notion Lecture Flashcard Generator creates Flashcards database rows. This system adds `Ready` rows, keeps `Imported` notes synchronized with Notion, deletes notes for `Rejected` rows, creates organized Anki decks, and syncs AnkiWeb.

## Requirements

- macOS
- Python 3
- Anki Desktop
- AnkiConnect installed and enabled in Anki Desktop
- A Notion internal integration with access to the Flashcards database
- An AnkiWeb account signed in within Anki Desktop

Anki Desktop must be running for AnkiConnect to accept cards. The Mac must be awake and online when the scheduled job runs.

## Configuration

Copy the template and edit the copy:

```bash
cp env.example .env
chmod 600 .env
```

Set at least:

```text
NOTION_TOKEN=your_internal_connection_token
NOTION_DATABASE_ID=your_flashcards_database_id
```

The Status select needs `Ready`, `Imported`, `Rejected`, and `Needs review` options. The sync uses `Needs review` when an imported note has disappeared from Anki. The `.env` file is private and must not be committed.

## Manual test

With Anki Desktop open:

```bash
set -a
source .env
set +a
python3 anki_notion_sync.py
```

The script checks `Ready`, `Imported`, and `Rejected` Notion rows and uses each page's stable `notionid_...` tag to find its Anki note. `Ready` creates a note if none exists, or updates the existing note, then changes the Notion status to `Imported`. The sync also updates existing `Imported` notes when their question, answer, Notion tags, or target deck changes in Notion, so you do not need to reset edited cards to `Ready`. It adds missing Notion tags and preserves tags it does not manage. `Rejected` deletes the matching Anki note(s) and leaves the Notion row rejected. An `Imported` row whose note is missing from Anki changes to `Needs review`; it is not recreated automatically. Set it to `Ready` to add it again.

Keep rejected rows in Notion: deleting a row outright removes the sync's way to identify and delete its Anki note. AnkiWeb syncing is requested after any Anki collection changes (add, update, or delete).

## macOS automation

For a LaunchAgent, keep the runtime outside protected folders such as `Documents`. A simple location is:

```text
~/notion-anki-sync
```

Copy the runtime files there, copy your private `.env`, then run:

```bash
chmod +x run_anki_sync.sh install_launchd.sh
./install_launchd.sh
```

The LaunchAgent checks every 15 minutes while the user is logged in.

## AnkiWeb and other devices

After an Anki collection change, the script calls AnkiConnect's AnkiWeb sync action when `ANKIWEB_AUTO_SYNC=true`.

Complete the initial sync manually on the Mac:

1. Sign in to the same AnkiWeb account used on the phone and Windows computer.
2. Click Anki's Sync button once.
3. Choose **Upload** only if the Mac collection is the authoritative collection.
4. Sign in to that same AnkiWeb account on the phone and Windows installations.
5. Enable automatic syncing in Windows Anki preferences if needed.

After that, new cards imported on the Mac are uploaded to AnkiWeb automatically. Anki clients generally sync when their collection is opened or closed. The Mac still needs to be awake, online, and running Anki Desktop for the Notion import and AnkiWeb upload to occur.

## Logs and troubleshooting

The script writes to `anki-sync.log`. The LaunchAgent writes to `anki-launchd.log` and `anki-launchd-error.log`.

Look for:

```text
IMPORTED:
UPDATED from Notion:
DELETED rejected card(s) from Anki:
SYNCED Anki collection changes to AnkiWeb.
```

If Anki reports a full-sync or collection conflict, resolve it manually after checking which device has the authoritative collection. Do not blindly choose Upload or Download.

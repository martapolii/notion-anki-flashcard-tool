# Notion → Anki Flashcard Tool

This project has two separate parts:

1. **Notion** creates academic flashcards from lecture and textbook summaries.
2. **A local computer system** imports those cards into Anki and syncs AnkiWeb.

The local sync system has implementations for both macOS and Windows. The Notion workflow is shared across both platforms.

## Documentation

### Notion workflow

- [Notion setup and replication](notion/agent-setup-and-replication.md) — the current source of truth for the Lecture Flashcard Generator agent, triggers, permissions, databases, and properties.
- [Notion AI transcript-summary instructions](notion/transcript-summary-instructions.md) — current Lecture, Project/Capstone, and Textbook summary instructions.
- [Agent instructions pointer](notion/agent-instructions.md) — points to the current instructions inside the replication document.

The files in [`notion/archive`](notion/archive) are historical versions and are not part of the current setup.

### Local system workflow

#### Mac

- [macOS system setup](system/macos/README.md) — Python, AnkiConnect, `.env`, LaunchAgent automation, AnkiWeb syncing, and troubleshooting.
- [`system/macos/anki_notion_sync.py`](system/macos/anki_notion_sync.py) — adds, updates, and rejects cards through AnkiConnect.
- [`system/macos/env.example`](system/macos/env.example) — safe configuration template.

#### Windows

- [Windows 11 system setup](system/windows/README.md) — Python, AnkiConnect, PowerShell, Task Scheduler automation, deck migration and cleanup, card status workflow, AnkiWeb syncing, and troubleshooting.
- [`system/windows/anki_notion_sync.py`](system/windows/anki_notion_sync.py) — adds, updates, and rejects cards through AnkiConnect.
- [`system/windows/env.example`](system/windows/env.example) — safe configuration template.

## High-level flow

```text
Notion AI transcript summaries
        ↓
Lecture Flashcard Generator agent
        ↓
Notion Flashcards database (Ready / Imported / Rejected)
        ↓
macOS LaunchAgent or Windows Task Scheduler
        + Python sync script
        ↓
Anki Desktop through AnkiConnect
        ↓
AnkiWeb
        ↓
Phone and Windows Anki clients
```

The Notion agent does not call Anki directly. The active Windows daily task reads `Ready` and `Rejected` rows through the Notion API. A weekly full check also reads `Imported` rows to reconcile deck placement and tags. `Ready` rows create Anki notes or update the Front/Back of their existing matching notes. Weekly checks of unchanged `Imported` rows preserve formatting done in Anki. `Rejected` rows are deleted from Anki. Stable Notion page tags prevent duplicate imports within one Anki collection. Collection changes are synced to AnkiWeb.

Run the scheduled Notion-to-Anki importer on **one computer only** for a given Notion database and AnkiWeb collection. If both the Mac and Windows importers run, each can add a `Ready` card to its local collection before either device syncs; AnkiWeb then merges the separately created notes, producing duplicates even though Notion has only one row. Keep AnkiWeb syncing enabled on your other devices, but disable their Notion import schedules.

Set an edited `Imported` row back to `Ready` when you want its Question or Answer changes sent to Anki; the next daily run applies them and restores `Imported`. The weekly full check reconciles deck placement and tags without replacing Anki Front/Back. If an `Imported` note is missing from Anki, the full check moves its Notion status to `Needs review` and does not recreate it automatically. A `Ready` row Anki refuses as a duplicate is moved to `Duplicate` rather than forcing a second note. Mark a row `Rejected` to remove its Anki note. Deleting a row outright in Notion does not communicate a deletion to the sync; mark it `Rejected` instead.

## Current Anki organization

Course codes remain lowercase. A card with `Anki Deck = comp307` and `Week = W1` is placed in:

```text
comp307::Week 1
```

A value such as `W1 (2)` still goes into the same weekly deck:

```text
comp307::Week 1
```

The active Windows importer also maps known chapter-only rows to their course
weeks. COMP255 chapters 6–8 map to weeks 6–8, and chapters 9–10 to week 9;
COMP307 chapters 7–9 map to weeks 7–9; COMP231 chapter 10 maps to week 6.
Rows without a known week are reported as errors for review instead of being
placed in a chapter or topic deck. The former `comp3231` course code is
normalized to `comp231`.

COMP307 abbreviation cards remain in their week decks and carry a
`comp307_abbreviations` tag. The saved `comp307::Abbreviations` filtered deck
can be rebuilt to study them together; emptying it returns them to their weeks.
The Windows import runs once daily at 8:00 p.m. local time.

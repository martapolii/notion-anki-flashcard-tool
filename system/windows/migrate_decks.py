#!/usr/bin/env python3
"""Preview or apply deck-only moves using the same mapping as the importer.

This script never changes Notion rows or Anki note fields. Apply mode requires
the expected move count from a fresh preview, so a changing collection cannot
silently produce a different migration.
"""

from __future__ import annotations

import argparse
import os
from collections import Counter, defaultdict
from pathlib import Path

import anki_notion_sync as sync


def load_env() -> None:
    env_file = Path(__file__).with_name(".env")
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")


def chunks(items: list[int], size: int = 200):
    for start in range(0, len(items), size):
        yield items[start:start + size]


def anki_notes() -> tuple[dict[str, list[dict]], dict[int, str]]:
    note_ids = sync.anki("findNotes", {"query": "tag:notion"})
    notes_by_tag: dict[str, list[dict]] = defaultdict(list)
    card_ids: list[int] = []
    for batch in chunks(note_ids):
        for note in sync.anki("notesInfo", {"notes": batch}):
            for tag in note.get("tags", []):
                if tag.startswith("notionid_"):
                    notes_by_tag[tag].append(note)
            card_ids.extend(note.get("cards", []))

    decks_by_card: dict[int, str] = {}
    for batch in chunks(card_ids):
        for deck_name, ids in sync.anki("getDecks", {"cards": batch}).items():
            for card_id in ids:
                decks_by_card[card_id] = deck_name
    return notes_by_tag, decks_by_card


def migration_plan() -> tuple[dict[str, list[int]], int, int, int, Counter[tuple[str, str]], set[int]]:
    pages = sync.query_sync_pages(sync.require_env("NOTION_DATABASE_ID"))
    notes_by_tag, decks_by_card = anki_notes()
    moves: dict[str, list[int]] = defaultdict(list)
    unchanged = missing = 0
    unresolved: Counter[tuple[str, str]] = Counter()
    abbreviation_notes: set[int] = set()
    eligible = {os.getenv("NOTION_READY_VALUE", "Ready"), os.getenv("NOTION_IMPORTED_VALUE", "Imported")}

    for page in pages:
        if sync.notion_property(page, os.getenv("NOTION_STATUS_PROPERTY", "Status")) not in eligible:
            continue
        notes = notes_by_tag.get(sync.page_id_tag(page), [])
        if not notes:
            missing += 1
            continue
        source_deck = sync.notion_property(page, os.getenv("NOTION_DECK_PROPERTY", "Anki Deck"))
        if any(part.strip().casefold() == "abbreviations" for part in source_deck.split("::")):
            abbreviation_notes.update(note["noteId"] for note in notes)
        try:
            target = sync.card_from_page(page)["deck"]
        except ValueError:
            unresolved[(sync.notion_property(page, "Class"), sync.notion_property(page, "Week"))] += 1
            continue
        for note in notes:
            for card_id in note.get("cards", []):
                current = decks_by_card.get(card_id)
                if current is None:
                    raise RuntimeError(f"Anki did not return a deck for card {card_id}")
                if current == target:
                    unchanged += 1
                else:
                    moves[target].append(card_id)

    return moves, unchanged, missing, len(pages), unresolved, abbreviation_notes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="move cards and sync AnkiWeb")
    parser.add_argument("--expect", type=int, help="expected move count from a fresh preview")
    args = parser.parse_args()
    if args.apply and args.expect is None:
        parser.error("--apply requires --expect from a fresh preview")

    load_env()
    os.environ["NOTION_SYNC_STATUS_VALUES"] = ",".join((
        os.getenv("NOTION_READY_VALUE", "Ready"),
        os.getenv("NOTION_IMPORTED_VALUE", "Imported"),
        os.getenv("NOTION_REJECTED_VALUE", "Rejected"),
    ))
    sync.NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")
    sync.ANKI_URL = os.getenv("ANKI_CONNECT_URL", "http://127.0.0.1:8765")
    sync.anki("version")
    moves, unchanged, missing, page_count, unresolved, abbreviation_notes = migration_plan()
    move_count = sum(len(ids) for ids in moves.values())
    print(f"Notion sync-status rows: {page_count}; deck moves: {move_count}; "
          f"already placed: {unchanged}; missing in Anki: {missing}; "
          f"abbreviation notes: {len(abbreviation_notes)}.")
    for target, ids in sorted(moves.items()):
        print(f"{target}: {len(ids)} card(s)")
    for (course, week), count in sorted(unresolved.items()):
        print(f"Unresolved {course} / {week or '(no week)'}: {count} card(s)")

    if not args.apply:
        print("Preview only; no changes made.")
        return 0
    if unresolved:
        raise SystemExit("Unresolved source weeks remain; no cards were moved.")
    if move_count != args.expect:
        raise SystemExit(f"Move count changed from {args.expect} to {move_count}; preview again.")

    for target, ids in sorted(moves.items()):
        sync.anki("createDeck", {"deck": target})
        for batch in chunks(ids, 100):
            sync.anki("changeDeck", {"cards": batch, "deck": target})
    if abbreviation_notes:
        for batch in chunks(sorted(abbreviation_notes)):
            sync.anki("addTags", {"notes": batch, "tags": "comp307_abbreviations"})
    if move_count or abbreviation_notes:
        sync.anki("sync")
    print(f"Moved {move_count} cards in place and synced AnkiWeb.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

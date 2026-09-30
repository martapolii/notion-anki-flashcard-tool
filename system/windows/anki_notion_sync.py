#!/usr/bin/env python3
"""Send Ready flashcards from a Notion database to Anki via AnkiConnect.

The script intentionally uses only Python's standard library.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from typing import Any, Callable


NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")
NOTION_API = "https://api.notion.com/v1"
ANKI_URL = os.getenv("ANKI_CONNECT_URL", "http://127.0.0.1:8765")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def request_json(url: str, method: str = "GET", body: dict[str, Any] | None = None,
                headers: dict[str, str] | None = None) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach {url}: {exc.reason}") from exc


def notion_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {require_env('NOTION_TOKEN')}",
        "Notion-Version": NOTION_VERSION,
    }


def plain_text(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(plain_text(item) for item in value)
    if isinstance(value, dict):
        if "plain_text" in value:
            return value["plain_text"] or ""
        if "text" in value:
            return plain_text(value["text"])
        if "content" in value:
            return value["content"] or ""
        if "name" in value:
            return value["name"] or ""
    return ""


def property_text(prop: dict[str, Any]) -> str:
    prop_type = prop.get("type")
    return plain_text(prop.get(prop_type))


def page_title(page: dict[str, Any]) -> str:
    for prop in page.get("properties", {}).values():
        if prop.get("type") == "title":
            return property_text(prop)
    return ""


def notion_property(page: dict[str, Any], name: str, default: str = "") -> str:
    prop = page.get("properties", {}).get(name)
    return default if prop is None else property_text(prop)


def query_sync_pages(database_id: str) -> list[dict[str, Any]]:
    url = f"{NOTION_API}/databases/{database_id}/query"
    statuses = [
        value.strip()
        for value in os.getenv("NOTION_SYNC_STATUS_VALUES", "Ready,Imported,Rejected").split(",")
        if value.strip()
    ]
    status_filters = [
        {
            "property": os.getenv("NOTION_STATUS_PROPERTY", "Status"),
            "select": {"equals": status},
        }
        for status in statuses
    ]
    body: dict[str, Any] = {
        "page_size": 100,
        "filter": status_filters[0] if len(status_filters) == 1 else {"or": status_filters},
    }
    results: list[dict[str, Any]] = []
    while True:
        response = request_json(url, "POST", body, notion_headers())
        results.extend(response.get("results", []))
        if not response.get("has_more"):
            return results
        body["start_cursor"] = response["next_cursor"]


def update_status(page_id: str, status: str) -> None:
    property_name = os.getenv("NOTION_STATUS_PROPERTY", "Status")
    body = {"properties": {property_name: {"select": {"name": status}}}}
    request_json(f"{NOTION_API}/pages/{page_id}", "PATCH", body, notion_headers())


def anki(action: str, params: dict[str, Any] | None = None) -> Any:
    response = request_json(
        ANKI_URL,
        "POST",
        {"action": action, "version": 6, "params": params or {}},
    )
    if response.get("error"):
        raise RuntimeError(f"AnkiConnect {action} failed: {response['error']}")
    return response.get("result")


def safe_tag(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_:-]+", "_", value.strip())
    return value.strip("_") or "untagged"


def week_label(value: str) -> str:
    """Normalize values such as 1, W1, W1 (2), and Week 1 to Week 1."""
    value = value.strip()
    match = re.search(r"(?:week|w)\s*[-_]?\s*(\d+)", value, re.IGNORECASE)
    if match:
        return f"Week {match.group(1)}"
    if value.isdigit():
        return f"Week {value}"
    return value


def session_number(value: str) -> str:
    """Extract the session number from W1 (2), Week 1 (2), etc."""
    match = re.search(r"(?:week|w)\s*[-_]?\s*\d+\s*\(\s*(\d+)\s*\)", value.strip(), re.IGNORECASE)
    return match.group(1) if match else ""


def base_deck_name(deck: str, class_name: str) -> str:
    """Prefer a populated deck, otherwise derive a lowercase code from Class."""
    value = (deck.strip() or class_name.strip()).lower()
    sectionless = re.fullmatch(r"([a-z0-9_-]+)\s*\([^)]*\)", value)
    return sectionless.group(1) if sectionless else value


def card_from_page(page: dict[str, Any]) -> dict[str, Any]:
    question = notion_property(page, os.getenv("NOTION_QUESTION_PROPERTY", "Question"))
    answer = notion_property(page, os.getenv("NOTION_ANSWER_PROPERTY", "Answer"))
    if not question:
        question = page_title(page)
    if not question or not answer:
        raise ValueError("Card needs a question/title and an Answer")

    page_id = page["id"].replace("-", "")
    class_name = notion_property(page, os.getenv("NOTION_CLASS_PROPERTY", "Class"), "Class")
    week = notion_property(page, os.getenv("NOTION_WEEK_PROPERTY", "Week"))
    topic = notion_property(page, os.getenv("NOTION_TOPIC_PROPERTY", "Topic"))
    deck = notion_property(page, os.getenv("NOTION_DECK_PROPERTY", "Anki Deck"))
    if not deck:
        deck = class_name or os.getenv("ANKI_DECK", "Notion Cards")
    # Course/deck names are intentionally lowercase in this workflow.
    deck = base_deck_name(deck, class_name)
    week_source = week or topic
    if os.getenv("ANKI_WEEK_SUBDECKS", "true").lower() in {"1", "true", "yes", "on"} and week_source:
        normalized_week = week_label(week_source)
        session = session_number(week) or session_number(topic)
        deck = f"{deck}::{normalized_week}"
        if session:
            deck += f"::Session {session}"
    tags = ["notion", safe_tag(class_name), "notionid_" + page_id]
    if week:
        tags.append("week_" + safe_tag(week))
    if topic:
        tags.append("topic_" + safe_tag(topic))
    return {"page_id": page["id"], "front": question, "back": answer,
            "deck": deck, "week": week, "tags": tags}


def stable_page_tag(card: dict[str, Any]) -> str:
    """Return the tag that uniquely identifies the source Notion page."""
    return next(tag for tag in card["tags"] if tag.startswith("notionid_"))


def page_id_tag(page: dict[str, Any]) -> str:
    """Build the stable Anki tag without requiring a valid question or answer."""
    return "notionid_" + page["id"].replace("-", "")


def note_field_value(note_info: dict[str, Any], name: str) -> str | None:
    field = note_info.get("fields", {}).get(name)
    return field.get("value") if isinstance(field, dict) else field


def update_existing_note(note_info: dict[str, Any], card: dict[str, Any],
                         before_mutation: Callable[[], None]) -> bool:
    """Mirror Notion content and deck placement while preserving user tags."""
    note_id = note_info["noteId"]
    changed = False
    fields = {}
    if note_field_value(note_info, "Front") != card["front"]:
        fields["Front"] = card["front"]
    if note_field_value(note_info, "Back") != card["back"]:
        fields["Back"] = card["back"]
    if fields:
        before_mutation()
        anki("updateNoteFields", {"note": {"id": note_id, "fields": fields}})
        changed = True

    existing_tags = set(note_info.get("tags", []))
    tags_to_add = [tag for tag in card["tags"] if tag not in existing_tags]
    if tags_to_add:
        before_mutation()
        anki("addTags", {"notes": [note_id], "tags": " ".join(tags_to_add)})
        changed = True

    card_ids = note_info.get("cards", [])
    if card_ids:
        current_decks = anki("getDecks", {"cards": card_ids})
        cards_to_move = [
            card_id
            for deck_name, deck_card_ids in current_decks.items()
            if deck_name != card["deck"]
            for card_id in deck_card_ids
        ]
        if cards_to_move:
            before_mutation()
            anki("createDeck", {"deck": card["deck"]})
            anki("changeDeck", {"cards": cards_to_move, "deck": card["deck"]})
            changed = True

    return changed


def sync() -> int:
    database_id = require_env("NOTION_DATABASE_ID")
    # This gives a clear error before modifying anything if Anki is not running.
    anki("version")
    pages = query_sync_pages(database_id)
    if not pages:
        print("No Notion cards with a configured sync status.")
        return 0

    added = 0
    updated = 0
    unchanged = 0
    deleted = 0
    missing = 0
    processed = 0
    sync_failed = False
    collection_changed = False

    def mark_collection_changed() -> None:
        nonlocal collection_changed
        collection_changed = True

    status_property = os.getenv("NOTION_STATUS_PROPERTY", "Status")
    ready_value = os.getenv("NOTION_READY_VALUE", "Ready")
    imported_value = os.getenv("NOTION_IMPORTED_VALUE", "Imported")
    rejected_value = os.getenv("NOTION_REJECTED_VALUE", "Rejected")
    missing_value = os.getenv("NOTION_MISSING_VALUE", "Needs review")

    for page in pages:
        try:
            status = notion_property(page, status_property)
            if status == rejected_value:
                note_ids = anki("findNotes", {"query": f"tag:{page_id_tag(page)}"})
                if note_ids:
                    # Rejected is an explicit Notion instruction to remove these notes.
                    collection_changed = True
                    anki("deleteNotes", {"notes": note_ids})
                    deleted += len(note_ids)
                    print(f"DELETED rejected card(s) from Anki: {page_title(page)[:80]}")
                else:
                    print(f"REJECTED; no matching Anki note: {page_title(page)[:80]}")
                processed += 1
                continue

            card = card_from_page(page)
            existing = anki("findNotes", {"query": f"tag:{stable_page_tag(card)}"})
            if existing:
                note_infos = anki("notesInfo", {"notes": existing})
                if not note_infos:
                    raise RuntimeError("Anki returned note IDs but no note details")
                note_changed = False
                for note_info in note_infos:
                    if update_existing_note(note_info, card, mark_collection_changed):
                        note_changed = True
                if note_changed:
                    collection_changed = True
                    updated += 1
                    print(f"UPDATED from Notion: {card['front'][:80]}")
                else:
                    unchanged += 1
                    print(f"UNCHANGED: {card['front'][:80]}")
                if status == ready_value:
                    update_status(card["page_id"], imported_value)
                processed += 1
                continue

            if status == imported_value:
                update_status(card["page_id"], missing_value)
                missing += 1
                print(f"MISSING in Anki; moved to {missing_value}: {card['front'][:80]}")
                processed += 1
                continue

            anki("createDeck", {"deck": card["deck"]})
            mark_collection_changed()
            anki("addNote", {"note": {
                "deckName": card["deck"],
                "modelName": os.getenv("ANKI_MODEL", "Basic"),
                "fields": {"Front": card["front"], "Back": card["back"]},
                "tags": card["tags"],
                "options": {"allowDuplicate": False, "duplicateScope": "deck"},
            }})
            update_status(card["page_id"], imported_value)
            print(f"IMPORTED: {card['front'][:80]}")
            added += 1
            processed += 1
        except Exception as exc:  # keep other cards moving, but report the failure
            print(f"ERROR on {page_title(page) or page['id']}: {exc}", file=sys.stderr)

    if collection_changed and os.getenv("ANKIWEB_AUTO_SYNC", "true").lower() in {"1", "true", "yes", "on"}:
        try:
            anki("sync")
            print("SYNCED Anki collection changes to AnkiWeb.")
        except Exception as exc:
            sync_failed = True
            print(f"ERROR syncing Anki collection to AnkiWeb: {exc}", file=sys.stderr)

    errors = len(pages) - processed
    print(
        f"Done. Added {added}; updated {updated}; deleted {deleted}; "
        f"unchanged {unchanged}; missing for review {missing}; errors {errors}; "
        f"total sync-status pages {len(pages)}."
    )
    return 0 if errors == 0 and not sync_failed else 1


if __name__ == "__main__":
    raise SystemExit(sync())

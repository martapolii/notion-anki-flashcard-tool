#!/usr/bin/env python3
"""Preview or remove obsolete empty decks after the course/week migration."""

from __future__ import annotations

import argparse
import re
from collections import Counter

import anki_notion_sync as sync


COURSES = {"comp231", "comp255", "comp303", "comp306", "comp307", "comp309"}
PRESERVE = {"Default", "Custom Study Session", "comp307::Abbreviations"}


def chunks(items: list[int], size: int = 200):
    for start in range(0, len(items), size):
        yield items[start:start + size]


def canonical(name: str) -> bool:
    if name in PRESERVE or name in COURSES:
        return True
    return any(re.fullmatch(re.escape(course) + r"::Week \d+", name) for course in COURSES)


def cleanup_plan() -> tuple[list[str], int]:
    names = sync.anki("deckNames")
    card_ids = sync.anki("findCards", {"query": ""})
    occupied: Counter[str] = Counter()
    for batch in chunks(card_ids):
        for deck, ids in sync.anki("getDecks", {"cards": batch}).items():
            occupied[deck] += len(ids)

    obsolete = sorted(name for name in names if not canonical(name))
    roots = [
        name for name in obsolete
        if not any(name.startswith(parent + "::") for parent in obsolete if parent != name)
    ]
    for root in roots:
        descendants = [name for name in names if name == root or name.startswith(root + "::")]
        if any(occupied[name] for name in descendants):
            raise RuntimeError(f"Refusing to remove {root}: it or a descendant contains cards")
    return roots, len(card_ids)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expect-roots", type=int)
    parser.add_argument("--expect-cards", type=int)
    args = parser.parse_args()
    if args.apply and (args.expect_roots is None or args.expect_cards is None):
        parser.error("--apply requires --expect-roots and --expect-cards from a fresh preview")

    roots, card_count = cleanup_plan()
    print(f"Cards: {card_count}; obsolete empty deck trees: {len(roots)}")
    for root in roots:
        print(root)
    if not args.apply:
        print("Preview only; no changes made.")
        return 0
    if len(roots) != args.expect_roots or card_count != args.expect_cards:
        raise SystemExit("Deck or card count changed; preview again.")

    if roots:
        sync.anki("deleteDecks", {"decks": roots, "cardsToo": True})
        remaining_cards = len(sync.anki("findCards", {"query": ""}))
        if remaining_cards != card_count:
            raise RuntimeError(f"Card count changed from {card_count} to {remaining_cards}")
        sync.anki("sync")
    print(f"Removed {len(roots)} empty deck trees; all {card_count} cards remain.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

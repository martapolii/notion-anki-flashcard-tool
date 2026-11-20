"""Derive a course/Week N Anki path from Notion's existing metadata."""

from __future__ import annotations

import re


COURSE_ALIASES = {"comp3231": "comp231"}
WEEK = re.compile(r"\b(?:week|w)\s*[-_]?\s*(\d+)\b", re.IGNORECASE)
CHAPTER = re.compile(r"\b(?:chapter|ch)\s*[-_]?\s*(\d+)\b", re.IGNORECASE)
CHAPTER_WEEKS = {
    "comp255": {6: 6, 7: 7, 8: 8, 9: 9, 10: 9},
    "comp307": {7: 7, 8: 8, 9: 9},
    "comp231": {10: 6},
}


def _course_code(value: str) -> str:
    root = value.split("::", 1)[0].strip().lower()
    sectionless = re.fullmatch(r"([a-z0-9_-]+)\s*\([^)]*\)", root)
    if sectionless:
        root = sectionless.group(1)
    return COURSE_ALIASES.get(root, root)


def normalized_deck_name(
    deck: str,
    class_name: str,
    week: str,
    topic: str,
    *,
    fallback: str = "Notion Cards",
    week_subdecks: bool = True,
) -> str:
    """Keep only course and week; reject rows whose course week is unknown."""
    course = _course_code(deck or class_name or fallback)
    class_course = _course_code(class_name) if class_name else ""
    if class_course and course != class_course:
        raise ValueError(f"Anki Deck course {course} conflicts with Class {class_course}")
    if not week_subdecks:
        return course

    source_week = WEEK.search(week) or WEEK.search(topic)
    if source_week:
        week_number = int(source_week.group(1))
    else:
        source_chapter = CHAPTER.search(week) or CHAPTER.search(deck) or CHAPTER.search(topic)
        chapter_number = int(source_chapter.group(1)) if source_chapter else None
        week_number = CHAPTER_WEEKS.get(course, {}).get(chapter_number)
        if week_number is None:
            raise ValueError("No course week is recorded or mapped for this card")

    deck_weeks = [int(match) for match in WEEK.findall(deck.split("::", 1)[1])] if "::" in deck else []
    if deck_weeks and week_number not in deck_weeks:
        raise ValueError(f"Anki Deck week conflicts with Week {week_number}")
    return f"{course}::Week {week_number}"

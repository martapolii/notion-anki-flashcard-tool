"""Render Notion card properties as safe, readable Anki HTML."""

from __future__ import annotations

import html
import re
from typing import Any
from urllib.parse import urlsplit


LIST_MARKER = re.compile(r"^\s*(?:(?P<bullet>[-•])|(?P<number>\d+[.)]))\s+")


def render_front(question: str, emphasis: str = "") -> str:
    """Bold only exact phrases explicitly named in Front Emphasis."""
    if re.search(r"\bA\.\s.*\s\|\s*B\.\s", question, re.S):
        question = re.sub(r"\s*\|\s*(?=[B-E]\.\s)", "\n", question)
        question = re.sub(r"\s+(?=A\.\s)", "\n", question, count=1)
    phrases = sorted({part.strip() for part in emphasis.splitlines() if part.strip()}, key=len, reverse=True)
    pattern = (re.compile(r"(?<!\w)(?:" + "|".join(re.escape(part) for part in phrases) + r")(?!\w)", re.IGNORECASE)
               if phrases else None)

    def render_line(line: str) -> str:
        if pattern is None:
            return html.escape(line)
        pieces = []
        last = 0
        for match in pattern.finditer(line):
            pieces.append(html.escape(line[last:match.start()]))
            pieces.append("<strong>" + html.escape(match.group()) + "</strong>")
            last = match.end()
        pieces.append(html.escape(line[last:]))
        return "".join(pieces)

    lines = question.splitlines()
    if len(lines) <= 1:
        return render_line(question)
    return (render_line(lines[0]) + '<div style="text-align:left; margin-top:0.75em">' +
            "".join('<div>' + render_line(line) + '</div>' for line in lines[1:]) + '</div>')


def _lines(rich_text: list[dict[str, Any]]) -> list[list[tuple[str, bool, str | None]]]:
    lines: list[list[tuple[str, bool, str | None]]] = [[]]
    for segment in rich_text:
        value = segment.get("plain_text")
        if value is None:
            value = (segment.get("text") or {}).get("content", "")
        bold = bool((segment.get("annotations") or {}).get("bold"))
        href = segment.get("href") or ((segment.get("text") or {}).get("link") or {}).get("url")
        if href and urlsplit(href).scheme not in {"http", "https", "mailto"}:
            href = None
        for character in value:
            if character == "\n":
                lines.append([])
            else:
                lines[-1].append((character, bold, href))
    return lines


def _render_chars(chars: list[tuple[str, bool, str | None]]) -> str:
    result = []
    for character, bold, href in chars:
        escaped = html.escape(character)
        if result and result[-1][0:2] == (bold, href):
            result[-1] = (bold, href, result[-1][2] + escaped)
        else:
            result.append((bold, href, escaped))
    output = []
    for bold, href, value in result:
        if bold:
            value = "<strong>" + value + "</strong>"
        if href:
            value = '<a href="' + html.escape(href, quote=True) + '">' + value + '</a>'
        output.append(value)
    return "".join(output)


def render_answer(rich_text: list[dict[str, Any]]) -> str:
    """Use Notion bold and explicit line markers; never split prose on commas."""
    output = ['<div style="text-align:left">']
    current_list = None
    for line in _lines(rich_text):
        raw = "".join(character for character, _, _ in line)
        marker = LIST_MARKER.match(raw)
        kind = "ul" if marker and marker.group("bullet") else "ol" if marker else None
        if kind != current_list:
            if current_list:
                output.append(f"</{current_list}>")
            if kind:
                output.append(f"<{kind}>")
            current_list = kind
        if not raw.strip():
            output.append("<br>")
        elif kind:
            output.append("<li>" + _render_chars(line[marker.end():]) + "</li>")
        else:
            output.append("<p>" + _render_chars(line) + "</p>")
    if current_list:
        output.append(f"</{current_list}>")
    output.append("</div>")
    return "".join(output)

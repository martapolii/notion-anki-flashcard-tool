import unittest
import os
from unittest.mock import patch

from deck_naming import normalized_deck_name
from anki_notion_sync import card_from_page, update_existing_note, sync


class DeckNamingTests(unittest.TestCase):
    def test_imported_abbreviation_keeps_week_home_and_filter_tag(self):
        page = {
            "id": "12345678-1234-1234-1234-123456789abc",
            "properties": {
                "Question": {"type": "rich_text", "rich_text": [{"plain_text": "What does X mean?"}]},
                "Answer": {"type": "rich_text", "rich_text": [{"plain_text": "Example"}]},
                "Class": {"type": "select", "select": {"name": "comp307(402)"}},
                "Week": {"type": "select", "select": {"name": "W3"}},
                "Anki Deck": {"type": "rich_text", "rich_text": [{"plain_text": "comp307::Abbreviations"}]},
            },
        }
        card = card_from_page(page)
        self.assertEqual(card["deck"], "comp307::Week 3")
        self.assertIn("comp307_abbreviations", card["tags"])

    def test_abbreviation_checkbox_tags_a_week_deck_card(self):
        page = {
            "id": "12345678-1234-1234-1234-123456789abc",
            "properties": {
                "Question": {"type": "rich_text", "rich_text": [{"plain_text": "What does X mean?"}]},
                "Answer": {"type": "rich_text", "rich_text": [{"plain_text": "Example"}]},
                "Class": {"type": "select", "select": {"name": "comp307(402)"}},
                "Week": {"type": "select", "select": {"name": "W3"}},
                "Anki Deck": {"type": "rich_text", "rich_text": [{"plain_text": "comp307::Week 3"}]},
                "Abbreviation": {"type": "checkbox", "checkbox": True},
            },
        }
        card = card_from_page(page)
        self.assertEqual(card["deck"], "comp307::Week 3")
        self.assertIn("comp307_abbreviations", card["tags"])

    def test_importer_does_not_pull_cards_out_of_abbreviation_filter(self):
        note = {"noteId": 7, "cards": [9], "tags": ["comp307_abbreviations"]}
        card = {"front": "Q", "back": "A", "deck": "comp307::Week 3",
                "tags": ["comp307_abbreviations"]}
        with patch("anki_notion_sync.anki", return_value={"comp307::Abbreviations": [9]}) as api:
            changed = update_existing_note(note, card, lambda: self.fail("Unexpected mutation"))
        self.assertFalse(changed)
        api.assert_called_once_with("getDecks", {"cards": [9]})

    def test_ready_update_sends_fields_but_imported_check_preserves_them(self):
        note = {"noteId": 7, "cards": [9], "tags": ["notion"],
                "fields": {"Front": {"value": "Old"}, "Back": {"value": "Old answer"}}}
        card = {"front": "New", "back": "New answer", "deck": "comp307::Week 3",
                "tags": ["notion"]}
        with patch("anki_notion_sync.anki", return_value={"comp307::Week 3": [9]}) as api:
            changed = update_existing_note(note, card, lambda: self.fail("Unexpected mutation"))
        self.assertFalse(changed)
        api.assert_called_once_with("getDecks", {"cards": [9]})

        mutations = []
        with patch("anki_notion_sync.anki", return_value={"comp307::Week 3": [9]}) as api:
            changed = update_existing_note(note, card, lambda: mutations.append(True), sync_fields=True)
        self.assertTrue(changed)
        self.assertEqual(len(mutations), 1)
        api.assert_any_call("updateNoteFields", {"note": {"id": 7,
            "fields": {"Front": "New", "Back": "New answer"}}})

    def test_ready_duplicate_is_marked_duplicate(self):
        page = {
            "id": "12345678-1234-1234-1234-123456789abc",
            "properties": {
                "Status": {"type": "select", "select": {"name": "Ready"}},
                "Question": {"type": "rich_text", "rich_text": [{"plain_text": "A question"}]},
                "Answer": {"type": "rich_text", "rich_text": [{"plain_text": "An answer"}]},
                "Class": {"type": "select", "select": {"name": "comp255(402)"}},
                "Week": {"type": "select", "select": {"name": "W2"}},
                "Anki Deck": {"type": "rich_text", "rich_text": [{"plain_text": "comp255"}]},
            },
        }
        def api(action, params=None):
            if action == "version":
                return 6
            if action == "findNotes":
                return []
            if action == "canAddNotes":
                return [False]
            self.fail(f"Unexpected Anki mutation: {action}")
        with patch.dict(os.environ, {"NOTION_DATABASE_ID": "test"}), \
             patch("anki_notion_sync.query_sync_pages", return_value=[page]), \
             patch("anki_notion_sync.anki", side_effect=api), \
             patch("anki_notion_sync.update_status") as update:
            self.assertEqual(sync(), 0)
        update.assert_called_once_with(page["id"], "Duplicate")

    def test_plain_course_and_week(self):
        self.assertEqual(
            normalized_deck_name("comp303", "comp303(402)", "W2", ""),
            "comp303::Week 2",
        )

    def test_existing_week_is_not_repeated(self):
        self.assertEqual(
            normalized_deck_name("comp307::Week 5", "comp307(402)", "W5", ""),
            "comp307::Week 5",
        )

    def test_sessions_are_combined_into_the_week(self):
        self.assertEqual(
            normalized_deck_name("comp303::Week 1", "comp303(402)", "W1 (2)", ""),
            "comp303::Week 1",
        )

    def test_chapters_use_the_course_week_mapping(self):
        self.assertEqual(
            normalized_deck_name("comp255::CH 10", "comp255(402)", "CH 10", ""),
            "comp255::Week 9",
        )
        self.assertEqual(
            normalized_deck_name("comp307::CH 7", "comp307(402)", "CH 7", ""),
            "comp307::Week 7",
        )
        self.assertEqual(
            normalized_deck_name("comp3231::CH 10", "comp3231(401)", "CH 10", ""),
            "comp231::Week 6",
        )

    def test_unmapped_chapter_needs_review(self):
        with self.assertRaisesRegex(ValueError, "No course week"):
            normalized_deck_name("comp307::CH 11", "comp307(402)", "CH 11", "")

    def test_abbreviations_with_week_go_under_that_week(self):
        self.assertEqual(
            normalized_deck_name("comp307::Abbreviations", "comp307(402)", "W3", ""),
            "comp307::Week 3",
        )

    def test_comp231_typo_is_corrected_in_deck_path(self):
        self.assertEqual(
            normalized_deck_name("comp3231::Week 7", "comp3231(401)", "W7", ""),
            "comp231::Week 7",
        )

    def test_conflicting_weeks_are_held_for_review(self):
        with self.assertRaisesRegex(ValueError, "conflicts"):
            normalized_deck_name("comp307::Week 5", "comp307(402)", "W6", "")

    def test_week_subdecks_can_be_disabled(self):
        self.assertEqual(
            normalized_deck_name("comp307", "comp307(402)", "W3", "", week_subdecks=False),
            "comp307",
        )


if __name__ == "__main__":
    unittest.main()

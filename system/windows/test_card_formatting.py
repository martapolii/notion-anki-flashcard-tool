import unittest

from anki_notion_sync import card_from_page
from card_formatting import render_answer, render_front


class CardFormattingTests(unittest.TestCase):
    def test_front_bolds_exact_phrases_and_escapes_code(self):
        self.assertEqual(
            render_front('What does docker exec -it <container_id> do?', 'docker exec -it <container_id>'),
            'What does <strong>docker exec -it &lt;container_id&gt;</strong> do?',
        )
        self.assertEqual(render_front('processes and process', 'process'),
                         'processes and <strong>process</strong>')

    def test_multiline_question_keeps_choices_on_separate_lines(self):
        self.assertEqual(render_front('Which item?\nA. First\nB. Second'),
                         'Which item?<div style="text-align:left; margin-top:0.75em"><div>A. First</div><div>B. Second</div></div>')

    def test_answer_renders_bold_and_both_list_types(self):
        rich = [
            {'plain_text': 'Steps:\n1. ', 'annotations': {'bold': False}},
            {'plain_text': 'Prepare', 'annotations': {'bold': True}},
            {'plain_text': ',\n2. Run <test>.\n- Review;', 'annotations': {'bold': False}},
        ]
        result = render_answer(rich)
        self.assertIn('<ol><li><strong>Prepare</strong>,</li><li>Run &lt;test&gt;.</li></ol>', result)
        self.assertIn('<ul><li>Review;</li></ul>', result)
        self.assertIn('style="text-align:left"', result)

    def test_importer_limits_rendering_to_weeks_eight_and_nine(self):
        def page(week):
            return {'id': '12345678-1234-1234-1234-123456789abc', 'properties': {
                'Question': {'type': 'title', 'title': [{'plain_text': 'What is a process?'}]},
                'Answer': {'type': 'rich_text', 'rich_text': [{'plain_text': '- First,\n- second.', 'annotations': {'bold': False}}]},
                'Class': {'type': 'rich_text', 'rich_text': [{'plain_text': 'comp309'}]},
                'Week': {'type': 'rich_text', 'rich_text': [{'plain_text': week}]},
                'Front Emphasis': {'type': 'rich_text', 'rich_text': [{'plain_text': 'process'}]},
            }}
        self.assertIn('<ul>', card_from_page(page('W8'))['back'])
        self.assertIn('<strong>process</strong>', card_from_page(page('W8'))['front'])
        self.assertEqual(card_from_page(page('W7'))['back'], '- First,\n- second.')


if __name__ == '__main__':
    unittest.main()

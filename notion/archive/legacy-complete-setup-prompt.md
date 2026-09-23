# Complete Notion setup prompt

Copy everything inside the block below into Notion Agent.

```text
I want to build a weekly flashcard workflow using my existing Notion course organization. Do not reorganize or duplicate my existing course pages, lecture topics, or transcript summaries.

## Existing workspace structure

- I have a Courses database with one page per course.
- Each course page contains course details, learning objectives, notes, related material, and Notion AI-generated transcript summaries.
- Each course has related Topics/Assignments records.
- Each topic record represents a lecture or assignment and has properties such as lecture/assignment, date, status, and mastery.
- A single lecture/topic page may contain multiple Notion AI-generated summaries, including a lecture transcript summary and one or more textbook-reading summaries.
- The summaries may include learning objectives, notes, definitions, core concepts, examples, code, and related material.
- Slides, PDFs, images, textbook notes, and code examples may also be attached or linked.

## Create the flashcards database

Create a new database named Flashcards with these properties:

- Question — title property
- Answer — rich text
- Class — rich text or select; use the lowercase course code, optionally with the section, such as `comp307(402)`
- Course Subject — rich text
- Week — rich text; preserve the exact lecture identifier, such as `W1`, `W2`, or `W1 (2)`
- Topic — rich text; use the title of the transcript summary or textbook summary the card came from, not merely the week/session label
- Source — relation to the relevant Topics/Assignments page if possible; otherwise use a URL or rich text
- Source Type — select with Lecture summary, Textbook reading, Lecture + textbook, Slide/PDF, Code, and Other
- Card Type — select with Definition, Concept, Process, Comparison, Formula, Example, Code, and Misconception
- Difficulty — select with Easy, Medium, and Hard
- Status — select with Draft, Ready, Imported, and Needs review
- Anki Deck — rich text; use the lowercase course code, such as `comp307`

Create these views:

- Ready for Anki — Status is Ready
- Needs Review — Status is Needs review
- Imported — Status is Imported
- By Course — grouped by Class
- By Week — grouped by Week
- By Source Type — grouped by Source Type

If practical, add a relation or rollup from Courses to Flashcards so each course page can show its flashcard count. Do not modify the existing course or Topics/Assignments properties except to add the flashcard-request properties listed below.

## Add request properties to Topics/Assignments

Add these properties to the existing Topics/Assignments database:

- Flashcard Request — select with Not requested, Requested, Complete, and Needs review
- Flashcard Request Date — date
- Flashcard Count — number

Do not generate any cards yet. First finish the database, properties, and views, then show me what was created and ask me to confirm.

## Flashcard-generation behavior

When I ask you to generate cards for a lecture/topic, or when a lecture/topic has Flashcard Request = Requested:

1. Read all relevant content on the lecture/topic page and its linked course page.
2. Identify every summary section on the page. A page may contain:
   - a lecture transcript summary;
   - one or more textbook-reading summaries;
   - definitions and core concepts;
   - examples, code, slides, PDFs, images, and related material.
3. Treat lecture and textbook summaries as equal, first-class study sources.
4. First synthesize all sources into one unified understanding of the week's material.
5. Then create a coherent set of active-recall flashcards from the combined material.
6. Explicitly test textbook-only definitions, terminology, core concepts, frameworks, examples, and distinctions. Do not use textbook material only as background or supplementation.
7. If lecture and textbook summaries explain the same concept, combine them into one stronger card or a small set of complementary cards rather than duplicating the concept.
8. If lecture and textbook material emphasize different aspects of the same concept, create complementary cards testing those different aspects.
9. Label each card's Source Type as Lecture summary, Textbook reading, or Lecture + textbook as appropriate. A textbook-only concept must remain clearly labeled as textbook-related.
10. Do not create cards from professor information, meeting times, credit hours, course administration, or other non-academic metadata.
11. Use slides, PDFs, images, code, and related material when they contain examinable information or clarify the summaries.
12. Use only the supplied course material. Do not invent facts or silently fill gaps from general knowledge.
13. Avoid duplicating cards already in the Flashcards database unless the new card tests a meaningfully different idea.

Create approximately 15–30 cards per lecture/topic, depending on the amount and importance of material. Prefer questions that ask me to explain, apply, compare, calculate, predict, identify, or trace something.

For programming material, include code-tracing, output-prediction, debugging, and concept cards.

For formulas, include variable meanings and a short application example.

Set these properties on every card:

- Class
- Course Subject
- Week
- Topic
- Source
- Source Type
- Card Type
- Difficulty
- Anki Deck, using the lowercase course code
- Preserve the exact week/session identifier in Week, such as `W1`, `W2`, or `W1 (2)`.
- Set Topic to the exact transcript-summary or textbook-summary title that supports the card. Do not set Topic to `W1`, `W2`, or another week label unless that is genuinely the summary title.
- Status = Ready

If Anki Deck cannot be populated for any reason, derive it from Class by taking the lowercase course code before the section in parentheses. For example, `comp306(402)` must produce `comp306`.

After generation:

- Set Flashcard Request = Complete.
- Set Flashcard Count to the number of cards created.
- If the material is insufficient or ambiguous, set Flashcard Request = Needs review and explain the issue instead of inventing cards.
- Report the number of cards created, the source pages used, the source types represented, and any gaps or review items.
```

## Manual steps I need to complete in Notion

Notion Agent may not be able to create page buttons or database templates. I will manually do the following:

1. Open the Topics/Assignments database.
2. Edit the database template used for lecture/topic pages, or add the button to each relevant existing lecture page.
3. Add a button block at the top called `Generate Flashcards`.
4. Configure it to:
   - set `Flashcard Request` to `Requested`;
   - set `Flashcard Request Date` to the current date/time;
   - show a confirmation message.
5. Test it on one lecture page only.

If the button cannot directly update the current page, create a Button database property called `Generate Flashcards` in the Topics/Assignments database and configure that property to set the same fields.

## Important source-handling rule

The lecture transcript summary and textbook summaries on the same page are all intended flashcard sources. The workflow must test both, merge overlapping concepts intelligently, and never omit textbook-only definitions or core concepts.
```

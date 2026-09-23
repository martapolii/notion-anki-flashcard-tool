# Notion AI Transcript Summary Instructions

## Introduction

These are custom instruction sets for **Notion AI transcript summaries**. Each set tells Notion AI how to turn a transcript into notes suited to a specific source or session:

- **Lecture** — coding lectures, technical classes, workshops, labs, and teaching sessions.
- **Project/Capstone Class** — sessions combining instructor guidance with team discussion or project work.
- **Textbook** — transcripts of textbooks or assigned readings.

Use the complete instruction set that matches the recording. Each set is self-contained, so repeated requirements are intentionally preserved rather than moved into a shared section.

## Contents

1. [Lecture instructions](#1-lecture-instructions)
2. [Project/Capstone Class instructions](#2-projectcapstone-class-instructions)
3. [Textbook instructions](#3-textbook-instructions)

---

---

# 1. Lecture Instructions

## Context

Use these instructions for coding lectures, classes, workshops, labs, and technical teaching sessions. Summarize the session as study notes—not as a business meeting recap—while retaining a clear **Action Items** section for assignments, deadlines, preparation, and follow-up work.

The **first line of every generated summary must be a descriptive H3 title based on the transcript**, formatted exactly as `### [specific title]`. Place it before every other heading, section, paragraph, or bullet. Never use a generic title such as “Meeting,” “Lecture,” “Class Notes,” or “Summary.” This requirement applies to the first line inside the summary; it may not rename the AI Meeting Notes block itself.

## Summary format

Summarize this class as clear, useful study notes rather than as business meeting notes.

Organize the summary by topic or concept rather than strictly following the transcript chronologically.

For each major topic:

- Explain the concept clearly and concisely.
- Preserve important definitions, terminology, rules, formulas, syntax, procedures, or frameworks.
- Include useful examples given by the professor.
- Capture explanations, analogies, demonstrations, or clarifications that make the concept easier to understand.
- Note important comparisons or distinctions between similar concepts.
- Connect related ideas where useful instead of treating every point as isolated.

When programming, code, algorithms, or technical demonstrations are discussed:

- Explain what the code or example is intended to demonstrate.
- Preserve important syntax, patterns, methods, classes, functions, commands, or algorithms.
- Describe the important logic or flow of the code.
- Include expected behavior or output when relevant.
- Capture common mistakes, edge cases, debugging advice, or implementation warnings mentioned by the professor.
- Do not reproduce large blocks of code unless the code itself is necessary to understand the lesson.

Pay special attention to anything the professor:

- Says is important.
- Repeats or strongly emphasizes.
- Says students should remember.
- Says will appear on a quiz, test, exam, lab, assignment, or project.
- Warns students commonly misunderstand or get wrong.
- Explains differently from the slides, textbook, or provided material.

Also capture:

- Questions asked by students when the professor's answer adds useful course information.
- Assignment, lab, quiz, test, project, or deadline information mentioned during class.
- Corrections or clarifications made to slides, readings, examples, instructions, or other course materials.
- Any resources, files, pages, examples, or references the professor specifically recommends reviewing.

Exclude:

- Small talk.
- Unrelated conversation.
- Repetitive discussion that adds no new information.
- Technical troubleshooting unrelated to the course content.

At the end, include:

## Key Takeaways

Summarize the most important concepts, skills, procedures, or applications from the class. Create a list of key words and their definitions.

## Professor Emphasis & Assessment Notes

Capture anything the professor specifically highlighted as important, testable, commonly misunderstood, worth remembering, or relevant to an upcoming quiz, test, exam, lab, assignment, or project. Include important deadlines or assessment instructions mentioned during class.

## Action Items

List concrete assignments, deadlines, required preparation, resources to review, and follow-up work. Include dates and submission requirements when stated. If no action items are supported by the transcript, write “None mentioned.”

Do not invent information that is not supported by the transcript. If part of the transcript is unclear, incomplete, or appears mistranscribed, flag it rather than guessing.

## Summary style

- Prefer clear headings and concise bullets, with short paragraphs when explanation is needed.
- Be detailed enough to support studying, but remove repetition that adds no new information.
- Use course-specific terminology accurately.
- Bold key terms, definitions, formulas, warnings, and deadlines sparingly.
- Preserve formulas and code syntax exactly when they are clear in the transcript.
- Exclude small talk, unrelated conversation, attendance chatter, and technical troubleshooting unless they affect the course content.
- Do not invent missing information. If audio is unclear or text appears mistranscribed, label it as unclear rather than guessing.
- Do not attribute a statement to a specific person unless the transcript supports that attribution.

---

# 2. Project/Capstone Class Instructions

## Instructions

Summarize this class as project-working notes rather than traditional lecture notes.

The class may contain a short instructor-led portion followed by team discussion or project work. Keep those parts separate.

The **first line of every generated summary must be a descriptive H3 title based on the transcript**, formatted exactly as `### [specific title]`. Place it before every other heading, section, paragraph, or bullet. Never use a generic title such as “Meeting,” “Lecture,” “Class Notes,” or “Summary.” This requirement applies to the first line inside the summary; it may not rename the AI Meeting Notes block itself.

## 1. Instructor / Deliverable Notes

Capture:

- Current deliverables, milestones, and submission requirements.
- Due dates or timeline changes mentioned.
- Rubric requirements or grading criteria.
- Required documents, diagrams, code, presentations, demonstrations, or other artifacts.
- Instructions about what must or must not be included.
- Clarifications the instructor gives about an assignment or deliverable.
- Examples of acceptable or unacceptable work.
- Anything the instructor emphasizes, repeats, warns about, or says teams commonly get wrong.
- Answers to student questions that clarify project requirements.
- Changes or corrections to previously provided instructions.

If the instructor discusses general concepts that are relevant to completing the project, summarize them briefly, but prioritize information that affects the team's work.

## 2. Team Discussion / Working Session

Capture meaningful project discussion, including:

### Decisions Made

- Technical decisions.
- Design or feature decisions.
- Scope changes.
- Workflow or process decisions.
- Any agreed-upon approach.

For each decision, include the reasoning when it is discussed.

### Tasks / Action Items

For every clearly assigned task, record:

- Task.
- Person responsible.
- Deadline or target date, if mentioned.
- Relevant dependency or prerequisite.

Do not assign ownership if the team did not explicitly assign it.

### Current Progress

- Work completed or reviewed during the session.
- Features, documents, designs, or other deliverables discussed as completed or in progress.

### Blockers / Risks

- Problems preventing progress.
- Technical issues.
- Missing information.
- Dependencies.
- Scheduling problems.
- Concerns raised by team members.

### Open Questions

Record questions that remain unresolved or require:

- Instructor clarification.
- Research.
- Team discussion.
- Testing.
- A future decision.

### Important Ideas / Suggestions

Capture proposed ideas that may affect the project, but clearly distinguish suggestions from decisions that the team actually agreed to.

## 3. End-of-Session Summary

End with:

### Key Outcomes

A concise summary of what was accomplished or decided.

### Action Items

A clean checklist of assigned tasks with owners and deadlines when known.

### Decisions

A concise list of confirmed decisions.

### Open Questions / Blockers

Anything that still needs to be resolved.

### Upcoming Deliverables

Any known deadlines, milestones, or required submissions discussed during the class.

Do not treat casual brainstorming as a confirmed decision.

Do not invent deadlines, task owners, decisions, or requirements that were not explicitly stated.

Exclude casual conversation, repeated discussion that adds no new information, and unrelated technical troubleshooting unless it affects the project.

---

# 3. Textbook Instructions

## Instructions

The **first line of every generated summary must be a descriptive H3 title based on the transcript or the stated chapter and title**, formatted exactly as `### [specific title]`. Place it before every other heading, section, paragraph, or bullet. Never use a generic title such as “Meeting,” “Lecture,” “Reading Notes,” or “Summary.” This requirement applies to the first line inside the summary; it may not rename the AI Meeting Notes block itself.

Turn this transcript of a textbook or assigned reading into concise, well-organized study notes.

The goal is to capture the important ideas I need to understand and review later without reproducing the reading in excessive detail.

Organize the notes by major topic using clear headings and subheadings.

For each topic:

- Summarize the main idea in a few concise bullet points.
- Include important definitions, terminology, rules, formulas, procedures, or concepts.
- Include examples only when they materially improve understanding.
- Capture important comparisons, distinctions, relationships, exceptions, or limitations.
- Preserve information that is necessary to understand how or why something works.
- Remove repetition, filler, long narrative explanations, and minor details that are not useful for studying.

When programming, code, algorithms, or technical material appears:

- Summarize what the example demonstrates.
- Include only the important logic, syntax, pattern, command, or takeaway.
- Mention important implementation details, limitations, edge cases, or common mistakes.
- Do not reproduce large blocks of code or describe every step unless necessary for understanding.

Prioritize:

- Core concepts and principles.
- Important terminology.
- Key processes or procedures.
- Important relationships between concepts.
- Useful examples.
- Exceptions, warnings, and limitations.
- Information that would be useful for quizzes, exams, labs, or assignments.

Avoid:

- Copying the reading too closely.
- Turning every sentence into a note.
- Repeating the same idea in multiple forms.
- Excessive historical or background detail unless it is important to the topic.
- Long paragraphs when a few concise bullets would communicate the same information.

At the end, include:

## Key Takeaways

A short summary of the most important concepts, relationships, skills, or procedures from the reading.

## Key Terms

Only include terms that are genuinely important to know, with brief definitions.

## Review / Follow-Up

Flag anything that seems unclear, incomplete, difficult, or potentially mistranscribed and should be checked against the textbook.

Keep the notes concise, scannable, and structured. Prefer short bullet points and clear subheadings over dense paragraphs.

Do not invent information that is not supported by the transcript. If something appears mistranscribed or incomplete, flag it instead of guessing.

---

# Source Pages

The source pages are private Notion pages in the author's workspace. Use the corresponding Lecture, Project/Capstone Class, and Textbook instruction pages in your own workspace.

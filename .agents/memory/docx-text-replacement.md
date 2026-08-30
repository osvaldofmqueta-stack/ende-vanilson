---
name: DOCX text replacement
description: Reliable handling of visible text in Word documents whose paragraphs are split across multiple runs.
---

For DOCX text edits, treat a paragraph's concatenated visible text as the replacement unit. Word commonly splits one sentence or title across several `w:t` runs, so matching or replacing only individual runs can miss content or leave stale fragments.

**Why:** A title or phrase can be visually continuous while being stored in multiple XML text nodes; run-level matching produced incomplete edits during document updating.

**How to apply:** Preserve the paragraph structure and formatting where possible, but identify target paragraphs from their concatenated `w:t` text and replace the visible paragraph content as a whole. Validate the resulting ZIP and XML before delivery.
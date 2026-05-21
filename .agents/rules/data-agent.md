# Data Agent Rule

- Never add scientific numeric data without provenance.
- Every data item must include source, DOI or URL, table/equation/page/figure, unit, valid range, review status, enabled flag, and notes.
- `review_status != verified_from_lee2020` must imply `enabled_by_default: false` unless a human explicitly approves otherwise.
- OCR-uncertain Lee data must be preserved as disabled placeholders with `OCR_CHECK_REQUIRED` in notes.
- External references are future-version work unless the user explicitly updates `ROADMAP.md`.
- Check reaction completeness against the original paper numbering before editing data. A single original reaction number can contain multiple product channels, and each channel must be represented as a separate record or an explicitly disabled placeholder.
- Preserve the original paper reaction number in each record whenever available, using fields such as `original_reaction_no` and `channel_id`.
- Keep the data hierarchy clean: `data/raw_sources/` stores source-nearest material, `data/staged/` stores extracted but not fully verified records, and `data/canonical/` stores human-reviewed records allowed for default use.
- Do not move records from `staged` to `canonical` without human review.

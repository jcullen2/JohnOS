# Lesson: Superhuman / email fetching

Hard-won; do not relearn.

- **Fetch by split** (Important / Pitch / Other / Calendar / Contact) via
  `list_threads` / `list_splits`. **Never bulk-fetch.**
- `query_email_and_calendar` **truncates newsletter bodies** — unusable for
  corpus work.
- `get_thread` returns ~15K-token HTML bodies. Don't bulk-fetch newsletters
  through it; it will blow the context budget.
- Sending is permanently capped at L1 (see standing-rules #1). Drafts stage only.

# Lesson: StrictlyVC ingestion

Bypass email entirely.

- Source: `newsletter.strictlyvc.com/sitemap.xml` → scrape the beehiiv pages.
- Parse funding sections by **walking h2/h3/p against the known heading list**.
- Tracking-redirect links inside email bodies **don't resolve** — never depend
  on them. Go to the sitemap.

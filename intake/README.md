# /intake — drop zone

Drop anything here you want the OS to process: a PDF, a link in a `.txt` or `.md`
file, a note, a screenshot. The nightly **intake** producer (4:00) drains this
folder, and also picks up emails the inbound producer routes over when the subject
starts with `intake:`.

Per item it: fetches/extracts the content → classifies it against
`/context/theses.md` → routes it (sourcing candidate · thesis signal, filed to
`/state/research/<thesis>/` · people-map update, staged L1 · priority-relevant →
DECIDE) → writes a one-line RAN receipt to the queue, then removes the file from
here (the receipt is the audit trail).

**Nothing is ever silently dropped.** If a link can't be fetched (X/Twitter often
blocks), the receipt asks you to paste the text and the item waits.

Runbook: `engine/producers/intake.md`. Config: `engine/config/intake.yaml`.

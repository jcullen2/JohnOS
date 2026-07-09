# Producer configs
*Spec §5: each producer has a config file here — a cadence, an autonomy level, a
write surface, and its sources. Config-driven (the digest pattern in
`/lessons/digest-pattern.md`), not hardcoded.*

One `<producer>.yaml` (or `.json`) per producer. Minimum keys:

```yaml
producer: inbound
cadence: "6:00,12:00,17:00"     # launchd times, inside the 4:00–6:15 batch for nightly ones
autonomy_level: L1               # must not exceed the cap in /context/autonomy.md
writes: [APPROVE, DECIDE, KNOW]  # the queue types this producer may emit
sources: []                      # feeds/connectors; keep the list here, not in code
triage_model: claude-haiku-4-5   # cheap first-pass filter (digest pattern)
notes: "Fetch by split, never bulk (/lessons/superhuman.md)."
```

Producers read `/context` for identity, rules, and their autonomy ceiling at run
time — never duplicate those facts into a config.

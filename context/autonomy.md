# Autonomy Table
*Per producer, per action-type. Ladder rules in FOUNDING_SPEC §7. The Friday
retro amends this; promotion requires 4 consecutive clean weeks in RAN plus an
explicit JC ruling logged to /lessons.*

Ladder: **L0** observe & report → **L1** stage for approval → **L2** act & report
in RAN → **L3** act silently.

| Producer  | Action-type                    | Level | Cap  |
|-----------|--------------------------------|-------|------|
| inbound   | drafts / archive batches       | L1    | L1   |
| inbound   | send                           | L0    | L1 🔒 |
| intake    | route / file to /state         | L2    | —    |
| intake    | people-map update              | L1    | L1   |
| sourcing  | signals / weekly rank          | L1    | —    |
| sourcing  | Affinity adds                  | L1    | L1   |
| news      | KNOW digest                    | L0    | —    |
| policy    | KNOW digest                    | L0    | —    |
| thesis    | signal counters / synth DECIDE | L0    | —    |
| tasks     | /state/tasks.json              | L2    | —    |
| network   | who-to-touch DECIDE            | L0    | —    |
| network   | staged drafts                  | L1    | L1 🔒 |
| finance   | everything                     | L0    | L0 🔒 |
| sports    | all                            | L0    | —    |
| learn     | all                            | L0    | —    |
| leisure   | all                            | L0    | —    |
| retro     | staged change-list             | L1    | L1   |
| daily     | render queue as artifact       | L0    | L0   |

## Permanent caps (🔒 — never promotable)

- **The system sends nothing, ever, at any level** (standing-rule #0). There is no
  send action in this table and no level that grants one — not email, not
  send-to-self, not any channel. Drafts stage only; staging is not sending. The
  review plane is Claude rendering the queue, never a push.
- Anything **touching money** → L0. No trades, no transfers, ever, at any level.
- **Network / LP outreach** → L1 max, staged only. Outreach never automates.
- **CRM destructive edits** → L1 max.

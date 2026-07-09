# Schedules (launchd)
*Spec §8: producers run headless in the 4:00–6:15 batch window so the Daily is
ready at 6:30. Claude Code / launchd owns `/engine`; Cowork owns judgment-bearing
passes.*

## Install
```bash
bash engine/schedule/install.sh      # rewrites paths, loads every *.plist
launchctl list | grep com.jc.os      # verify
```
`install.sh` substitutes `__OS_ROOT__` with this repo's absolute path into
`~/Library/LaunchAgents/` and loads each job. Re-run after editing any plist.

## The Daily (`com.jc.os.daily.plist`)
Runs `render_daily.py` at **6:30** daily. Reads open `/queue` items, writes
`/daily/<date>.html` + `.md`. Pure Python, no network, no LLM — reliable and free.
Logs: `engine/schedule/daily.{out,err}.log` (gitignored).

## Adding a producer job (Session 2+)
Producers write queue items **before 6:15** so the Daily sees them. One plist per
producer; stagger start times inside the window so they don't contend.

1. Copy `com.jc.os.daily.plist` → `com.jc.os.<producer>.plist`.
2. Point `ProgramArguments` at the producer entrypoint
   (e.g. `engine/producers/inbound.py`).
3. Set `StartCalendarInterval` inside **4:00–6:15**. Suggested cadence:

   | Producer  | Time(s)                | Notes                                  |
   |-----------|------------------------|----------------------------------------|
   | inbound   | 6:00 (+ 12:00, 17:00)  | intraday passes render deltas too      |
   | sourcing  | 4:15 nightly; Mon rank | Monday adds the ranked top-5 DECIDE     |
   | thesis    | 4:30                   | signal counts → /state                  |
   | tasks     | 4:45                   | nightly sweep → /state/tasks.json       |
   | lp        | 5:00 (weekly)          | decay alerts                            |
   | finance   | 5:15 (25th + alerts)   | instrumentation only                    |
   | political | 5:30                   | cross-spectrum                          |
   | sports    | in-season, event-driven| KNOW only                               |
   | fun       | Thu 5:45               | suggestions                             |

4. `bash engine/schedule/install.sh` to load it.
5. A producer that fails must not block the Daily — the renderer just notes it silent.

The **Friday retro** (Cowork, 16:00) is not a launchd job — it runs in Cowork
pointed at `/os`. See spec §5.

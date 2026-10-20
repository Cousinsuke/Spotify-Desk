# ChatGPT project continuation workflow — Spotify Desk

Copy this file into a new ChatGPT conversation as the project continuation instruction, or ask ChatGPT to open it directly through the connected GitHub repository.

**Repository:** `Cousinsuke/Spotify-Desk`
**Working systems:** Windows 11 and Omarchy/Arch Linux
**Goal:** portable Spotify music controller with 800 × 480 screen, optional PC companion and future ESP32-S3 physical controls.

## 1. Load project state first

Before implementing anything:
1. Retrieve repository metadata and determine the **current active development branch**, rather than assuming `main` or an old remembered branch.
2. If `docs/CHATGPT-HANDOFF.md` exists, read it first.
3. Read referenced `docs/ROADMAP.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md` and relevant hardware/design docs.
4. Inspect **actual current code** in the relevant area.
5. Compare the newest branch HEAD/commits against the handoff's latest source checkpoint. Inspect meaningful later commits.
6. Use recent Spotify Desk conversation history only if the repository cannot resolve intent, chronology or acceptance.
7. Do **not** rebuild the entire state from old chats or memory when repository code and commits answer the question.

If the handoff is stale, identify what changed after its checkpoint, what those commits implemented, and whether runtime validation has happened.

## 2. Separate project phase from actual work

The *current project phase* is the roadmap stage (e.g. Phase 6 hardware design).
The *current actual work* may instead be an ad-hoc browser polish task, missing album art, Spotify volume regression, pairing bug, SSH/Omarchy test, backend optimization or new hardware experiment.

Never invent phase or item numbers merely to categorize ad-hoc work.

## 3. Determine the true latest task

Use handoff **and** commits newer than its checkpoint to identify:
- actual current work and its purpose;
- last user-confirmed/accepted task (regardless of roadmap entry);
- work implemented but pending actual runtime validation;
- next intended work.

A newly committed test is not proof of successful actual Windows, Omarchy or ESP32 runtime behavior.

## 4. Source-of-truth priority

**For implementation truth:** current branch code → newest relevant commits → handoff → roadmap/decisions → recent conversation → old memory.

**For chronology / task status:** handoff + post-checkpoint commits → recent commits → current docs → relevant recent user acceptance.

Do not use older ZIP descriptions to override newer actual source. During the initial empty-repo bootstrap only, Phase 5.2's validated ZIP is a transitional baseline, explicitly documented as such.

## 5. Protect accepted work

Before editing a component, inspect current implementation and related commits. Preserve:
- the accepted 800 × 480 screen, controls and album-reactive glow;
- Spotify Wi-Fi and PC modes;
- fast native media controls / sensible skip feedback;
- Spotify/SYSTEM volume synchronization and mismatched-track safeguards;
- four simulated keys, encoder and pairing state;
- platform-specific Windows and Linux functionality;
- Phase 5.2 artwork retry and proxy behavior.

Never rebuild or replace a working UI just because its parent phase is still open. Phase 5.0 briefly diverged from the established UI; Phase 5.1 restored it. Treat that regression as a reason to inspect before changing.

## 6. Handoff bootstrap

If `docs/CHATGPT-HANDOFF.md` does not exist, bootstrap it from repository docs, source and recent commits. Record active branch, phase, current actual task (roadmap/ad-hoc), implementation checkpoint, latest user-accepted work, pending validation, next action, unresolved issues, architecture, platform-test state, deferred work and workflow rules. Do not claim nonexistent validation.

## 7. Update handoff for ad-hoc work

Record meaningful fixes and polish even when not on the roadmap: artwork failures, status-polling optimization, keyboard shortcuts, touch targets, visual changes, startup reliability, platform parity and other real tasks. Keep this file concise and current; use the changelog for longer history.

## 8. First response in a fresh conversation: read-only for implementation

On the **first response of a new Spotify Desk project conversation**:
- Verify active branch, current HEAD, handoff existence/currentness and newest relevant commits.
- Report current project phase, actual current work, roadmap vs ad-hoc classification, last accepted work, implemented-but-awaiting-validation work, next action and unresolved issues.
- State any code/documentation discrepancy or uncertain acceptance status.
- Do **not** change implementation code on this first turn. An initial missing handoff may be created as documentation bootstrap.
- Wait for user confirmation or instruction to continue. Don't give deployment commands unless current work is already awaiting runtime testing.

This rule is specifically for continuation conversations, not a reason to refuse the user's explicit current GitHub repository bootstrap request.

## 9. Four distinct completion states

- **Implemented:** source exists.
- **Statically validated:** syntax/tests/audit checks passed.
- **Runtime-tested:** run on actual Windows 11, Omarchy or physical ESP32 as appropriate.
- **Accepted:** user explicitly confirms the behaviour works.

Do not treat a `200` API response as proof that a speaker's volume or song actually changed. Do not mark a Windows patch accepted solely from an Omarchy test.

## 10. Platform rules

Supported desktop targets:
- **Windows 11:** Windows Media Control / pycaw / WASAPI and browser.
- **Omarchy / Arch Linux:** MPRIS/playerctl / PipeWire / wpctl and browser.
- **Future ESP32-S3:** firmware not yet written.

Protect both Windows and Omarchy. Some media/volume behaviour must be platform-specific; document intentional differences. Validate relevant changes on both platforms before calling them cross-platform complete. An SSH D-Bus session with no local MPRIS player is not necessarily a Wi-Fi Spotify API fault.

## 11. Hardware and reference-project rules

The planned hardware is **ESP32-S3, Waveshare 4.3-inch 800 × 480 touch screen, four owned mechanical MX switches, rotary encoder and printed case**. Do not assume a compatible display SKU, pin count, electrical wiring or form factor until a datasheet/schematic is checked.

Use external hardware examples and the user's original inspiration video for ideas, not as unverified pinouts. Do not copy unrelated TUF Linux compositor/Quickshell/Caelestia rules into this project.

Distinguish *Spotify Connect remote control* from *running Spotify audio playback directly on the MCU*. Investigate official API/SDK and token/security limitations before deciding that standalone is feasible.

## 12. GitHub implementation workflow

After user confirmation:
1. Read code, handoff, newest commits and relevant docs.
2. Make focused changes directly with GitHub read/write access; prefer repository edits over asking the user to retype implementation.
3. Use the active development branch. Preserve accepted behaviour and update tests.
4. Commit changes; give commit/ref or PR link.
5. Provide compact commands for Windows PowerShell or SSH-to-Omarchy as appropriate: pull, install changed dependencies, run tests, start server, verify.
6. If a runtime dependency or source artifact cannot be accessed through the connector, say so accurately. Do not pretend the contents were uploaded.

Never commit OAuth tokens, bearer tokens, local configuration, `.venv`, debug logs, captured raw audio, Wi-Fi credentials or passwords. Never expose prototype port 8888 to the public internet.

## 13. Documentation after user acceptance

Once user accepts work, update relevant repository files **yourself**:
- `docs/CHATGPT-HANDOFF.md` (every meaningful task);
- `docs/CHANGELOG.md` (releases/important ad-hoc fixes);
- `docs/ROADMAP.md` when a real roadmap item changed;
- `docs/DECISIONS.md` for actual design/architecture decisions;
- `README.md`/INSTALL/TESTING/HARDWARE when user-facing truth changed.

Do not ask user to manually edit Markdown if GitHub connector can do it. A documentation update isn't evidence of platform runtime acceptance.

## 14. Keep checkpoint and history accurate

Handoff should contain:
- `Active development branch: <actual branch>`
- `Latest implementation checkpoint: <actual code commit SHA>`
- `Last accepted: <actual user-accepted task/environment>`
- `Pending validation: <exact environment/check>`
- `Next intended work: <specific task>`

After a new commit, compare HEAD to checkpoint; inspect post-checkpoint source changes and update the handoff accordingly. Documentation-only commits are fine but never claim to be new source checkpoints.

Use Git history and releases/tags to preserve versions. Avoid duplicate version directories full of stale code.

## 15. Keep continuation efficient

Prefer:
`docs/CHATGPT-HANDOFF.md` → newer commits → relevant current docs → relevant current code → necessary recent conversation.

Avoid exhaustive searches of old chats. Ask a direct question only if a missing decision materially blocks safe progress. The goal is that GitHub and this handoff are enough to resume the Spotify Desk project from its **real latest state**, whether the task is firmware, Linux, Windows, network security, UI polish or an unrelated bug fix.

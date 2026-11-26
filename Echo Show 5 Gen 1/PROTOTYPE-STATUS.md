# Prototype status — 2026-11-26

Branch: [echo-show/prototype](https://github.com/Cousinsuke/Spotify-Desk/tree/echo-show/prototype)
First code commit: [fceb865](https://github.com/Cousinsuke/Spotify-Desk/commit/fceb8653d337645ac9df93ec17c162c3b9cd7024).
The first increment is intentionally isolated in Echo Show 5 Gen 1/prototype/; root application, CAD and Pi are unchanged. Main stores design docs.

## Run on Omarchy

From an existing clean checkout (check git status; do not discard user changes):

```bash
cd ~/Projects/Spotify-Desk
git status --short
git fetch origin
git worktree add ~/Projects/Spotify-Desk-Echo-Prototype -b echo-show-preview-local origin/echo-show/prototype
cd ~/Projects/Spotify-Desk-Echo-Prototype
python3 -m http.server 8765 --bind 127.0.0.1 --directory "Echo Show 5 Gen 1/prototype"
```

Use a different worktree path/branch if already present; do not overwrite. Open http://127.0.0.1:8765/ in browser. Use 960 x 480 responsive viewport at 100% zoom if desired. Ctrl+C stops server. To update later, fetch and fast-forward the local preview branch; check status first.

## Implemented in first increment

Home clock and synthetic widgets; right-side rail, default 10s hide and per-page settings, reflow and arrow/edge swipe handlers; Apps drawer; General/Navigation settings shell; top-edge swipe quick settings and click fallback; Graphite/Black, rail styles and opacity, animation options, preview-only dimming, manual night mode, non-sensitive local preference cache and reset. Home on reload.

## Pending/limitations

Source JS parse passed using read-back; branch head verified. No runtime/browser or hardware test. Gesture/touch-action and focus/timer behavior require validation, particularly native Android notification shade interactions. Other dashboard views currently labelled planned, no service connection. App-specific quick settings, pin/reorder, schedule, full settings, Pi-backed preferences and calendar/system information not implemented. Brightness is CSS dimming only, no hardware backlight or keep-awake integration. No actual CGM readings or credentials, no live network data. No Pi changes.

## First user review

1. Home layout at 960 x 480; clock and sample tiles.
2. Rail hides after 10 seconds when not focused/overlay open; arrow and inward swipe reveal, no automatic page switch.
3. Apps opens right drawer; dismiss outside/close or select Settings.
4. Swipe down from top or click small top handle; theme and preview brightness apply.
5. Settings General/Navigation: opacity, rail style, auto-hide, reset. Reload returns Home.
6. Report layout/interaction problems; do not share private readings or credentials.

Next increment: Spotify, Weather and Glucose pages with shared shell and existing chart renderer, then expand context controls/settings. Pi preflight can run in parallel; do not wipe old data.

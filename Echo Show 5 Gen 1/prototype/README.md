# Echo Show 5 browser prototype — increment 1

Static, offline-only UI shell; no service connection, credentials, actual CGM data, firmware changes, real playback or hardware backlight control. All sample data is fabricated. Existing root application is unchanged.

Run on Omarchy from the repository root:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory "Echo Show 5 Gen 1/prototype"
```

Open http://127.0.0.1:8765/ in a desktop browser. Designed for 960 x 480 at 100% zoom; use browser responsive mode if needed. Ctrl+C stops the server.

Implemented: Home with three sample widgets and real local clock; right rail with 10-second default auto-hide and reflow, arrow/edge swipe reveal, Apps drawer with outside/close/select dismissal, Settings Centre shell with General/Navigation controls, top-edge swipe-down quick settings (click top handle for desktop), Graphite/Black, rail appearance, opacity, animation, timeout, per-page hide, preview brightness dimming, manual preview night mode, preference-only local storage and reset. Home always opens on reload. Scheduled night mode is a labelled planned setting, not active. Calendar/System and Spotify/Weather/Glucose are labelled planned destinations, not implemented. Contextual quick settings currently share general controls; app-specific controls and pin/reorder are pending. No Pi preference server yet.

Validation required: browser layout and gestures, accessibility, timer/focus behavior, actual device resource use; no browser/device test has been performed in this commit. Run node --check app.js if Node is installed. Use synthetic data only. Next: full Spotify, Weather and Glucose pages using existing chart renderer, then expanded settings and app registry.

'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const app=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');
const css=fs.readFileSync(path.join(__dirname,'style.css'),'utf8');
const live=fs.readFileSync(path.join(__dirname,'spotify-live.js'),'utf8');
for(const part of [
  "screen.querySelectorAll('select')",
  'select.hidden=true;select.tabIndex=-1',
  "select.dispatchEvent(new Event('change',{bubbles:true}))",
  "button.disabled=option.disabled",
  "panel.setAttribute('aria-modal','true')",
  "e.key==='Escape'",
  "current.trigger.focus({preventScroll:true})",
  'themedSelectObserver.observe(screen',
  'weatherRenderDeferred=true',
  "active==='spotify'?2000:5000",
  "select.hasAttribute('data-mode')",
])assert.ok(app.includes(part),part);
assert.ok(css.includes('-webkit-tap-highlight-color:transparent'));
assert.ok(css.includes('[data-input=touch] button:focus'));
assert.ok(css.includes('.themed-select-panel'));
assert.ok(live.includes('accept(s,s.sampleAgeMs)'));
new Function(app);new Function(live);
console.log('Themed select and playback integration source checks passed');

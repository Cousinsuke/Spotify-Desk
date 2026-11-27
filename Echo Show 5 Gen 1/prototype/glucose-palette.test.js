'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const css=fs.readFileSync(path.join(__dirname,'style.css'),'utf8'),js=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');
const rule=selector=>{const i=css.lastIndexOf(selector+'{');assert.ok(i>=0,selector);return css.slice(i+selector.length+1,css.indexOf('}',i));};
for(const b of ['range','low','above','high']){
 const r=rule('#screen[data-glucose-band='+b+']');assert.ok(r.includes('--glu-status-bg:'));assert.ok(r.includes('--glu-dynamic-bg:'));
}
const graph=rule('.glucose-graph'); // Last rule is position-only; check base separately.
assert.ok(css.includes('gap:8px;background:#252a30'));
assert.ok(rule('#glucosePlot .glu-trace').includes('stroke:#fff'));
assert.ok(rule('#glucosePlot .glu-label').includes('fill:#fff'));
assert.ok(rule('#screen[data-page=home] .tile[data-page=glucose]').includes('background:var(--glu-status-bg)'));
assert.ok(!rule('#screen[data-page=glucose][data-glucose-background=theme]').includes('--glu-status'));
assert.ok(!rule('#screen[data-page=glucose][data-glucose-background=theme][data-theme=black]').includes('--glu-status'));
assert.ok(rule('#screen[data-page=glucose][data-glucose-background=dynamic]').includes('--glu-bg:var(--glu-dynamic-bg)'));
assert.ok(js.slice(js.indexOf('function updateHomeGlucose(){'),js.indexOf('function glucoseAge(){')).includes('screen.dataset.glucoseBand=glucosePreview.theme(s.latest?.mmol,s.status)'));
console.log('Glucose palette source checks passed');

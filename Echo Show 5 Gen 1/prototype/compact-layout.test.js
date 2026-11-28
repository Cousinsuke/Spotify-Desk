'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const css=fs.readFileSync(path.join(__dirname,'style.css'),'utf8');
const start=css.indexOf('/* Compact landscape:');
assert.ok(start>=0);
const rules=css.slice(start);
for(const expected of [
  '(max-width:840px)','(max-height:420px)',
  '.weather-current{min-height:84px',
  '.forecast-day,.forecast-hours .hour-card{height:108px',
  '#weatherDetails{inset:14px 34px 24px;max-height:none;overflow-y:auto',
  '#weatherDetails .hourly-days{min-height:112px',
  'grid-template-columns:repeat(6,minmax(0,1fr))',
  '.cal-grid{grid-template-rows:20px repeat(6,minmax(0,1fr))}',
  '.sys-panel{padding:10px}',
  '#rail button{min-height:0}'
])assert.ok(rules.includes(expected),expected);
assert.ok(!rules.includes('data-page=glucose'));
assert.ok(!rules.includes('data-page=home'));
assert.ok(css.includes('.cal-agenda{background:'));
assert.ok(css.includes('overflow-y:auto;overflow-x:hidden'));
assert.ok(css.includes('#forecastDays,#weatherDetails #detailHours{'));
console.log('Compact layout source checks passed; verify actual bounds and scroll on device.');

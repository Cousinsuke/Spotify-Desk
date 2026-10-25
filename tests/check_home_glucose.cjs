'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const js = fs.readFileSync(path.join(__dirname, '../static/desk-dashboard.js'),'utf8');
const start = js.indexOf('  function updateHomeGlucose(');
const end = js.indexOf('  function historyLabel(', start);
assert.ok(start > 0 && end > start, 'production Home CGM renderer exists');

const makeElement = () => ({
  textContent:'', hidden:false, labels:{},
  setAttribute(name,value){this.labels[name]=value;}
});
const homeNumber = makeElement();
const homeArrow = makeElement();
const homeHint = makeElement();
const homeReading = makeElement();
const arrows = {
  DoubleUp:'↑↑', SingleUp:'↑', FortyFiveUp:'↗', Flat:'→',
  FortyFiveDown:'↘', SingleDown:'↓', DoubleDown:'↓↓'
};
const draw = new Function('glucoseHome','glucoseHomeArrow','glucoseHomeHint',
  'glucoseHomeReading','TREND_SYMBOLS',
  js.slice(start,end)+'\nreturn updateHomeGlucose;')(
    homeNumber,homeArrow,homeHint,homeReading,arrows);

draw('live',{mmol:5.2,direction:'Flat'},65);
assert.equal(homeNumber.textContent,'5.2','Home value has no unit suffix');
assert.equal(homeArrow.textContent,'→','Libreview Flat trend');
assert.equal(homeArrow.hidden,false);
assert.equal(homeHint.textContent,'Feed · 1m old');
assert.match(homeReading.labels['aria-label'],/millimoles per litre/);

draw('live',{mmol:5.2,direction:'DoubleUp'},120);
assert.equal(homeArrow.textContent,'↑↑','double-up trend is shown');

draw('live',{mmol:3.4,direction:'SingleDown'},90);
assert.equal(homeArrow.textContent,'↓','use reported direction, not absolute level');

draw('live',{mmol:6.6,direction:'Unknown'},30);
assert.equal(homeArrow.textContent,'','no fabricated direction');
assert.equal(homeArrow.hidden,true);

draw('stale',{mmol:4.8,direction:'Flat'},920);
assert.equal(homeNumber.textContent,'Not live');
assert.equal(homeArrow.hidden,true);
assert.equal(homeArrow.textContent,'');
assert.equal(homeHint.textContent,'Feed stale or unavailable');

draw('unavailable',null,undefined);
assert.equal(homeArrow.hidden,true);
assert.equal(homeNumber.textContent,'Not live');

console.log('Home glucose arrow, no-unit reading, stale and unknown-trend checks: OK');

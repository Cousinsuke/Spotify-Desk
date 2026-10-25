'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

// Execute the production weather renderer with a tiny fake DOM. This exercises
// the actual DOM card output without browser/network access.
const src = fs.readFileSync(path.join(__dirname, '../static/desk-dashboard.js'), 'utf8');
const begin = src.indexOf('  function updateWeatherUI() {');
const finish = src.indexOf('  async function refreshWeather()', begin);
assert.ok(begin >= 0 && finish > begin, 'weather renderer present');

class FakeElement {
  constructor(tag) { this.tagName = tag; this.children = []; this.textContent = ''; this.title = ''; }
  append(...els) { this.children.push(...els); }
  appendChild(el) { this.children.push(el); return el; }
  replaceChildren() { this.children = []; this.textContent = ''; }
  setAttribute(k, v) { this[k] = v; }
}
const fakeDocument = {createElement(tag) {return new FakeElement(tag);}};
const dailyElement = new FakeElement('div');
const values = {};
const fixture = {
  current: {
    temperature_2m:11.4, weather_code:0, apparent_temperature:9.2,
    relative_humidity_2m:65, wind_speed_10m:17, precipitation:0
  },
  daily: {
    time:['2026-10-25','2026-10-26','2026-10-27'],
    weather_code:[0,61,3],
    temperature_2m_max:[12.2,13.5,10.3],
    temperature_2m_min:[5.6,8.1,3.5],
    precipitation_probability_max:[5,80,40]
  }
};
const makeRender = new Function(
  'weather','WEATHER_LOCATION','condition','rounded','setText','finite','byId','document','weatherUpdated',
  src.slice(begin, finish) + '\nreturn updateWeatherUI;'
);
const getCondition = code => ({0:['Clear sky','☀'],61:['Rain','☂'],3:['Overcast','☁']}[code] || ['Unavailable','☁']);
const render = makeRender(
  {data:fixture},
  {name:'Bournemouth',country:'United Kingdom'},
  getCondition,
  (n,unit)=>Number.isFinite(n)?Math.round(n)+unit:'--'+unit,
  (id,value)=>values[id]=value,
  n=>typeof n==='number'&&Number.isFinite(n),
  id=>id==='deskDaily'?dailyElement:undefined,
  fakeDocument,
  new Date('2026-10-25T19:00:00Z').getTime()
);
render();
assert.equal(dailyElement.children.length,3,'three day cards');
assert.deepEqual(dailyElement.children.map(c=>c.children[0].textContent),['Today','Tomorrow','Tue']);
assert.deepEqual(dailyElement.children.map(c=>c.children[3].children[0].textContent),['12°','14°','10°']);
assert.deepEqual(dailyElement.children.map(c=>c.children[3].children[1].textContent),['6°','8°','4°']);
assert.deepEqual(dailyElement.children.map(c=>c.children[4].textContent),['5% rain','80% rain','40% rain']);
assert.equal(values.deskWeatherLocation,'Bournemouth, United Kingdom');
assert.equal(values.deskWeatherValue,'11°');
assert.equal(values.deskWeatherCondition,'Clear sky');
assert.ok(values.deskWeatherNote.includes('Refreshes every 15 minutes'));

// No daily data should give an explicit fallback without inventing forecast.
const renderWithoutDaily = makeRender(
  {data:{current:fixture.current}},
  {name:'Bournemouth',country:'United Kingdom'},
  getCondition, (n,u)=>Number.isFinite(n)?Math.round(n)+u:'--'+u,
  (id,value)=>values[id]=value,
  n=>typeof n==='number'&&Number.isFinite(n),
  id=>id==='deskDaily'?dailyElement:undefined,
  fakeDocument,
  new Date('2026-10-25T19:00:00Z').getTime()
);
renderWithoutDaily();
assert.equal(dailyElement.children.length,1);
assert.equal(dailyElement.children[0].textContent,'Daily forecast currently unavailable.');
console.log('Bournemouth 3-day forecast cards and missing-data fallback: OK');

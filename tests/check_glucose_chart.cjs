'use strict';
const assert=require('node:assert/strict');
const chart=require('../static/glucose-chart.js');
const end=new Date('2026-10-25T19:30:00Z').getTime();
const rows=[
 {timestamp:end-6*3600000,mmol:9.8},
 {timestamp:end-70*60000,mmol:7.6},
 {timestamp:end-50*60000,mmol:6.9},
 {timestamp:end-10*60000,mmol:4.6},
 {timestamp:end-5*60000,mmol:4.7}
];
for (const hours of [1,3,6,12,24]) {
  const rendered=chart.render(rows,{hours,endTime:end,scale:'auto'});
  assert.equal(rendered.rangeLow,4);
  assert.equal(rendered.rangeHigh,7);
  assert.equal(rendered.ticks.length,5);
  assert.ok(rendered.ticks.every(t=>/^\d{2}:\d{2}$/.test(t.label)),'real time labels');
  assert.match(rendered.svg,/fill-opacity=".13"/,'target shading');
  assert.match(rendered.svg,/>4\.0</,'target low');
  assert.match(rendered.svg,/>7\.0</,'target high');
  assert.ok(rendered.latest,'latest point included');
  assert.equal(rendered.latest.mmol,4.7);
}
const hour=chart.render(rows,{hours:1,endTime:end,scale:'auto'});
assert.equal(hour.points.length,3,'1h range filters old readings');
assert.equal(hour.segments.length,2,'missing data must break the line');
assert.equal(hour.ticks[4].label,'19:30');
const six=chart.render(rows,{hours:6,endTime:end,scale:'auto'});
assert.ok(six.bounds.high<13,'auto zoom must emphasize movement');
assert.ok(six.bounds.low<=4);
const full=chart.render(rows,{hours:6,endTime:end,scale:'fixed'});
assert.deepEqual(full.bounds,{low:0,high:40},'full scale contains all allowed readings');
assert.throws(()=>chart.render(rows,{hours:2,endTime:end}),/supported range/);
const none=chart.render([],{hours:3,endTime:end});
assert.equal(none.noData,true);
assert.equal(none.segments.length,0);
const dedup=chart.seriesWindow([...rows,{timestamp:end-5*60000,mmol:5.1}],3,end);
assert.equal(dedup[dedup.length-1].mmol,5.1);
console.log('Glucose chart geometry, target shading, time axis, ranges and gap checks: OK');

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
assert.equal(hour.ticks[4].label,
  new Intl.DateTimeFormat('en-GB',{hour:'2-digit',minute:'2-digit',hour12:false})
    .format(new Date(end)),'last tick should reflect local clock');
const six=chart.render(rows,{hours:6,endTime:end,scale:'auto'});
assert.ok(six.bounds.high<13,'auto zoom must emphasize movement');
assert.ok(six.bounds.low<=4);
const full=chart.render(rows,{hours:6,endTime:end,scale:'fixed'});
assert.deepEqual(full.bounds,{low:3,high:21},'Libre-style full graph should run from 3 to 21');
assert.deepEqual(full.yTicks,[3,6,9,12,15,18,21],'3 mmol/L tick spacing');
assert.match(full.svg,/>21</,'upper bound label');
assert.match(full.svg,/>3</,'lower bound label');
assert.doesNotMatch(full.svg,/>40(?:\\.0)?</,'old 40 mmol/L tick removed');
// Fixed mode must extend safely for exceptional readings, not crop them.
const veryHigh=chart.render([{timestamp:end-120000,mmol:25.4}],{hours:1,endTime:end,scale:'fixed'});
const veryLow=chart.render([{timestamp:end-120000,mmol:2.5}],{hours:1,endTime:end,scale:'fixed'});
assert.deepEqual(veryHigh.bounds,{low:3,high:27});
assert.deepEqual(veryLow.bounds,{low:0,high:21});
// Labels in AUTO cannot collide at 7.0 vs a nearby rounded centre tick.
for (const hours of [1,3,6,12,24]) {
  const c=chart.render(rows,{hours,endTime:end,scale:'auto'});
  const axisY = tick => 160-(tick-c.bounds.low)/(c.bounds.high-c.bounds.low)*144;
  for (let a=0;a<c.yTicks.length;a++) for (let b=a+1;b<c.yTicks.length;b++) {
    assert.ok(Math.abs(axisY(c.yTicks[a])-axisY(c.yTicks[b]))>=19.999,
      'AUTO y-axis label collision at '+c.yTicks[a]+'/'+c.yTicks[b]);
  }
}
const crowd=chart.render([{timestamp:end-5*60000,mmol:10.8},{timestamp:end-10*60000,mmol:4.8}],
  {hours:3,endTime:end,scale:'auto'});
assert.ok(crowd.yTicks.includes(7),'target 7.0 should take priority over nearby midpoint tick');
assert.ok(!crowd.yTicks.some((v,i)=>crowd.yTicks.slice(i+1).some(w=>Math.abs(crowd.bounds.high-crowd.bounds.low)>0 &&
  Math.abs(v-w)/(crowd.bounds.high-crowd.bounds.low)*144<19.999)),'no crowding in 3h AUTO');
assert.throws(()=>chart.render(rows,{hours:2,endTime:end}),/supported range/);
const none=chart.render([],{hours:3,endTime:end});
assert.equal(none.noData,true);
assert.equal(none.segments.length,0);
const dedup=chart.seriesWindow([...rows,{timestamp:end-5*60000,mmol:5.1}],3,end);
assert.equal(dedup[dedup.length-1].mmol,5.1);
console.log('Glucose chart 3-21 full scale, collision-free auto ticks, outliers and gaps: OK');

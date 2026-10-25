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
// In BOTH mode the chart is narrower than GRAPH mode, but its SVG
// coordinates should adapt instead of compressing the time and value labels.
const compact=chart.render(rows,{hours:3,endTime:end,scale:'auto',width:410});
const wide=chart.render(rows,{hours:3,endTime:end,scale:'auto',width:680});
assert.equal(compact.width,410);
assert.equal(wide.width,680);
assert.match(compact.svg,/width="410"/);
assert.match(wide.svg,/width="680"/);
assert.ok(compact.svg.includes('x2="388"'),'compact chart right edge should be width - 22');
assert.ok(wide.svg.includes('x2="658"'),'wide chart right edge should be width - 22');
assert.deepEqual(compact.yTicks,wide.yTicks,'layout does not alter actual glucose scale');
assert.equal(compact.points.length,wide.points.length,'layout does not filter readings');
assert.deepEqual(six.bounds,{low:3,high:12},'AUTO default is 3 to 12');
assert.deepEqual(six.yTicks,[3,4,7,9,12],'AUTO uses 3, target 4/7, and rounded reference ticks');
assert.match(six.svg,/>4\.0</,'target 4 keeps decimal');
assert.match(six.svg,/>7\.0</,'target 7 keeps decimal');
assert.match(six.svg,/>9</,'whole-number 9 reference');
assert.doesNotMatch(six.svg,/>9\.6</,'no fractional 9.6 label');
const autoLow=chart.render([{timestamp:end-120000,mmol:2.7}],
  {hours:3,endTime:end,scale:'auto'});
assert.deepEqual(autoLow.bounds,{low:2,high:12},'AUTO expands below 3 when needed');
const autoHigh=chart.render([{timestamp:end-120000,mmol:12.3}],
  {hours:3,endTime:end,scale:'auto'});
assert.deepEqual(autoHigh.bounds,{low:3,high:15},'AUTO expands beyond 12 when needed');
const autoExtreme=chart.render([{timestamp:end-120000,mmol:35.1}],
  {hours:3,endTime:end,scale:'auto'});
assert.deepEqual(autoExtreme.bounds,{low:3,high:36},'extreme actual reading remains visible');
const autoEmpty=chart.render([],{hours:1,endTime:end,scale:'auto'});
assert.deepEqual(autoEmpty.bounds,{low:3,high:12},'empty AUTO keeps the default scale');
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
for (const extreme of [veryHigh,veryLow,chart.render(
  [{timestamp:end-60000,mmol:40}],{hours:1,endTime:end,scale:'fixed'})]) {
  const y = tick => 160-(tick-extreme.bounds.low) /
    (extreme.bounds.high-extreme.bounds.low)*144;
  for (let i=1;i<extreme.yTicks.length;i++) {
    assert.ok(Math.abs(y(extreme.yTicks[i])-y(extreme.yTicks[i-1]))>=19.99,
      'extended full scale tick labels must not overlap');
  }
}
// Labels in AUTO cannot collide at 7.0 vs a nearby rounded centre tick.
for (const hours of [1,3,6,12,24]) {
  const c=chart.render(rows,{hours,endTime:end,scale:'auto'});
  const axisY = tick => 160-(tick-c.bounds.low)/(c.bounds.high-c.bounds.low)*144;
  for (let a=0;a<c.yTicks.length;a++) for (let b=a+1;b<c.yTicks.length;b++) {
    assert.ok(Math.abs(axisY(c.yTicks[a])-axisY(c.yTicks[b])) >=14.999,
      'AUTO y-axis label collision at '+c.yTicks[a]+'/'+c.yTicks[b]);
  }
}
const crowd=chart.render([{timestamp:end-5*60000,mmol:10.8},{timestamp:end-10*60000,mmol:4.8}],
  {hours:3,endTime:end,scale:'auto'});
assert.ok(crowd.yTicks.includes(7),'target 7.0 should take priority over nearby midpoint tick');
assert.ok(!crowd.yTicks.some((v,i)=>crowd.yTicks.slice(i+1).some(w=>Math.abs(crowd.bounds.high-crowd.bounds.low)>0 &&
  Math.abs(v-w)/(crowd.bounds.high-crowd.bounds.low)*144<14.999)),'no crowding in 3h AUTO');
assert.throws(()=>chart.render(rows,{hours:2,endTime:end}),/supported range/);
const none=chart.render([],{hours:3,endTime:end});
assert.equal(none.noData,true);
assert.equal(none.segments.length,0);
const dedup=chart.seriesWindow([...rows,{timestamp:end-5*60000,mmol:5.1}],3,end);
assert.equal(dedup[dedup.length-1].mmol,5.1);
console.log('Glucose graph: whole-number AUTO 3–12, dynamic extremes and 3–21 FULL scale: OK');

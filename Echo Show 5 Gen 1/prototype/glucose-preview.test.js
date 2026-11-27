'use strict';
const assert=require('node:assert/strict'),p=require('./glucose-preview.js'),c=require('./glucose-chart.js');
const now=Date.UTC(2026,0,1,12);
const s=p.make('range',now);
assert.equal(s.status,'sample');assert.equal(s.readings.length,289);
assert.equal(s.readings.at(-1).mmol,s.latest.mmol);
assert.equal(s.latest.timestamp,now-120000);
assert.equal(p.theme(3.9,'sample'),'low');assert.equal(p.theme(4,'sample'),'range');assert.equal(p.theme(7,'sample'),'range');assert.equal(p.theme(7.1,'sample'),'above');assert.equal(p.theme(15,'sample'),'high');assert.equal(p.theme(6,'stale'),'neutral');assert.equal(p.theme(NaN,'live'),'neutral');
for(const h of c.RANGES){const r=c.render(s.readings,{hours:h,endTime:now,scale:'auto',width:450});assert.ok(r.points.length>0);assert.ok(r.points.every(x=>x.timestamp>=now-h*3600000));}
assert.deepEqual(c.yBounds([],'auto'),{low:3,high:12});
assert.deepEqual(c.yBounds([],'fixed'),{low:3,high:21});
assert.equal(c.yBounds([{mmol:39}],'fixed').high,39);
assert.equal(c.yBounds([{mmol:2.2}],'auto').low,2);
assert.equal(c.geometry([{timestamp:now-3600000,mmol:5},{timestamp:now,mmol:6}],{hours:3,endTime:now,scale:'auto'}).segments.length,2);
assert.equal(c.seriesWindow([{timestamp:now,mmol:5},{timestamp:now,mmol:6}],1,now).length,1);
console.log('27 Glucose assertions passed');

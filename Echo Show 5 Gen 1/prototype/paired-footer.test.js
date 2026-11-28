'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const read=name=>fs.readFileSync(path.join(__dirname,name),'utf8');
const js=read('app.js'),css=read('style.css'),html=read('index.html');
assert.ok(css.includes('html[data-device-gateway="1"] #demo{display:none}'));
assert.ok(js.includes("dataset.deviceGateway==='1'?'':'LOCAL TEST · SECONDARY DISPLAY'"));
assert.ok(!js.includes('LIVE · PAIRED DISPLAY'));
assert.ok(html.includes('DESIGN PREVIEW · SAMPLE DATA'));
console.log('Paired display footer checks passed');

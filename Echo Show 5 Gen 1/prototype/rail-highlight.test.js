'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const read=name=>fs.readFileSync(path.join(__dirname,name),'utf8');
const js=read('app.js'),css=read('style.css');
const line=js.split('\n').find(line=>line.startsWith('function renderRail(){'));
assert.ok(line);
const rail={dataset:{},innerHTML:''};
const apps={home:'Home',spotify:'Spotify',weather:'Weather',glucose:'Glucose',settings:'Settings'};
const prefs={appLayout:{}};
const render=new Function('rail','apps','prefs','appRailIds','icon','active','overlay',line+';renderRail();');
for(const active of Object.keys(apps)){
  for(const overlay of [null,'drawer','quick','devices','weather']){
    render(rail,apps,prefs,()=>Object.keys(apps),()=>'',active,overlay);
    assert.equal(rail.dataset.drawerOpen,String(overlay==='drawer'));
    assert.equal((rail.innerHTML.match(/aria-current="page"/g)||[]).length,1);
    assert.ok(rail.innerHTML.includes('data-page="'+active+'" aria-label="'+apps[active]+'" aria-current="page"'));
    assert.ok(rail.innerHTML.includes('aria-label="Apps" aria-expanded="'+String(overlay==='drawer')+'"'));
    // The stylesheet suppresses current-page highlighting only for the drawer.
    const highlighted=Number(rail.dataset.drawerOpen!=='true')+Number(overlay==='drawer');
    assert.equal(highlighted,1);
  }
}
assert.ok(css.includes('#rail:not([data-drawer-open=true]) button[aria-current=page],#rail button[aria-expanded=true]{background:#53718b;color:white}'));
assert.ok(!css.includes('#rail button[aria-current=page],#rail button[aria-expanded=true]'));
assert.ok(js.includes('shade.hidden=true;renderRail();'));
assert.ok(js.includes("else{renderQuick()}renderRail();"));
console.log('Exclusive Apps drawer highlight checks passed');

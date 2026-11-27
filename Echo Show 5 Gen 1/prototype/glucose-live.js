(function(root){
'use strict';
const arrows={DoubleUp:'↑↑',SingleUp:'↑',FortyFiveUp:'↗',Flat:'→',FortyFiveDown:'↘',SingleDown:'↓',DoubleDown:'↓↓'};
const statuses=['loading','live','stale','unavailable','configuration_error','not_configured'];
const valid=p=>p&&Number.isFinite(p.timestamp)&&Number.isFinite(p.mmol)&&p.mmol>=.5&&p.mmol<=40;
function normalise(raw,now=Date.now()){
 const status=statuses.includes(raw?.status)?raw.status:'unavailable';
 if(['loading','unavailable','configuration_error','not_configured'].includes(status))return {status,latest:null,readings:[],endTime:now};
 const unique=new Map();
 for(const p of (Array.isArray(raw.readings)?raw.readings.slice(0,730):[])){
  if(valid(p)&&p.timestamp>=now-86400000&&p.timestamp<=now+120000)unique.set(p.timestamp,{timestamp:p.timestamp,mmol:p.mmol,direction:Object.prototype.hasOwnProperty.call(arrows,p.direction)?p.direction:null});
 }
 const rows=Array.from(unique.values()).sort((a,b)=>a.timestamp-b.timestamp);
 const latest=rows.at(-1);
 if(!latest)return {status:'unavailable',latest:null,readings:[],endTime:now};
 const age=Math.max(0,Math.floor((now-latest.timestamp)/1000));
 return {status:status==='live'&&age<600?'live':'stale',latest:{...latest,arrow:arrows[latest.direction]||''},readings:rows,endTime:now,ageSeconds:age};
}
function label(status){return ({loading:'CONNECTING GLUROO',live:'LIVE FEED',stale:'STALE · NOT LIVE',unavailable:'GLUCOSE UNAVAILABLE',configuration_error:'CHECK GLUROO CONFIGURATION',not_configured:'GLUROO NOT CONFIGURED',sample:'SAMPLE DATA · NOT LIVE'})[status]||'GLUCOSE UNAVAILABLE'}
const enabled=typeof location!=='undefined'&&new URLSearchParams(location.search).get('live')==='1';
let raw={status:'loading',readings:[]},busy=false,received=0;
const api={enabled,normalise,label,get data(){return normalise(received&&Date.now()-received>=60000&&raw.status==='live'?{...raw,status:'stale'}:raw)},onChange:null,
 async refresh(){
  if(!enabled||busy)return;
  busy=true;
  try{
   const r=await fetch('/api/glucose',{headers:{'X-Desk-Preview':'1'},cache:'no-store',credentials:'same-origin'});
   if(!r.ok)throw Error('unavailable');
   const data=await r.json();
   // Reject invalid or future data at receipt; do not let it become live later.
   raw=normalise(data);
   received=Date.now();
  }catch{raw={status:'unavailable',readings:[]}}
  finally{busy=false;api.onChange?.()}
 }};
if(typeof module==='object'&&module.exports)module.exports=api;else root.EchoGlucoseLive=api;
})(typeof globalThis!=='undefined'?globalThis:this);

(function(root){
'use strict';
const sample=root.EchoWeatherPreview;
const enabled=typeof location!=='undefined'&&new URLSearchParams(location.search).get('live')==='1';
const zone='Europe/London';
const fmt=new Intl.DateTimeFormat('en-GB',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit'});
const hh=new Intl.DateTimeFormat('en-GB',{timeZone:zone,hour:'2-digit',minute:'2-digit',hourCycle:'h23'});
function dayKey(ms){const p=fmt.formatToParts(new Date(ms));const get=k=>p.find(x=>x.type===k)?.value;return get('year')+'-'+get('month')+'-'+get('day')}
const num=v=>typeof v==='number'&&Number.isFinite(v)?Math.round(v):'--';
const time=v=>typeof v==='number'&&Number.isFinite(v)?hh.format(new Date(v*1000)):'--:--';
function condition(code,day=1){
 if(!Number.isFinite(code))return 'unknown';
 if(code===0)return day===0?'night':'clear';
 if(code===1||code===2)return day===0?'partlyNight':'partly';
 if(code===3)return 'cloud';
 if(code===45||code===48)return 'fog';
 if([71,73,75,77,85,86].includes(code))return 'snow';
 if(code>=95&&code<=99)return 'storm';
 if((code>=51&&code<=67)||(code>=80&&code<=82))return 'rain';
 return 'unknown';
}
function model(raw,now=Date.now()){
 const c=raw?.current,h=raw?.hourly,d=raw?.daily;
 if(!c||!Array.isArray(h?.time)||!Array.isArray(d?.time))return null;
 // Daily epoch boundaries use the API's fixed offset; hourly instants use London DST.
 const offset=Number(raw.utc_offset_seconds)||0,today=dayKey(now);
 const daily=d.time.map((t,i)=>({date:new Date((t+offset)*1000).toISOString().slice(0,10),condition:condition(d.weather_code[i]),high:num(d.temperature_2m_max[i]),low:num(d.temperature_2m_min[i]),rain:num(d.precipitation_probability_max[i]),sunrise:time(d.sunrise[i]),sunset:time(d.sunset[i])})).filter(x=>x.date>=today);
 const days=daily.slice(0,7);
 const hours=h.time.map((t,i)=>({timestamp:t*1000,day:days.findIndex(x=>x.date===dayKey(t*1000)),time:time(t),temp:num(h.temperature_2m[i]),rain:num(h.precipitation_probability[i]),condition:condition(h.weather_code[i],h.is_day[i])})).filter(x=>x.day>=0);
 const first=days[0]||{};
 return {days,hours,current:{temp:num(c.temperature_2m),feels:num(c.apparent_temperature),humidity:num(c.relative_humidity_2m),condition:condition(c.weather_code,c.is_day),rain:first.rain??'--',sunrise:first.sunrise??'--:--',sunset:first.sunset??'--:--',observed:c.time*1000}};
}
const empty={temp:'--',feels:'--',humidity:'--',condition:'unknown',rain:'--',sunrise:'--:--',sunset:'--:--'};
let payload=null,status='loading',updated=null,busy=false;
const api={...sample,enabled,condition,model,onChange:null,get status(){return enabled?status:'sample'},get current(){return model(payload)?.current||empty},get updated(){return updated},
 forecast(duration){return (model(payload)?.days||[]).slice(0,sample.validDuration(duration))},
 hourly(i,now=new Date()){const m=model(payload,now.getTime());return !m?[]:i===0?m.hours.filter(x=>x.timestamp>now.getTime()).slice(0,24):m.hours.filter(x=>x.day===i)},
 summary(i){const m=model(payload),d=m?.days[i];return !d?null:i===0?{...d,...m.current}:d},
 label(){return status==='fresh'?'Open-Meteo · '+hh.format(new Date(updated*1000)):status==='stale'?'Stale · '+hh.format(new Date(updated*1000)):status==='loading'?'Updating weather…':'Weather unavailable'},
 async refresh(){
  if(!enabled||busy)return;
  busy=true;
  try{
   const r=await fetch('/api/weather',{headers:{'X-Desk-Preview':'1'},cache:'no-store'});
   if(!r.ok)throw Error('weather unavailable');
   const x=await r.json();
   if(!['fresh','stale','loading','unavailable'].includes(x.status))throw Error('invalid response');
   const previous=updated,prior=status;
   payload=x.data||null;status=x.status;updated=x.updated;
   if(previous!==updated||prior!==status)api.onChange?.();
  }catch{const prior=status;payload=null;status='unavailable';updated=null;if(prior!==status)api.onChange?.()}
  finally{busy=false}
 }
};
if(typeof module==='object'&&module.exports)module.exports={model,condition};
else root.EchoWeatherLive=api;
})(typeof globalThis!=='undefined'?globalThis:this);

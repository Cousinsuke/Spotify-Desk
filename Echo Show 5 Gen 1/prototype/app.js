'use strict';
const $=id=>document.getElementById(id), screen=$('screen'), page=$('page'), rail=$('rail'), drawer=$('drawer'), quick=$('quick'), shade=$('shade'), reveal=$('reveal');
const apps={home:'Home',spotify:'Spotify',weather:'Weather',glucose:'Glucose',settings:'Settings',calendar:'Calendar',system:'System Information'};
const icons={home:'<path d="M3 10 12 3l9 7v10h-6v-7H9v7H3z"/>',spotify:'<circle cx="12" cy="12" r="10"/><path d="M6 9q6-3 12 1M7 13q5-2 10 1M8 16q4-1 8 1"/>',weather:'<path d="M6 19a5 5 0 0 1-1-10 7 7 0 0 1 13 1 4.5 4.5 0 0 1 0 9z"/>',glucose:'<path d="M12 2C8 8 4 12 4 16a8 8 0 0 0 16 0c0-4-4-8-8-14z"/>',settings:'<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 1v3M12 20v3M1 12h3M20 12h3M4 4l2 2M18 18l2 2M4 20l2-2M18 6l2-2"/>',calendar:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M7 2v6M17 2v6M7 14h3M14 14h3M7 18h3"/>',system:'<rect x="2" y="4" width="20" height="14" rx="2"/><path d="M8 22h8M12 18v4M5 11h4l2-4 3 8 2-4h3"/>',apps:'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>'};
const icon=id=>'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">'+icons[id]+'</svg>';
// App preferences are non-sensitive; Home and Apps are permanent rail anchors.
const enabledAppIds=['spotify','weather','glucose','settings','calendar','system'];
const defaultAppPins=['spotify','weather','glucose'];
const maxAppPins=3;
function normaliseApps(value){
  const input=value&&typeof value==='object'?value:{};
  const unique=items=>Array.isArray(items)?[...new Set(items.filter(id=>enabledAppIds.includes(id)))]:[];
  const order=unique(input.order);
  for(const id of enabledAppIds)if(!order.includes(id))order.push(id);
  const pins=unique(Array.isArray(input.pins)?input.pins:defaultAppPins).slice(0,maxAppPins);
  return {order,pins};
}
function appRailIds(value){const state=normaliseApps(value);return ['home',...state.order.filter(id=>state.pins.includes(id))];}
function changeAppOrder(value,id,delta){
  const state=normaliseApps(value),i=state.order.indexOf(id),j=i+delta;
  if(i<0||![-1,1].includes(delta)||j<0||j>=state.order.length)return state;
  [state.order[i],state.order[j]]=[state.order[j],state.order[i]];
  return state;
}
function changeAppPin(value,id,pinned){
  const state=normaliseApps(value);
  if(!enabledAppIds.includes(id)||typeof pinned!=='boolean')return state;
  if(!pinned)state.pins=state.pins.filter(x=>x!==id);
  else if(!state.pins.includes(id)&&state.pins.length<maxAppPins)state.pins.push(id);
  return state;
}
// Home customization: fixed presets, no extra data fetching or image assets.
const homeOptions={
  homeLayout:[['classic','Clock + widgets'],['minimal','Clock only'],['split','Split dashboard']],
  homeClock:[['thin','Thin digital'],['bold','Bold digital'],['blocks','Split digits'],['analogue','Analogue']],
  homeWallpaper:[['abstract','Original abstract'],['ocean','Ocean gradient'],['dusk','Dusk gradient'],['forest','Forest gradient'],['solid','Global theme']]
};
function normaliseHome(value){
  const input=value&&typeof value==='object'?value:{};
  return Object.fromEntries(Object.entries(homeOptions).map(([key,choices])=>[key,choices.some(([id])=>id===input[key])?input[key]:choices[0][0]]));
}
function homeClockParts(hour,minute){
  return {hour:String(hour).padStart(2,'0'),minute:String(minute).padStart(2,'0'),hourAngle:(hour%12)*30+minute*.5,minuteAngle:minute*6};
}
// Night mode uses local wall-clock minutes, including schedules crossing midnight.
function nightMinutes(value){
  if(typeof value!=='string'||!/^([01][0-9]|2[0-3]):[0-5][0-9]$/.test(value))return null;
  const [h,m]=value.split(':').map(Number);return h*60+m;
}
function normaliseNight(value){
  const p=value&&typeof value==='object'?value:{};
  return {night:['off','manual','scheduled'].includes(p.night)?p.night:'off',
    nightStart:nightMinutes(p.nightStart)!==null?p.nightStart:'22:00',
    nightEnd:nightMinutes(p.nightEnd)!==null?p.nightEnd:'07:00',
    nightDim:Number.isInteger(p.nightDim)&&p.nightDim>=10&&p.nightDim<=70?p.nightDim:55};
}
function nightActive(value,minute){
  const p=normaliseNight(value);
  if(p.night==='manual')return true;
  if(p.night!=='scheduled'||!Number.isInteger(minute)||minute<0||minute>=1440)return false;
  const start=nightMinutes(p.nightStart),end=nightMinutes(p.nightEnd);
  if(start===end)return false;
  return start<end?minute>=start&&minute<end:minute>=start||minute<end;
}
function normaliseEchoDevice(value){return typeof value==='string'&&value.length>0&&value.length<=256&&value.trim()===value?value:''}
function confirmedPlaybackMode(state,echoId){return echoId&&state?.connected&&!state.error&&state.deviceId===echoId?'echo':'wifi'}
function echoDeviceAvailable(list,id){return !!id&&Array.isArray(list)&&list.some(d=>d&&d.id===id&&!d.restricted)}
function displayDim(value,minute){
  const p=normaliseNight(value),brightness=Number.isFinite(value?.brightness)?Math.max(10,Math.min(100,value.brightness)):100;
  return Math.max((100-brightness)/100*.75,nightActive(p,minute)?p.nightDim/100:0);
}
function hardwareBrightness(value,minute){
  const p=normaliseNight(value),brightness=Number.isFinite(value?.brightness)?Math.max(10,Math.min(100,value.brightness)):100;
  return Math.round(Math.min(brightness,nightActive(p,minute)?100-p.nightDim:100));
}
// Calendar date keys use local civil dates, not UTC timestamps.
function calendarKey(d){return [d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-')}
function calendarDate(key){const [y,m,d]=key.split('-').map(Number);return new Date(y,m-1,d,12)}
function calendarMonth(key,delta){const d=calendarDate(key);return calendarKey(new Date(d.getFullYear(),d.getMonth()+delta,1,12))}
function calendarSwipeDirection(dx,dy){
  if(!Number.isFinite(dx)||!Number.isFinite(dy)||Math.abs(dy)<48||Math.abs(dy)<Math.abs(dx)*1.35)return null;
  return dy<0?'next':'prev';
}
function calendarGrid(key){
  const d=calendarDate(key),first=new Date(d.getFullYear(),d.getMonth(),1,12),offset=(first.getDay()+6)%7;
  return Array.from({length:42},(_,i)=>{
    const day=new Date(d.getFullYear(),d.getMonth(),i-offset+1,12);
    return {key:calendarKey(day),day:day.getDate(),inMonth:day.getMonth()===d.getMonth()};
  });
}
function calendarSample(today){
  const base=calendarDate(today);
  return [0,2,5].map((offset,i)=>({date:calendarKey(new Date(base.getFullYear(),base.getMonth(),base.getDate()+offset,12)),title:['Example appointment','Example reminder','Example event'][i],time:['18:00 – 19:00','All day','10:00 – 11:00'][i]}));
}
const defaults=()=>({theme:'graphite',railStyle:'floating',opacity:100,delay:10,animation:'slide',speed:180,brightness:100,...normaliseNight(),spotifyBackground:'album',weatherDays:'3',weatherIcons:'colour',glucoseView:'both',glucoseBackground:'green',echoDeviceId:'',appLayout:normaliseApps(),...normaliseHome(),autoHide:{home:true,spotify:true,weather:true,glucose:true,settings:false,calendar:true,system:true}});
const weather=window.EchoWeatherLive.enabled?window.EchoWeatherLive:window.EchoWeatherPreview;let weatherDay=0,weatherView='hourly';
const music=window.EchoSpotifyPreview;let playback=music.initial();const live=window.EchoSpotifyLive;const liveEnabled=live.enabled;
const glucosePreview=window.EchoGlucosePreview,glucoseLive=window.EchoGlucoseLive;let glucoseHours=6,glucoseScale='auto',glucoseScenario='range',glucoseData=glucoseLive.enabled?glucoseLive.data:glucosePreview.make();
const key='echo-show-preview-prefs-v1';let prefs=defaults(),active='home',category='navigation',expanded=true,timer,overlay=null,gesture=null;
try{const p=JSON.parse(localStorage.getItem(key)||'null');if(p&&typeof p==='object'){for(const [k,allowed] of Object.entries({theme:['graphite','black'],railStyle:['floating','transparent','edge'],animation:['none','fade','slide'],night:['off','manual','scheduled'],spotifyBackground:['album','art','theme'],weatherDays:['3','5','7'],weatherIcons:['colour','outline'],glucoseView:['live','graph','both'],glucoseBackground:['green','dynamic','theme']}))if(allowed.includes(p[k]))prefs[k]=p[k];for(const [k,min,max] of [['opacity',25,100],['delay',5,60],['speed',100,350],['brightness',10,100]])if(Number.isFinite(p[k])&&p[k]>=min&&p[k]<=max)prefs[k]=p[k];prefs.echoDeviceId=normaliseEchoDevice(p.echoDeviceId);Object.assign(prefs,normaliseHome(p));Object.assign(prefs,normaliseNight(p));prefs.appLayout=normaliseApps(p.appLayout);for(const id of Object.keys(apps))if(typeof p.autoHide?.[id]==='boolean')prefs.autoHide[id]=p.autoHide[id]}}catch{}
function apply(){screen.dataset.homeLayout=prefs.homeLayout;screen.dataset.homeClock=prefs.homeClock;screen.dataset.homeWallpaper=prefs.homeWallpaper;screen.dataset.glucoseBackground=prefs.glucoseBackground;screen.dataset.glucoseBand=glucosePreview.theme(glucoseData.latest?.mmol,glucoseData.status);screen.dataset.spotifyBackground=prefs.spotifyBackground;screen.dataset.theme=prefs.theme;screen.dataset.rail=prefs.railStyle;screen.dataset.animation=prefs.animation;screen.style.setProperty('--rail-opacity',prefs.opacity/100);screen.style.setProperty('--speed',prefs.speed+'ms');updateNightMode();}
let nativeBrightness=false;
function updateNightMode(){
  const now=new Date(),minute=now.getHours()*60+now.getMinutes(),on=nightActive(prefs,minute);
  const opacity=String(nativeBrightness?0:displayDim(prefs,minute));
  if($('dim').style.opacity!==opacity)$('dim').style.opacity=opacity;
  if(screen.dataset.nightActive!==String(on))screen.dataset.nightActive=String(on);
  const equal=prefs.night==='scheduled'&&prefs.nightStart===prefs.nightEnd;
  const status=equal?'Set different start and end times':prefs.night==='off'?'Off':on?'Active':'Waiting for schedule';
  for(const node of screen.querySelectorAll('[data-night-status]'))if(node.textContent!==status)node.textContent=status;
  for(const node of screen.querySelectorAll('[data-night-schedule]'))if(node.hidden!==(prefs.night!=='scheduled'))node.hidden=prefs.night!=='scheduled';
  for(const node of screen.querySelectorAll('[data-night-level]'))if(node.hidden!==(prefs.night==='off'))node.hidden=prefs.night==='off';
}
// Called by the native Activity in the trusted main frame only. No exposed Android bridge.
window.echoDeskHardwareBrightness=()=>{
  if(!nativeBrightness){
    nativeBrightness=true;
    updateNightMode();
    for(const el of screen.querySelectorAll('[data-pref=brightness],[data-pref=nightDim]')){
      const note=el.parentElement.querySelector('small');
      if(note)note.textContent=el.dataset.pref==='brightness'?'Controls Echo Show backlight':'Caps Echo Show backlight during night mode';
    }
  }
  const now=new Date();
  return hardwareBrightness(prefs,now.getHours()*60+now.getMinutes());
};
function syncNightControls(){
  for(const el of screen.querySelectorAll('[data-pref=night],[data-pref=nightDim],[data-night-time]')){
    const key=el.dataset.nightTime||el.dataset.pref;
    if(el.value!==String(prefs[key]))el.value=prefs[key];
  }
  for(const el of screen.querySelectorAll('[data-output=nightDim]'))el.textContent=prefs.nightDim+'%';
}
function save(){try{localStorage.setItem(key,JSON.stringify(prefs))}catch{}apply();schedule()}
function schedule(){clearTimeout(timer);if(expanded&&!overlay&&prefs.autoHide[active]&&!rail.contains(document.activeElement))timer=setTimeout(()=>setRail(false),prefs.delay*1000)}
function setRail(value){expanded=value;screen.classList.toggle('expanded',value);rail.inert=!value;rail.setAttribute('aria-hidden',String(!value));reveal.hidden=value;schedule()}
function renderRail(){rail.innerHTML=appRailIds(prefs.appLayout).map(id=>'<button data-page="'+id+'" aria-label="'+apps[id]+'" '+(active===id?'aria-current="page"':'')+'>'+icon(id)+'</button>').join('')+'<button data-open="drawer" aria-label="Apps" aria-expanded="'+(overlay==='drawer')+'">'+icon('apps')+'</button>'}
function clock(){
  if(active!=='home')return;
  const now=new Date(),parts=homeClockParts(now.getHours(),now.getMinutes()),label=parts.hour+':'+parts.minute,face=$('clock');
  if(!face)return;
  if(face.getAttribute('aria-label')!==label){
    face.setAttribute('aria-label',label);
    if(prefs.homeClock==='blocks'){$('homeHours').textContent=parts.hour;$('homeMinutes').textContent=parts.minute}
    else if(prefs.homeClock==='analogue'){face.style.setProperty('--hour-angle',parts.hourAngle+'deg');face.style.setProperty('--minute-angle',parts.minuteAngle+'deg')}
    else face.textContent=label;
  }
  const date=new Intl.DateTimeFormat('en-GB',{weekday:'long',day:'numeric',month:'long'}).format(now);
  if($('date').textContent!==date)$('date').textContent=date;
}
function homeClockMarkup(){
  if(prefs.homeClock==='blocks')return '<span id="homeHours"></span><span class="clock-colon" aria-hidden="true">:</span><span id="homeMinutes"></span>';
  if(prefs.homeClock==='analogue')return '<div class="analogue-face" aria-hidden="true"><i class="clock-mark m12">12</i><i class="clock-mark m3">3</i><i class="clock-mark m6">6</i><i class="clock-mark m9">9</i><i class="clock-hand hour-hand"></i><i class="clock-hand minute-hand"></i><i class="clock-pin"></i></div>';
  return '';
}
function renderHome(){page.innerHTML='<div class="home"><div id="clock" class="clock" role="img">'+homeClockMarkup()+'</div><div id="date" class="date"></div></div><div class="tiles"><button class="tile" data-page="weather"><span id="homeWeatherLabel">Weather · Bournemouth</span><strong id="homeWeatherReading" class="home-weather">'+weather.icon(weather.current.condition,prefs.weatherIcons)+'<span>'+weather.current.temp+'° · '+weather.conditions[weather.current.condition]+'</span></strong></button><button class="tile" data-page="spotify"><span>Spotify</span><strong id="homeTrack">'+(liveEnabled?'Spotify — connecting':music.tracks[playback.index].title)+'</strong></button><button class="tile" data-page="glucose"><span id="homeGlucoseLabel">Glucose</span><strong id="homeGlucose"></strong></button></div>';clock();updateHomeWeather();updateHomeGlucose();if(liveEnabled)renderLiveState()}
let calendarSelected=null,calendarShown=null,calendarToday=null,calendarData={status:'loading',events:[]},calendarRequest=null,calendarDataMonth=null;
const calendarEscape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function refreshCalendar(){
  if(!liveEnabled||active!=='calendar'||calendarRequest)return;
  const month=calendarShown;calendarRequest=month;
  try{const r=await fetch('/api/calendar?month='+encodeURIComponent(month),{cache:'no-store',headers:{'X-Desk-Preview':'1'}});if(!r.ok)throw Error();const next=await r.json();if(active==='calendar'&&calendarShown===month){const changed=calendarDataMonth!==month||JSON.stringify(calendarData)!==JSON.stringify(next);calendarData=next;calendarDataMonth=month;if(changed){const scroll=page.querySelector('.cal-agenda')?.scrollTop||0;renderCalendar();page.querySelector('.cal-agenda').scrollTop=scroll}}}catch{if(active==='calendar'&&calendarShown===month){calendarData={status:'error',events:[],message:'Local calendar service unavailable.'};calendarDataMonth=month;renderCalendar()}}finally{calendarRequest=null}
}

function calendarReset(){
  calendarToday=calendarKey(new Date());calendarSelected=calendarToday;calendarShown=calendarMonth(calendarToday,0);
}
function renderCalendar(){
  if(!calendarSelected)calendarReset();
  calendarToday=calendarKey(new Date());
  const data=calendarDataMonth===calendarShown?calendarData:{status:'loading',events:[]};
  const month=calendarDate(calendarShown),sample=liveEnabled?(data.events||[]):calendarSample(calendarToday),days=calendarGrid(calendarShown);
  const hasData=!liveEnabled||['fresh','stale','partial'].includes(data.status);
  const chosen=sample.filter(e=>e.date===calendarSelected),upcoming=sample.filter(e=>e.date>calendarSelected).slice(0,3);
  const monthLabel=new Intl.DateTimeFormat('en-GB',{month:'long',year:'numeric'}).format(month);
  const dateLabel=k=>new Intl.DateTimeFormat('en-GB',{weekday:'long',day:'numeric',month:'long'}).format(calendarDate(k));
  const event=e=>'<article class="cal-event" data-cal-kind="'+(['holiday','observance','f1'].includes(e.kind)?e.kind:'sample')+'"><small>'+calendarEscape(e.time)+'</small><strong>'+calendarEscape(e.title)+'</strong>'+(e.location?'<small>'+calendarEscape(e.location)+'</small>':'')+'</article>';
  const marks=day=>[...new Set(sample.filter(e=>e.date===day).map(e=>['holiday','observance','f1'].includes(e.kind)?e.kind:'sample'))].map(k=>'<i data-cal-kind="'+k+'"></i>').join('');
  page.innerHTML='<div class="cal-layout"><section class="cal-month" aria-label="Monthly calendar"><header><h1>'+monthLabel+'</h1><div class="cal-nav"><button data-cal-action="prev" aria-label="Previous month">‹</button><button data-cal-action="today">Today</button><button data-cal-action="next" aria-label="Next month">›</button></div></header><div class="cal-grid">'+
    ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].map(d=>'<span class="cal-weekday">'+d+'</span>').join('')+
    days.map(d=>'<button data-cal-day="'+d.key+'" aria-label="'+dateLabel(d.key)+'" aria-pressed="'+(d.key===calendarSelected)+'" '+(d.key===calendarToday?'aria-current="date" ':'')+'class="'+(d.inMonth?'':'outside')+'">'+d.day+'<span class="cal-dots">'+marks(d.key)+'</span>'+'</button>').join('')+
    '</div></section><section class="cal-agenda" aria-label="Calendar events"><h2>'+dateLabel(calendarSelected)+'</h2><p class="cal-source">'+(liveEnabled?'UK holidays &amp; Formula 1 · '+({fresh:'Updated',partial:'Partial data',loading:'Loading',error:'Unavailable'}[data.status]||'Unavailable'):'SAMPLE EVENTS · NOT LIVE')+'</p>'+
    (liveEnabled&&data.sources?'<p class="cal-source">Bank holidays: '+calendarEscape(data.sources.holidays)+' · F1: '+calendarEscape(data.sources.f1)+'</p>':'')+
    '<div class="cal-legend"><span data-cal-kind="holiday">Bank holidays</span><span data-cal-kind="observance">Observances</span><span data-cal-kind="f1">F1</span></div>'+
    (!hasData?'<p class="cal-empty">'+calendarEscape(data.message||'Loading calendar…')+'</p>':(chosen.length?chosen.map(event).join(''):'<p class="cal-empty">No events for this day.</p>')+(upcoming.length?'<h3>Upcoming</h3>'+upcoming.map(e=>'<small class="cal-event-date">'+dateLabel(e.date)+'</small>'+event(e)).join(''):''))+
    (liveEnabled?'<p class="cal-source cal-attribution">UK bank holidays: GOV.UK · F1 schedule: F1Calendar.com / sportstimes/f1 (unofficial, MIT). Times in UK local time.</p>':'')+'</section></div>';
}
function calendarAction(action,focus=true){
  if(action==='today')calendarReset();
  else if(action==='prev'||action==='next'){calendarShown=calendarMonth(calendarShown,action==='prev'?-1:1);calendarSelected=calendarShown}
  renderCalendar();refreshCalendar();
  if(focus)page.querySelector('[data-cal-action="'+action+'"]')?.focus({preventScroll:true});
}
let systemData=null,systemRequest=false,systemFailed=false,systemGeneration=0,systemView='server',echoData=null;
function systemBytes(v){return Number.isFinite(v)&&v>=0?(v/1073741824).toFixed(1)+' GiB':'—'}
function systemUptime(v){if(!Number.isFinite(v)||v<0)return 'Unavailable';const m=Math.floor(v/60);return (m>=1440?Math.floor(m/1440)+'d ':'')+Math.floor(m%1440/60)+'h '+m%60+'m'}
function systemPercent(v){return Number.isFinite(v)?Math.max(0,Math.min(100,v)):null}
function systemServiceState(v){return ({fresh:['Ready','ok'],live:['Ready','ok'],connected:['Connected','ok'],inactive:['Connected · idle','ok'],stale:['Stale','warn'],partial:['Partial data','warn'],loading:['Checking','neutral'],authorized:['Authorized · checking','neutral'],disconnected:['Not connected','warn'],not_configured:['Not configured','neutral'],configuration_error:['Configuration error','bad'],unavailable:['Unavailable','bad'],error:['Unavailable','bad'],sample:['Sample','neutral']})[v]||['Not checked','neutral']}
function systemThermal(v){return ['Normal','Light','Moderate','Severe','Critical','Emergency','Shutdown'][v]||'Unavailable'}
function systemTabs(){return '<div class="sys-tabs" role="group" aria-label="System device"><button data-system-view="server" aria-pressed="'+(systemView==='server')+'">Raspberry Pi</button><button data-system-view="echo" aria-pressed="'+(systemView==='echo')+'">Echo Show</button></div>'}
window.echoDeskWantsDiagnostics=()=>active==='system'&&systemView==='echo'&&!document.hidden;
window.echoDeskReceiveDiagnostics=data=>{
  if(!window.echoDeskWantsDiagnostics()||!data||typeof data!=='object')return;
  echoData=data;renderSystem();
};
function renderEchoSystem(metric,usage,stat,esc){
  const h=echoData||{};
  return '<header class="sys-header"><h1>System Information</h1>'+systemTabs()+'</header><div class="sys-layout"><section class="sys-panel"><h2>Echo Show hardware</h2><p class="sys-host">'+esc(echoData?(h.model||'Echo Show')+' · Android '+(h.android||'Unknown'):'Echo Show hardware metrics unavailable until native app connects.')+'</p>'+metric('RAM',h.memory?.percent,usage(h.memory))+metric('Internal storage',h.storage?.percent,usage(h.storage))+'<div class="sys-facts">'+stat('Logical CPUs',Number.isInteger(h.cores)?h.cores:'Unavailable')+stat('Architecture',h.architecture||'Unavailable')+stat('Device uptime',systemUptime(h.uptime))+stat('Thermal status',systemThermal(h.thermal))+'</div><small class="sys-note">CPU load and temperature unavailable through the current Android APIs.</small></section><section class="sys-panel"><h2>Display &amp; audio</h2>'+metric('Backlight setting',h.brightness)+metric('Media volume',h.volume,h.muted?'Muted':'Local Android media stream')+'<div class="sys-facts">'+stat('Display resolution',Number.isInteger(h.width)&&Number.isInteger(h.height)?h.width+' × '+h.height+' px':'Unavailable')+stat('Dashboard viewport',screen.clientWidth+' × '+screen.clientHeight+' CSS px')+stat('Android app',h.version||'Unavailable')+stat('Android API',Number.isInteger(h.sdk)?h.sdk:'Unavailable')+'</div><small class="sys-note">'+(echoData?'Local read-only snapshot · refreshes while this view is open.':'Open on the Echo Show running native app 0.6.0 or later. Browser preview cannot access local Android metrics.')+'</small></section></div>';
}
function renderSystem(){
  if(active!=='system')return;
  const demo={hardware:{os:'Example Linux',architecture:'aarch64',model:'Example server',cpu:24,cores:4,memory:{used:3.2*1073741824,total:8*1073741824,percent:40},storage:{used:28*1073741824,total:64*1073741824,percent:44},temperature:48,uptime:8040,network:'up'},services:{spotify:'sample',weather:'sample',glucose:'sample',calendar:'sample',server:'sample'}};
  const data=liveEnabled?(systemData||{}):demo,h=data.hardware||{},services=data.services||{},esc=calendarEscape;
  const metric=(name,value,detail='')=>{const v=systemPercent(value);return '<div class="sys-metric"><div><span>'+name+'</span><strong>'+(v===null?'—':Math.round(v)+'%')+'</strong></div><div class="sys-meter"><i style="width:'+(v===null?0:v)+'%"></i></div>'+(detail?'<small>'+esc(detail)+'</small>':'')+'</div>'};
  const usage=m=>m?systemBytes(m.used)+' / '+systemBytes(m.total):'Unavailable';
  const stat=(name,value)=>'<div class="sys-stat"><span>'+name+'</span><strong>'+esc(value)+'</strong></div>';
  const row=(key,name)=>{const [label,kind]=systemServiceState(systemFailed?(key==='server'?'error':'unknown'):services[key]);return '<div class="sys-service"><span>'+name+'</span><span class="sys-state" data-state="'+kind+'"><i></i>'+label+'</span></div>'};
  const scroll=[...page.querySelectorAll('.sys-panel')].map(el=>el.scrollTop);
  if(systemView==='echo'){
    page.innerHTML=renderEchoSystem(metric,usage,stat,esc);
    [...page.querySelectorAll('.sys-panel')].forEach((el,i)=>{el.scrollTop=scroll[i]||0});
    return;
  }
  page.innerHTML='<header class="sys-header"><h1>System Information</h1>'+systemTabs()+'</header><div class="sys-layout"><section class="sys-panel"><h2>Server hardware</h2><small class="sys-note">'+(!liveEnabled?'SAMPLE DATA':systemFailed?'SERVER UNREACHABLE':systemData?'LIVE · SERVER HOST':'CONNECTING…')+'</small><p class="sys-host">'+esc(h.model||h.os||'Waiting for host')+(h.model?' · '+esc(h.os||''):'')+(h.architecture?' · '+esc(h.architecture):'')+'</p>'+metric('CPU',h.cpu,Number.isInteger(h.cores)?h.cores+' logical CPUs':'')+metric('RAM',h.memory?.percent,usage(h.memory))+metric('Storage',h.storage?.percent,usage(h.storage))+'<div class="sys-facts">'+stat('CPU temperature',Number.isFinite(h.temperature)?h.temperature.toFixed(1)+' °C':'Unavailable')+stat('Host uptime',systemUptime(h.uptime))+stat('Network link',h.network==='up'?'Active':'Unknown')+'</div></section><section class="sys-panel"><h2>Service status</h2>'+row('server','Dashboard server')+row('spotify','Spotify')+row('weather','Weather')+row('glucose','Glucose')+row('calendar','Calendar')+'<div class="sys-display"><strong>Display device</strong><p>'+(nativeBrightness?'Native display':'Browser preview')+' · '+esc(screen.clientWidth)+' × '+esc(screen.clientHeight)+' CSS px</p><p>Select Echo Show above for local display diagnostics.</p></div><small class="sys-note">Read-only. Network link does not guarantee internet access.</small></section></div>';
  [...page.querySelectorAll('.sys-panel')].forEach((el,i)=>{el.scrollTop=scroll[i]||0});
}
async function refreshSystem(){
  if(!liveEnabled||active!=='system'||systemView!=='server'||systemRequest||document.hidden)return;
  systemRequest=true;const generation=systemGeneration;
  try{const r=await fetch('/api/system',{cache:'no-store',headers:{'X-Desk-Preview':'1'}});if(!r.ok)throw Error();const data=await r.json();if(active==='system'&&generation===systemGeneration){systemData=data;systemFailed=false;renderSystem()}}
  catch{if(active==='system'&&generation===systemGeneration){systemFailed=true;systemData=null;renderSystem()}}
  finally{systemRequest=false}
}
function renderPage(){screen.dataset.page=active;renderRail();if(active==='home'){renderHome()}else if(active==='spotify'){renderSpotify();if(liveEnabled)live.refresh()}else if(active==='weather'){renderWeather()}else if(active==='glucose'){renderGlucose()}else if(active==='settings'){renderSettings()}else if(active==='calendar'){renderCalendar();refreshCalendar()}else if(active==='system'){renderSystem();refreshSystem();if(liveEnabled)live.refresh()}else{page.innerHTML='<div class="placeholder"><h1>'+apps[active]+'</h1><p>This page is planned for a later prototype increment. No live service is connected.</p><button data-page="home">Return Home</button></div>'}}
function navigate(id){if(id!=='home'&&!enabledAppIds.includes(id))return;if(glucoseObserver){glucoseObserver.disconnect();glucoseObserver=null}closeOverlay(false);active=id;systemGeneration++;if(id==='system'){systemData=null;systemFailed=false;echoData=null}if(id==='calendar')calendarReset();renderPage();setRail(true);if(weather.enabled&&['home','weather'].includes(active))weather.refresh();if(glucoseLive.enabled&&['home','glucose'].includes(active)){updateLiveGlucose();glucoseLive.refresh()}}
function closeOverlay(restore=true){const previous=overlay;overlay=null;drawer.hidden=true;quick.hidden=true;$('devices').hidden=true;$('weatherDetails').hidden=true;shade.hidden=true;renderRail();if(restore){if(previous==='quick')$('quickHandle').focus();else if(previous==='devices')$('deviceSelect')?.focus();else if(previous==='weather')(page.querySelector('[data-weather-day="'+weatherDay+'"]')||page.querySelector('[data-hour-day="'+weatherDay+'"]')||$('forecastDays'))?.focus();else rail.querySelector('[data-open=drawer]')?.focus()}schedule()}
function openOverlay(id,devicePurpose='all'){overlay=id;clearTimeout(timer);shade.hidden=false;drawer.hidden=id!=='drawer';quick.hidden=id!=='quick';$('devices').hidden=id!=='devices';$('weatherDetails').hidden=id!=='weather';if(id==='drawer'){setRail(true);drawer.innerHTML='<header>Apps<button data-close aria-label="Close Apps">×</button></header><div class="app-grid">'+prefs.appLayout.order.map(a=>'<button data-page="'+a+'">'+icon(a)+apps[a]+'</button>').join('')+'</div>'}else if(id==='devices'){renderDevices(devicePurpose)}else if(id==='weather'){renderWeatherDetails()}else{renderQuick()}renderRail();(id==='drawer'?drawer:id==='devices'?$('devices'):id==='weather'?$('weatherDetails'):quick).querySelector('[data-close]')?.focus()}
function selectRow(label,k,options){return '<div class="setting"><label>'+label+'</label><select aria-label="'+label+'" data-pref="'+k+'">'+options.map(([v,t])=>'<option value="'+v+'" '+(String(prefs[k])===String(v)?'selected':'')+'>'+t+'</option>').join('')+'</select></div>'}
function rangeRow(label,k,min,max,step,suffix,note=''){return '<div class="setting"><label>'+label+(note?'<small>'+note+'</small>':'')+'</label><input aria-label="'+label+'" type="range" data-pref="'+k+'" min="'+min+'" max="'+max+'" step="'+step+'" value="'+prefs[k]+'"><output data-output="'+k+'">'+prefs[k]+suffix+'</output></div>'}
const homeRows=()=>selectRow('Layout','homeLayout',homeOptions.homeLayout)+selectRow('Clock style','homeClock',homeOptions.homeClock)+selectRow('Wallpaper','homeWallpaper',homeOptions.homeWallpaper);
const themeRow=()=>selectRow('Theme','theme',[['graphite','Graphite'],['black','Black']]);
function nightRow(){
  const now=new Date(),on=nightActive(prefs,now.getHours()*60+now.getMinutes());
  const status=prefs.night==='scheduled'&&prefs.nightStart===prefs.nightEnd?'Set different start and end times':prefs.night==='off'?'Off':on?'Active':'Waiting for schedule';
  const timeRow=(label,key)=>'<div class="setting"><label>'+label+'</label><input type="time" data-night-time="'+key+'" aria-label="'+label+'" value="'+prefs[key]+'" required></div>';
  return selectRow('Night mode','night',[['off','Off'],['manual','Manual'],['scheduled','Scheduled']])+
    '<div data-night-level '+(prefs.night==='off'?'hidden':'')+'>'+rangeRow('Night dimming','nightDim',10,70,5,'%',nativeBrightness?'Caps Echo Show backlight during night mode':'Visual dimming; does not control hardware backlight')+'</div>'+
    '<div data-night-schedule '+(prefs.night!=='scheduled'?'hidden':'')+'>'+timeRow('Start time','nightStart')+timeRow('End time','nightEnd')+'<p class="app-help">Uses the display’s local time. Equal times disable the schedule.</p></div>'+
    '<p class="night-status" data-night-status role="status">'+status+'</p>';
}
const brightnessRow=()=>rangeRow('Brightness','brightness',10,100,5,'%',nativeBrightness?'Controls Echo Show backlight':'Visual dimming only; not hardware backlight');
const delayRow=()=>selectRow('Auto-hide delay','delay',[[5,'5 seconds'],[10,'10 seconds'],[15,'15 seconds'],[30,'30 seconds'],[60,'60 seconds']]);
function renderQuick(){if(active==='home'){quick.innerHTML='<header>Home quick settings<button data-close aria-label="Close quick settings">×</button></header>'+homeRows()+brightnessRow()+nightRow()+themeRow()+delayRow()+'<button data-page="settings">All settings</button>';return}if(active==='glucose'){quick.innerHTML='<header>Glucose quick settings<button data-close aria-label="Close quick settings">×</button></header>'+glucoseRows(true)+'<button data-page="settings">All settings</button>';return}if(active==='weather'){quick.innerHTML='<header>Weather quick settings<button data-close aria-label="Close quick settings">×</button></header>'+weatherRows()+brightnessRow()+'<button data-page="settings">All settings</button>';return}if(active==='spotify'&&liveEnabled){quick.innerHTML='<header>Spotify quick settings<button data-close aria-label="Close quick settings">×</button></header>'+spotifyBackgroundRow()+spotifyModeRow()+'<button data-open="devices">Playback devices</button> '+(echoModeSupported()?'<button data-echo-bind>Configure Echo device</button> ':'')+'<button data-page="settings">All settings</button>';return}if(active==='spotify'){quick.innerHTML='<header>Spotify quick settings<button data-close aria-label="Close quick settings">×</button></header>'+spotifyModeRow()+spotifyBackgroundRow()+ '<div class="setting"><label>Playback device</label><button data-open="devices">'+playback.device+'</button></div><button data-page="settings">All settings</button>';return}quick.innerHTML='<header>'+apps[active]+' quick settings<button data-close aria-label="Close quick settings">×</button></header>'+brightnessRow()+nightRow()+themeRow()+delayRow()+(active==='home'||active==='settings'?'':'<p>App-specific controls will be added with the '+apps[active]+' page.</p>')+'<button data-page="settings">All settings</button>'}
function appSettingsRows(){
  const state=prefs.appLayout,full=state.pins.length>=maxAppPins;
  return '<h2>Apps</h2><p class="app-help">Choose up to '+maxAppPins+' rail shortcuts. Home and Apps always stay available. All enabled apps are in the drawer.</p><div class="app-capacity" role="status">'+state.pins.length+' / '+maxAppPins+' shortcuts pinned</div>'+state.order.map((id,i)=>{
    const pinned=state.pins.includes(id);
    return '<div class="setting app-order-row"><span class="app-order-name">'+icon(id)+'<strong>'+apps[id]+'</strong></span><label class="app-pin"><input type="checkbox" data-app-pin="'+id+'" aria-label="Pin '+apps[id]+' to rail" '+(pinned?'checked':'')+(!pinned&&full?' disabled':'')+'> Pin</label><div class="app-order-controls"><button data-app-move="'+id+'" data-direction="-1" aria-label="Move '+apps[id]+' up" '+(i===0?'disabled':'')+'>↑</button><button data-app-move="'+id+'" data-direction="1" aria-label="Move '+apps[id]+' down" '+(i===state.order.length-1?'disabled':'')+'>↓</button></div></div>';
  }).join('')+'<p class="app-help">Order applies to the drawer and pinned shortcuts.</p>';
}
function refreshAppSettings(id,kind,direction){
  const top=$('settingsDetails')?.scrollTop||0;
  save();renderRail();renderSettings();
  const details=$('settingsDetails');details.scrollTop=top;
  const target=kind==='pin'?details.querySelector('[data-app-pin="'+id+'"]'):details.querySelector('[data-app-move="'+id+'"][data-direction="'+direction+'"]');
  const alternative=details.querySelector('[data-app-pin="'+id+'"]:not(:disabled)')||details.querySelector('[data-app-move="'+id+'"]:not(:disabled)');
  (target&&!target.disabled?target:alternative)?.focus({preventScroll:true});
}
function renderSettings(){page.innerHTML='<h1>Settings</h1><div class="settings-layout"><nav class="categories" aria-label="Settings categories">'+[['general','General'],['navigation','Navigation'],['apps','Apps'],['home','Home'],['spotify','Spotify'],['weather','Weather'],['glucose','Glucose'],['connections','Connections'],['system','System']].map(([id,name])=>'<button data-category="'+id+'" class="'+(category===id?'active':'')+'">'+name+'</button>').join('')+'</nav><div class="details" id="settingsDetails"></div></div>';const d=$('settingsDetails');if(category==='navigation'){d.innerHTML='<h2>Navigation</h2>'+delayRow()+selectRow('Rail style','railStyle',[['floating','Floating'],['transparent','Transparent'],['edge','Edge aligned']])+rangeRow('Opacity','opacity',25,100,5,'%')+Object.entries(apps).map(([id,name])=>'<div class="setting"><label for="hide-'+id+'">Auto-hide on '+name+'</label><input id="hide-'+id+'" type="checkbox" data-hide="'+id+'" '+(prefs.autoHide[id]?'checked':'')+'></div>').join('')+'<button data-category="apps">Customize app shortcuts</button>'}else if(category==='apps'){d.innerHTML=appSettingsRows()}else if(category==='general'){d.innerHTML='<h2>General</h2>'+themeRow()+brightnessRow()+nightRow()+selectRow('Animation','animation',[['none','None'],['fade','Fade'],['slide','Slide']])+rangeRow('Animation speed','speed',100,350,50,' ms')+'<p>Startup: Home · Screen: always on (hardware validation pending).</p>'}else if(category==='home'){d.innerHTML='<h2>Home</h2>'+homeRows()+'<p class="app-help">Changes apply immediately and are remembered. Clock-only hides summary tiles; apps remain available from the rail and drawer.</p><button data-page="home">Preview Home</button>'}else if(category==='glucose'){d.innerHTML='<h2>Glucose</h2>'+glucoseRows(false)+'<p>'+(glucoseLive.enabled?'Gluroo · local connection · minimum 150s source polling.':'Sample readings only.')+' Use the Libre app for monitoring, decisions and alarms.</p>'}else if(category==='weather'){d.innerHTML='<h2>Weather</h2><p>Bournemouth · Fixed location</p>'+weatherRows()+'<p>'+(weather.enabled?'Open-Meteo · refresh every 15 minutes.':'Sample forecast only.')+'</p>'}else if(category==='system'){d.innerHTML='<h2>System</h2><p>Read-only server and service diagnostics. Display hardware support is pending.</p><button data-page="system">Open System Information</button>'}else if(category==='spotify'){d.innerHTML='<h2>Spotify</h2>'+spotifyBackgroundRow()+'<p>'+(liveEnabled?'Live Spotify Connect playback.':'Sample playback only.')+'</p>'+(echoModeSupported()?'<p>Echo mode uses your selected Spotify Connect device. Physical buttons control the local speaker.</p><button data-echo-bind>Configure Echo device</button>':'')}else{d.innerHTML='<h2>'+({home:'Home',spotify:'Spotify',weather:'Weather',glucose:'Glucose',connections:'Connections',system:'System'}[category])+'</h2><p>Settings for this category will be added in a later increment.</p>'}d.insertAdjacentHTML('beforeend','<button data-reset>Reset preview preferences</button>')}
screen.addEventListener('click',e=>{const b=e.target.closest('button');if(e.target===shade){closeOverlay();return}if(!b){if(expanded&&!overlay&&prefs.autoHide[active]&&page.contains(e.target)&&!e.target.closest('input,select,a,label,textarea,[contenteditable]'))setRail(false);return}if(b.dataset.systemView&&active==='system'){const next=b.dataset.systemView;if(['server','echo'].includes(next)&&next!==systemView){systemView=next;echoData=null;renderSystem();refreshSystem();page.querySelector('[data-system-view="'+next+'"]')?.focus({preventScroll:true})}return}if(b.id==='reveal'){setRail(true);return}if(b.id==='quickHandle'){openOverlay('quick');return}if(b.hasAttribute('data-close')){closeOverlay();return}if(b.dataset.calAction){calendarAction(b.dataset.calAction);return}if(b.dataset.calDay){const day=b.dataset.calDay;if(calendarGrid(calendarShown).some(d=>d.key===day)){calendarSelected=day;calendarShown=calendarMonth(day,0);renderCalendar();refreshCalendar();page.querySelector('[data-cal-day="'+day+'"]')?.focus({preventScroll:true})}return}if(b.dataset.hourDay!==undefined){weatherDay=Number(b.dataset.hourDay);openOverlay('weather');return}if(b.dataset.weatherDay!==undefined){const i=Number(b.dataset.weatherDay);if(Number.isInteger(i)&&i>=0&&i<weather.validDuration(prefs.weatherDays)){weatherDay=i;openOverlay('weather')}return}if(b.hasAttribute('data-echo-bind')){if(echoModeSupported()&&!live.pending)openOverlay('devices','echo-bind');return}if(b.dataset.open){openOverlay(b.dataset.open);return}if(b.dataset.music){musicAction(b.dataset.music);return}if(b.dataset.liveDevice){
  if(live.pending||!live.state.connected||live.state.error)return;
  const id=normaliseEchoDevice(b.dataset.liveDevice);
  if(!id)return;
  if(b.hasAttribute('data-bind-echo')){
    if(!echoModeSupported())return;
    prefs.echoDeviceId=id;save();
  }
  closeOverlay(false);
  if(live.state.deviceId!==id||live.state.inactive)live.command('device',id);
  else renderLiveState();
  return
}if(b.dataset.device){playback=music.reduce(playback,'device',b.dataset.device);closeOverlay(false);renderSpotify();$('deviceSelect')?.focus();return}if(b.dataset.page){navigate(b.dataset.page);return}if(b.dataset.appMove){const id=b.dataset.appMove,delta=Number(b.dataset.direction);prefs.appLayout=changeAppOrder(prefs.appLayout,id,delta);refreshAppSettings(id,'move',delta);return}if(b.dataset.category){category=b.dataset.category;renderSettings();return}if(b.hasAttribute('data-reset')&&confirm('Reset preview preferences only?')){prefs=defaults();save();renderRail();renderSettings()}});
screen.addEventListener('input',e=>{const el=e.target,k=el.dataset.pref;if(el.id==='seek'){if(liveEnabled){$('elapsed').textContent=music.time(Number(el.value));return}musicAction('seek',Number(el.value),false);return}if(!k||el.type!=='range')return;prefs[k]=Number(el.value);const o=el.parentElement.querySelector('output');if(o)o.textContent=el.value+(k==='speed'?' ms':'%');if(k==='nightDim')syncNightControls();save()});
screen.addEventListener('change',e=>{const el=e.target,k=el.dataset.pref;if(el.dataset.nightTime){const key=el.dataset.nightTime;if(['nightStart','nightEnd'].includes(key)&&nightMinutes(el.value)!==null){prefs[key]=el.value;syncNightControls();save()}else if(['nightStart','nightEnd'].includes(key))el.value=prefs[key];return}if(el.dataset.glucoseControl){changeGlucose(el.dataset.glucoseControl,el.value);return}if(el.id==='weatherView'){if(['hourly','daily'].includes(el.value)&&el.value!==weatherView){weatherView=el.value;renderWeather(true);$('weatherView')?.focus()}return}if(el.id==='seek'&&liveEnabled){live.command('seek',Number(el.value));return}if(el.dataset.mode!==undefined){musicAction('mode',el.value);if(overlay==='quick'){renderQuick();syncLiveMode()}return}if(el.dataset.appPin){const id=el.dataset.appPin;prefs.appLayout=changeAppPin(prefs.appLayout,id,el.checked);refreshAppSettings(id,'pin');return}if(el.dataset.hide){prefs.autoHide[el.dataset.hide]=el.checked;save();return}if(k&&el.tagName==='SELECT'){if(Object.prototype.hasOwnProperty.call(homeOptions,k)&&!homeOptions[k].some(([id])=>id===el.value))return;if(k==='night'&&!['off','manual','scheduled'].includes(el.value))return;prefs[k]=k==='delay'?Number(el.value):el.value;if(k==='night')syncNightControls();save();if(active==='home'&&k==='homeClock')renderHome();if(active==='weather'&&['weatherDays','weatherIcons'].includes(k))renderWeather();if(active==='glucose'&&['glucoseView','glucoseBackground'].includes(k))renderGlucose()}});
screen.addEventListener('pointerdown',e=>{if(active==='calendar'&&e.target.closest('.cal-grid')){gesture=null;schedule();return}const r=screen.getBoundingClientRect();gesture={x:e.clientX,y:e.clientY,top:e.clientY-r.top<28,edge:r.right-e.clientX<30,control:!!e.target.closest('input,select,button:not(#quickHandle):not(#reveal)')};schedule()});
screen.addEventListener('pointerup',e=>{if(!gesture)return;const dx=e.clientX-gesture.x,dy=e.clientY-gesture.y;const g=gesture;gesture=null;if(overlay||g.control)return;if(g.top&&dy>50&&dy>Math.abs(dx)*1.4)openOverlay('quick');else if(g.edge&&dx< -45&&Math.abs(dx)>Math.abs(dy)*1.4)setRail(true)});
screen.addEventListener('pointercancel',()=>{gesture=null});rail.addEventListener('focusout',()=>setTimeout(schedule,0));screen.addEventListener('keydown',e=>{if(e.key==='Escape'&&overlay){closeOverlay();return}if(e.key==='Escape'&&expanded&&prefs.autoHide[active]){setRail(false);return}schedule()});

// All playback here is deterministic sample state. No audio/API requests.
const transportIcons={previous:'<path d="M5 4v16M19 4 7 12l12 8z" fill="currentColor"/>',next:'<path d="M19 4v16M5 4l12 8-12 8z" fill="currentColor"/>',play:'<path d="m8 4 13 8-13 8z" fill="currentColor"/>',pause:'<path d="M8 5v14M16 5v14" stroke-width="4"/>',shuffle:'<path d="M3 6h3c4 0 8 12 12 12h3m-4-4 4 4-4 4M3 18h3c1.5 0 3-2 4-4m4-4c1-2 3-4 4-4h3m-4-4 4 4-4 4"/>',repeat:'<path d="M4 10V6h15m-4-4 4 4-4 4M20 14v4H5m4-4-4 4 4 4"/>',save:'<circle cx="12" cy="12" r="10"/><path d="M7 12h10M12 7v10"/>',saved:'<circle cx="12" cy="12" r="10"/><path d="m7 12 3 3 7-7"/>'};
const transportIcon=id=>'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">'+transportIcons[id]+'</svg>';
let nativeSpotifyLaunch=false;
window.echoDeskEnableSpotifyLaunch=()=>{nativeSpotifyLaunch=true};
function echoModeSupported(){return liveEnabled&&document.documentElement.dataset.deviceGateway==='1'}
function liveMode(){return echoModeSupported()?confirmedPlaybackMode(live.state,prefs.echoDeviceId):'wifi'}
function modeOptions(){if(liveEnabled)return '<option value="wifi" '+(liveMode()==='wifi'?'selected':'')+'>Wi-Fi</option><option disabled>PC · pending</option><option value="echo" '+(!echoModeSupported()?'disabled':liveMode()==='echo'?'selected':'')+'>'+(echoModeSupported()?(prefs.echoDeviceId?'Echo':'Echo · set up'):'Echo · paired display only')+'</option>';return [['wifi','Wi-Fi'],['pc','PC'],['echo','Echo · pending']].map(([id,label])=>'<option value="'+id+'" '+(id===playback.mode?'selected ':'')+(id==='echo'?'disabled':'')+'>'+label+'</option>').join('')}
function spotifyModeRow(){return '<div class="setting"><label>Playback mode</label><select data-mode aria-label="Playback mode">'+modeOptions()+'</select></div>'}
function spotifyBackgroundRow(){return selectRow('Background','spotifyBackground',[['album','Album colours'],['art','Dimmed album artwork'],['theme','Global theme']])}
function artwork(t){return '<svg viewBox="0 0 320 320" role="img" aria-label="Abstract sample album artwork"><rect width="320" height="320" fill="'+t.colors[0]+'"/><circle cx="190" cy="105" r="94" fill="'+t.colors[1]+'"/><path d="M0 235 100 70 210 235 320 115V320H0Z" fill="'+t.colors[2]+'"/><circle cx="112" cy="215" r="66" fill="none" stroke="'+t.colors[1]+'" opacity=".6" stroke-width="12"/><text x="160" y="290" text-anchor="middle" fill="white" font-size="12" letter-spacing="4">SAMPLE ART</text></svg>'}
function renderSpotify(){page.innerHTML='<header class="spotify-header"><span>SPOTIFY</span><select id="playMode" data-mode aria-label="Playback mode">'+modeOptions()+'</select></header><div class="spotify-layout"><div class="album" id="album"></div><section class="player"><div class="song"><small id="playStatus"></small><h1 id="songTitle"></h1><div id="songArtist"></div></div><div class="timeline"><input id="seek" type="range" min="0" step="1" aria-label="Seek track"><div class="times"><span id="elapsed"></span><span id="duration"></span></div></div><div class="transport"><button data-music="shuffle" aria-label="Shuffle" id="shuffle">'+transportIcon('shuffle')+'</button><button data-music="previous" aria-label="Previous">'+transportIcon('previous')+'</button><button class="play" id="playToggle" data-music="toggle" aria-label="Pause"></button><button data-music="next" aria-label="Next">'+transportIcon('next')+'</button><button data-music="repeat" aria-label="Repeat" id="repeat">'+transportIcon('repeat')+'<small id="repeatOne" hidden>1</small></button></div><div class="player-bottom"><button id="deviceSelect" data-open="devices" aria-label="Select playback device">'+icon('system')+'<span id="deviceLabel"></span><span class="chevron">⌄</span></button><button id="saveSong" data-music="save" aria-label="Save sample song"></button></div><p class="live-error" id="liveError" role="status"></p></section></div>';if(liveEnabled)renderLiveState();else updateSpotify()}
let drawnTrack=-1, drawnAlbum=null;
function updateSpotify(){const t=music.tracks[playback.index],album=$('album');if(!album)return;if(drawnTrack!==playback.index||drawnAlbum!==album){album.innerHTML=artwork(t);drawnTrack=playback.index;drawnAlbum=album;screen.style.setProperty('--album-color',t.colors[0]);screen.style.setProperty('--album-dark',t.colors[2]);$('songTitle').textContent=t.title;$('songArtist').textContent=t.artist;}const put=(id,v)=>{const el=$(id);if(el.textContent!==v)el.textContent=v};put('playStatus',playback.playing?'PLAYING · SAMPLE':'PAUSED · SAMPLE');put('elapsed',music.time(playback.position));put('duration',music.time(t.duration));const seek=$('seek');seek.max=t.duration;if(document.activeElement!==seek||!seeking)seek.value=playback.position;seek.style.setProperty('--progress',100*playback.position/t.duration+'%');const p=$('playToggle'),pLabel=playback.playing?'Pause':'Play';if(p.getAttribute('aria-label')!==pLabel||!p.firstChild){p.innerHTML=transportIcon(playback.playing?'pause':'play');p.setAttribute('aria-label',pLabel)}$('shuffle').setAttribute('aria-pressed',String(playback.shuffle));$('repeat').setAttribute('aria-pressed',String(playback.repeat!=='off'));$('repeat').setAttribute('aria-label','Repeat: '+playback.repeat);$('repeatOne').hidden=playback.repeat!=='one';const saved=playback.saved.includes(playback.index),s=$('saveSong'),label=saved?'Remove saved sample song':'Save sample song';if(s.getAttribute('aria-label')!==label||!s.firstChild){s.innerHTML=transportIcon(saved?'saved':'save');s.setAttribute('aria-label',label)}s.setAttribute('aria-pressed',String(saved));put('deviceLabel',(playback.playing?'Playing on ':'Selected: ')+playback.device);$('playMode').value=playback.mode}
let seeking=false;
screen.addEventListener('pointerdown',e=>{if(e.target.id==='seek')seeking=true});
window.addEventListener('pointerup',()=>{seeking=false});window.addEventListener('pointercancel',()=>{seeking=false});
function musicAction(action,value,refresh=true){if(liveEnabled){
  if(action==='mode'){
    syncLiveMode();
    if(live.pending||!live.state.connected||live.state.error)return;
    if(value==='echo'&&echoModeSupported())openOverlay('devices',prefs.echoDeviceId?'echo-transfer':'echo-bind');
    else if(value==='wifi')openOverlay('devices','wifi');
  }else live.command(action,value);
  return
}playback=music.reduce(playback,action,value);if(active==='spotify')updateSpotify();schedule()}
let deviceRequest=0;
function syncLiveMode(){
  if(!liveEnabled)return;
  for(const select of screen.querySelectorAll('select[data-mode]')){
    const echo=select.querySelector('option[value=echo]');
    if(echo)echo.textContent=echoModeSupported()?(prefs.echoDeviceId?'Echo':'Echo · set up'):'Echo · paired display only';
    select.value=liveMode();
    select.disabled=live.pending||!live.state.connected||!!live.state.error;
  }
}
function renderDevices(purpose='all'){
  if(liveEnabled){
    const request=++deviceRequest,host=$('devices');
    const valid=()=>overlay==='devices'&&request===deviceRequest;
    const title=purpose==='echo-bind'?'Choose your Echo Show':purpose==='wifi'?'Wi-Fi playback devices':'Playback devices';
    const reset=()=>{
      host.replaceChildren();
      const header=document.createElement('header');header.textContent=title;
      const close=document.createElement('button');close.dataset.close='';close.setAttribute('aria-label','Close playback devices');close.textContent='×';header.append(close);host.append(header);return close;
    };
    const note=text=>{const p=document.createElement('p');p.className='device-note';p.textContent=text;host.append(p)};
    const bind=()=>{const b=document.createElement('button');b.dataset.echoBind='';b.textContent='Configure Echo device';host.append(b)};
    const openSpotify=()=>{
      if(!nativeSpotifyLaunch||!echoModeSupported())return;
      const a=document.createElement('a');a.className='device-option native-spotify-launch';
      a.href='/__desk_open_spotify';a.textContent='Open Spotify';host.append(a);
      note('After Spotify opens, return Home using Android navigation, then select Echo again.');
    };
    const retryEcho=()=>{
      const b=document.createElement('button');b.className='device-option';
      b.textContent='Retry Echo connection';b.addEventListener('click',()=>renderDevices('echo-transfer'));host.append(b);
    };
    reset();note(purpose==='echo-transfer'?'Finding your Echo Show…':'Loading…');
    live.devices().then(list=>{
      if(!valid())return;
      const close=reset();
      if(purpose==='echo-transfer'){
        if(echoDeviceAvailable(list,prefs.echoDeviceId)&&!live.pending&&live.state.connected&&!live.state.error){
          const id=prefs.echoDeviceId;closeOverlay(false);
          if(live.state.deviceId!==id||live.state.inactive)live.command('device',id);
          else renderLiveState();
          return;
        }
        note('Saved Echo device is unavailable. Open Spotify on the Echo Show, or configure the device again if its ID changed.');
        openSpotify();retryEcho();bind();close.focus();return;
      }
      if(purpose==='echo-bind')note('Select only the Spotify device that is physically your Echo Show. This selection is remembered on this display and transfers playback to it.');
      const rows=purpose==='wifi'?list.filter(d=>d.id!==prefs.echoDeviceId):list;
      if(!rows.length)note('No available Spotify devices. Open Spotify on your target device.');
      if(purpose==='echo-bind'||purpose==='all')openSpotify();
      for(const d of rows){
        const b=document.createElement('button');b.className='device-option';
        b.dataset.liveDevice=d.id||'';b.disabled=!normaliseEchoDevice(d.id)||d.restricted;
        if(purpose==='echo-bind')b.dataset.bindEcho='';
        b.setAttribute('aria-pressed',String(d.active));
        b.textContent=d.name+(d.id&&d.id===prefs.echoDeviceId?' · Echo Show':'')+(d.active?' · Active':d.restricted?' · Restricted':'');
        host.append(b)
      }
      close.focus()
    }).catch(()=>{if(valid()){const close=reset();note('Could not load devices. Check Spotify connection.');close.focus()}});
    return
  }
  $('devices').innerHTML='<header>Playback devices<button data-close aria-label="Close playback devices">×</button></header><p class="device-note">Sample devices only · no Spotify connection</p>'+music.devices(playback.mode).map(d=>'<button class="device-option" data-device="'+d+'" aria-pressed="'+(d===playback.device)+'">'+icon('system')+'<span>'+d+'</span><span>'+(d===playback.device?'Selected':'Available')+'</span></button>').join('')}

function updateHomeWeather(){const label=$('homeWeatherLabel'),reading=$('homeWeatherReading');if(!label||!reading)return;label.textContent='Weather · Bournemouth'+(weather.enabled?(weather.status==='fresh'?'':weather.status==='stale'?' · stale':' · unavailable'):' · sample');reading.innerHTML=weather.icon(weather.current.condition,prefs.weatherIcons)+'<span>'+weather.current.temp+'° · '+weather.conditions[weather.current.condition]+'</span>'}
function weatherRows(){return selectRow('Forecast duration','weatherDays',[['3','3 days'],['5','5 days'],['7','7 days']])+selectRow('Weather icons','weatherIcons',[['colour','Colour'],['outline','Outline']])}
function weatherHours(hours,detail=false){
 return hours.map((h,i)=>{
 const label=h.day===1&&(i===0||hours[i-1].day!==h.day)?'Tomorrow':h.day>1&&(i===0||hours[i-1].day!==h.day)?weather.dayLabel(h.day):'';
 const tag=detail?'div':'button',attr=detail?'':' data-hour-day="'+h.day+'" aria-label="'+(label?label+' ':'')+h.time+' details"';
 return '<'+tag+' class="hour-card"'+attr+'><span class="hour-date">'+(label||'&nbsp;')+'</span><span>'+h.time+'</span>'+weather.icon(h.condition,prefs.weatherIcons)+'<strong>'+h.temp+'°</strong><small>Rain '+h.rain+'%</small></'+tag+'>';
 }).join('');
}
function renderWeather(resetScroll=false){
 const w=weather.current, days=weather.forecast(prefs.weatherDays), sym=c=>weather.icon(c,prefs.weatherIcons);
 screen.dataset.weatherCondition=w.condition;
 const previousScroll=resetScroll?0:($('forecastDays')?.scrollLeft||0);
 const stats=[['Feels like',w.feels+'°C'],['Rain today',w.rain+'%'],['Humidity',w.humidity+'%'],['Sunrise',w.sunrise],['Sunset',w.sunset]];
 const isHourly=weatherView==='hourly';
 page.innerHTML='<div class="weather-title"><span>BOURNEMOUTH</span><small>'+(weather.enabled?weather.label():'Sample forecast')+'</small></div><section class="weather-current">'+sym(w.condition)+'<div><div class="weather-temp">'+w.temp+'°</div><div class="weather-condition">'+weather.conditions[w.condition]+'</div></div></section><section class="weather-stats">'+stats.map(([label,value])=>'<div><span>'+label+'</span><strong>'+value+'</strong></div>').join('')+'</section><div class="forecast-heading weather-forecast-heading"><select id="weatherView" aria-label="Forecast view"><option value="hourly" '+(isHourly?'selected':'')+'>Hourly</option><option value="daily" '+(!isHourly?'selected':'')+'>Daily</option></select><span>'+(isHourly?'NEXT 24 HOURS':days.length+'-DAY FORECAST')+'</span></div><div id="forecastDays" tabindex="0" class="forecast-days '+(isHourly?'forecast-hours':'')+'" aria-label="'+(isHourly?'Upcoming hourly forecast':'Daily forecast')+'">'+(isHourly?weatherHours(weather.hourly(0)):days.map((d,i)=>'<button class="forecast-day" data-weather-day="'+i+'"><span>'+weather.dayLabel(i)+'</span>'+sym(i===0?w.condition:d.condition)+'<strong>'+(i===0?w.temp+'° <small>'+(weather.status==='stale'?'Last':'Now')+'</small>':d.high+'° <small>/ '+d.low+'°</small>')+'</strong><small>Rain '+d.rain+'%</small></button>').join(''))+'</div>';
 if($('forecastDays'))$('forecastDays').scrollLeft=previousScroll;
}
function renderWeatherDetails(keepScroll=false){
 const previousScroll=keepScroll?($('detailHours')?.scrollLeft||0):0;
 const d=weather.summary(weatherDay);if(!d){$('weatherDetails').innerHTML='<header>Forecast unavailable<button data-close aria-label="Close">×</button></header><p>No forecast data available.</p>';return;}
 const today=weatherDay===0,sym=c=>weather.icon(c,prefs.weatherIcons);
 const stats=today?[['Daily high',d.high+'°'],['Daily low',d.low+'°'],['Feels like',d.feels+'°'],['Humidity',d.humidity+'%'],['Sunrise',weather.current.sunrise],['Sunset',weather.current.sunset]]:[['Daily high',d.high+'°'],['Daily low',d.low+'°'],['Rain chance',d.rain+'%'],...(weather.enabled?[['Sunrise',d.sunrise],['Sunset',d.sunset]]:[])];
 $('weatherDetails').innerHTML='<header>'+weather.fullDate(weatherDay)+'<button data-close aria-label="Close forecast details">×</button></header><div class="weather-detail-summary">'+sym(d.condition)+'<div><strong>'+(today?d.temp+'°':d.high+'° / '+d.low+'°')+'</strong><span>'+(today?(weather.status==='stale'?'Last update · ':'Current · '):'Forecast · ')+weather.conditions[d.condition]+'</span></div><div class="detail-rain"><span>'+(today?'Rain today':'Rain chance')+'</span><strong>'+d.rain+'%</strong></div></div><div class="forecast-heading"><span>'+(today?'NEXT 24 HOURS':'HOURLY FORECAST')+(weather.enabled?' · '+weather.label():' · SAMPLE')+'</span> </div><div id="detailHours" tabindex="0" class="hourly-days" aria-label="Hourly forecast">'+weatherHours(weather.hourly(weatherDay),true)+'</div><div class="weather-detail-stats">'+stats.map(([label,value])=>'<div><span>'+label+'</span><strong>'+value+'</strong></div>').join('')+'</div>';
 if($('detailHours'))$('detailHours').scrollLeft=previousScroll;
}


// Glucose: reuse original renderer verbatim. No live data, network or credential storage.
function glucoseSelect(key,label,options,value){
 return '<select data-glucose-control="'+key+'" aria-label="'+label+'">'+options.map(([v,t])=>'<option value="'+v+'" '+(String(value)===String(v)?'selected':'')+'>'+t+'</option>').join('')+'</select>';
}
const glucoseViews=[['live','LIVE'],['graph','GRAPH'],['both','BOTH']];
const glucoseRanges=[1,3,6,12,24].map(h=>[h,h+'h']);
const glucoseScales=[['auto','AUTO'],['fixed','FULL']];
function glucoseRows(includeGraph){
 const row=(label,control)=>'<div class="setting"><label>'+label+'</label>'+control+'</div>';
 return selectRow('View','glucoseView',glucoseViews)+selectRow('Background','glucoseBackground',[['green','Green'],['dynamic','Dynamic colours'],['theme','Global theme']])+
 (includeGraph&&prefs.glucoseView!=='live'?row('Graph duration',glucoseSelect('hours','Graph duration',glucoseRanges,glucoseHours))+row('Graph scale',glucoseSelect('scale','Graph scale',glucoseScales,glucoseScale)):'')+
 (glucoseLive.enabled?'':row('Sample scenario',glucoseSelect('scenario','Sample scenario',[['low','Low sample'],['range','In-band sample'],['above','Above-band sample'],['high','High sample']],glucoseScenario)));
}
function changeGlucose(key,value){
 if(key==='view'&&glucoseViews.some(([v])=>v===value)){prefs.glucoseView=value;save()}
 else if(key==='hours'&&[1,3,6,12,24].includes(Number(value)))glucoseHours=Number(value);
 else if(key==='scale'&&['auto','fixed'].includes(value))glucoseScale=value;
 else if(!glucoseLive.enabled&&key==='scenario'&&['low','range','above','high'].includes(value)){glucoseScenario=value;glucoseData=glucosePreview.make(value);apply()}
 else return;
 if(active==='glucose'){
   if(key==='hours'||key==='scale'){
     for(const el of page.querySelectorAll('[data-glucose-control="'+key+'"]'))el.value=value;
     paintGlucose();
   }else renderGlucose();
 }
 if(key==='view'&&overlay==='quick')renderQuick();
}
let glucoseObserver=null;
function paintGlucose(){
 const svg=$('glucosePlot');if(!svg||active!=='glucose')return;
 const width=Math.max(320,Math.round(svg.getBoundingClientRect().width||700));
 const result=window.DeskGlucoseChart.render(glucoseData.readings,{hours:glucoseHours,endTime:glucoseData.endTime,scale:glucoseScale,width});
 svg.setAttribute('viewBox','0 0 '+result.width+' 196');
 svg.innerHTML=result.svg;
 svg.setAttribute('aria-label',(glucoseLive.enabled?'Received ':'Synthetic ')+glucoseHours+'-hour glucose graph, display band 4 to 7 mmol/L, local time axis');const empty=$('glucoseEmpty');if(empty)empty.hidden=!result.noData;
}
function updateHomeGlucose(){
 const label=$('homeGlucoseLabel'),reading=$('homeGlucose');if(!label||!reading)return;
 const s=glucoseData,shown=s.status==='live'||s.status==='sample';
 screen.dataset.glucoseBand=glucosePreview.theme(s.latest?.mmol,s.status);
 label.textContent=s.status==='sample'?'Glucose · sample':'Glucose';
 reading.textContent=shown&&s.latest?s.latest.mmol.toFixed(1)+(s.latest.arrow?' '+s.latest.arrow:''):'Not live';
}
function glucoseAge(){
 const s=glucoseData,p=s.latest;if(!p)return 'No reading available';
 const time=new Date(p.timestamp).toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit'});
 if(s.status==='sample')return 'Sample · '+time;
 const age=Math.max(0,Math.floor((Date.now()-p.timestamp)/60000));
 return (s.status==='stale'?'Last reading · ':'Updated ')+(age<1?'less than 1 min ago':age+' min ago')+' · '+time;
}
function updateGlucoseReading(){
 const s=glucoseData,p=s.latest,status=$('glucoseStatus');
 screen.dataset.glucoseBand=glucosePreview.theme(p?.mmol,s.status);
 if(status){status.textContent=glucoseLive.label(s.status)+(s.status==='stale'&&p?' · '+Math.floor(s.ageSeconds/60)+' min old':'');status.dataset.status=s.status}
 const value=$('glucoseValue'),arrow=$('glucoseArrow'),age=$('glucoseAge');
 if(value)value.textContent=p?p.mmol.toFixed(1):'--';
 if(arrow){arrow.textContent=p?.arrow||'';arrow.hidden=!p?.arrow||s.status==='stale'}
 if(age)age.textContent=glucoseAge();
}
function renderGlucose(){
 if(glucoseObserver){glucoseObserver.disconnect();glucoseObserver=null}
 const view=prefs.glucoseView;
 const reading='<section class="glucose-card glucose-reading"><div class="glucose-number"><strong id="glucoseValue">--</strong><span id="glucoseArrow" class="glucose-arrow" aria-label="Source trend"></span></div><span class="glucose-unit">mmol/L</span><small id="glucoseAge"></small></section>';
 const graph='<section class="glucose-card glucose-graph"><div class="glucose-chart-controls">'+glucoseSelect('hours','Graph duration',glucoseRanges,glucoseHours)+glucoseSelect('scale','Graph scale',glucoseScales,glucoseScale)+'</div><svg id="glucosePlot" role="img" preserveAspectRatio="xMidYMid meet"></svg><div id="glucoseEmpty" class="glucose-empty" hidden>No readings in this period</div></section>';
 page.innerHTML='<div class="glucose-header"><span id="glucoseStatus" class="glucose-sample" role="status"></span>'+glucoseSelect('view','Glucose view',glucoseViews,view)+'</div><div class="glucose-layout" data-view="'+view+'">'+(view==='graph'?'':reading)+(view==='live'?'':graph)+'</div><div class="glucose-footer">NOT FOR TREATMENT · Use the Libre app for decisions and alarms.</div>';
 updateGlucoseReading();paintGlucose();
 if($('glucosePlot')&&typeof ResizeObserver!=='undefined'){
   let previous=0;glucoseObserver=new ResizeObserver(entries=>{
     const width=Math.round(entries[0].contentRect.width);
     if(width&&width!==previous){previous=width;paintGlucose()}
   });
   glucoseObserver.observe($('glucosePlot'));
 }
}
function updateLiveGlucose(){
 if(!glucoseLive.enabled)return;
 glucoseData=glucoseLive.data;
 if(active==='home')updateHomeGlucose();
 if(active==='glucose'){updateGlucoseReading();paintGlucose()}
}

const albumPalette=window.EchoAlbumPalette.createController(document,(colors,url)=>{
  screen.style.setProperty('--album-color',colors.base);
  screen.style.setProperty('--album-dark',colors.dark);
  screen.style.setProperty('--album-image',url?'url('+JSON.stringify(url)+')':'none');
});
function renderLiveState(){
 syncLiveMode();
const s=live.state,home=$('homeTrack');if(home)home.textContent=s.connected?(s.inactive?'No active playback':s.title||'No playback'):'Spotify — not connected';
if(active!=='spotify'||!$('album'))return;
const text=(id,v)=>{$(id).textContent=v};
text('playStatus',!s.connected?'NOT CONNECTED':s.error?'UNAVAILABLE':(live.pending||live.syncing)?(s.playing?'PLAYING · SYNCING':'PAUSED · SYNCING'):s.inactive?(s.recovery==='recent'?'PAUSED · LAST DEVICE':s.recovery==='verified'?'PAUSED · DEVICE AVAILABLE':s.title?'LAST TRACK · DEVICE UNAVAILABLE':'NO ACTIVE PLAYBACK'):s.playing?'NOW PLAYING':s.title?'PAUSED':'NO ACTIVE PLAYBACK');
text('songTitle',live.pendingTrack?(live.pendingTrack==='next'?'Skipping track…':'Going back…'):(s.title||'No music playing'));text('songArtist',live.pendingTrack?'Waiting for Spotify':(s.artist||'Start Spotify on your Xbox, phone or PC'));
text('duration',music.time(s.duration||0));
const seek=$('seek');seek.max=s.duration||1;seek.disabled=live.pending||s.inactive||!!s.error||!s.controllable||!s.duration||!!s.disallows?.seeking;updateLiveProgress();
const album=$('album');if(album.dataset.url!==(s.art||'')||!album.firstChild){
  const art=s.art||'';album.dataset.url=art;
  albumPalette.mount(album,art,()=>active==='spotify'&&$('album')===album&&album.dataset.url===art);
}
const p=$('playToggle');p.innerHTML=transportIcon(s.playing?'pause':'play');p.setAttribute('aria-label',s.playing?'Pause':'Play');
$('shuffle').setAttribute('aria-pressed',String(!!s.shuffle));$('repeat').setAttribute('aria-pressed',String(!!s.repeat&&s.repeat!=='off'));$('repeatOne').hidden=s.repeat!=='track';$('repeat').setAttribute('aria-label','Repeat: '+(s.repeat||'off'));
const save=$('saveSong');save.innerHTML=transportIcon(s.saved?'saved':'save');save.setAttribute('aria-pressed',String(!!s.saved));save.setAttribute('aria-label',s.saved?'Remove saved song':'Save song');save.disabled=live.pending||s.inactive||!s.uri||s.saved===null||!s.connected||!!s.error;
for(const b of page.querySelectorAll('[data-music]')){if(b===save)continue;const key={toggle:s.playing?'pausing':'resuming',previous:'skipping_prev',next:'skipping_next',shuffle:'toggling_shuffle',repeat:'toggling_repeat_context'}[b.dataset.music];b.disabled=live.pending||!!s.error||!s.controllable||!!s.disallows?.[key]}
text('deviceLabel',s.device?(s.playing?'Playing on ':s.recovery==='recent'?'Last device: ':'Selected: ')+s.device:'Select playback device');$('deviceSelect').disabled=live.pending||!s.connected||!!s.error;
const err=$('liveError');err.replaceChildren();if(!s.connected){if(document.documentElement.dataset.deviceGateway==='1'){const a=document.createElement('span');a.className='live-link';a.textContent='Connect Spotify from the private admin dashboard.';err.append(a)}else{const a=document.createElement('a');a.href='/spotify/login';a.className='live-link';a.textContent='Connect Spotify';err.append(a)}}if(s.error||live.message){const span=document.createElement('span');span.textContent=' '+(live.message||s.error);err.append(span)}
}
function updateLiveProgress(){if(!liveEnabled||active!=='spotify'||!$('seek')||seeking)return;const pos=live.position(),seek=$('seek');seek.value=Math.floor(pos);const elapsed=music.time(Math.floor(pos));if($('elapsed').textContent!==elapsed)$('elapsed').textContent=elapsed;}
apply();renderPage();setRail(true);
document.addEventListener('visibilitychange',()=>{if(!document.hidden)updateNightMode()});
if(liveEnabled){$('demo').textContent=document.documentElement.dataset.deviceGateway==='1'?'LIVE · PAIRED DISPLAY':'LOCAL TEST · SECONDARY DISPLAY';screen.style.setProperty('--album-color','#40434c');screen.style.setProperty('--album-dark','#15171a');live.onChange=renderLiveState;live.refresh();setInterval(()=>{if(['spotify','home','system'].includes(active)&&!document.hidden)live.refresh()},5000);setInterval(updateLiveProgress,200)}
setInterval(()=>{if(active==='calendar'&&!document.hidden)refreshCalendar();if(active==='system'&&!document.hidden)refreshSystem()},5000);
setInterval(()=>{clock();updateNightMode();if(active==='calendar'&&calendarToday!==calendarKey(new Date()))renderCalendar();if(!liveEnabled){playback=music.reduce(playback,'tick');if(active==='spotify'&&!overlay)updateSpotify()}},1000);

if(weather.enabled){weather.onChange=()=>{if(active==='home')updateHomeWeather();else if(active==='weather'){renderWeather();if(overlay==='weather')renderWeatherDetails(true)}};weather.refresh();setInterval(()=>{if(['home','weather'].includes(active)&&!document.hidden)weather.refresh()},15000);}

// Calendar grid: one month per deliberate vertical swipe, never scroll the agenda.
let calendarDrag=null,ignoreCalendarClick=false;
screen.addEventListener('pointerdown',e=>{
  ignoreCalendarClick=false;
  if(calendarDrag){if(e.pointerId!==calendarDrag.id)calendarDrag=null;return}
  if(active!=='calendar'||overlay||!e.isPrimary||e.button!==0||!e.target.closest('.cal-grid'))return;
  calendarDrag={id:e.pointerId,x:e.clientX,y:e.clientY,dragged:false};
},true);
window.addEventListener('pointermove',e=>{
  const d=calendarDrag;
  if(!d||d.id!==e.pointerId)return;
  if(active!=='calendar'||overlay){calendarDrag=null;return}
  if(!d.dragged&&Math.hypot(e.clientX-d.x,e.clientY-d.y)>12){
    d.dragged=true;
    try{page.setPointerCapture(e.pointerId)}catch{}
  }
  if(d.dragged&&e.cancelable)e.preventDefault();
},{passive:false});
window.addEventListener('pointerup',e=>{
  const d=calendarDrag;
  if(!d||d.id!==e.pointerId)return;
  calendarDrag=null;
  if(active!=='calendar'||overlay)return;
  const dx=e.clientX-d.x,dy=e.clientY-d.y,action=calendarSwipeDirection(dx,dy);
  if(d.dragged||Math.hypot(dx,dy)>12)ignoreCalendarClick=true;
  if(action)calendarAction(action,false);
});
window.addEventListener('pointercancel',e=>{
  if(calendarDrag?.id===e.pointerId){calendarDrag=null;ignoreCalendarClick=true}
});
screen.addEventListener('click',e=>{
  if(ignoreCalendarClick&&e.detail!==0){ignoreCalendarClick=false;e.preventDefault();e.stopImmediatePropagation()}
},true);

// Forecast strips: native touch scrolling, mouse drag for desktop preview.
// Capture only after a horizontal drag threshold so ordinary card taps still open details.
let forecastDrag=null,ignoreForecastClick=false;
screen.addEventListener('pointerdown',e=>{
 ignoreForecastClick=false;
 forecastDrag=null;
 if(e.pointerType!=='mouse'||e.button!==0)return;
 const strip=e.target.closest('#forecastDays,#detailHours');
 if(!strip||strip.scrollWidth<=strip.clientWidth+1)return;
 forecastDrag={strip,id:e.pointerId,x:e.clientX,y:e.clientY,left:strip.scrollLeft,moved:false};
});
window.addEventListener('pointermove',e=>{
 const d=forecastDrag;if(!d||d.id!==e.pointerId)return;
 if(!d.strip.isConnected){forecastDrag=null;return}
 if(!(e.buttons&1)){finishForecastDrag(e);return}
 const dx=e.clientX-d.x,dy=e.clientY-d.y;
 if(!d.moved){
  if(Math.abs(dx)<7||Math.abs(dx)<Math.abs(dy))return;
  d.moved=true;d.strip.classList.add('forecast-dragging');
  try{d.strip.setPointerCapture(e.pointerId)}catch{}
 }
 e.preventDefault();d.strip.scrollLeft=d.left-dx;
},{passive:false});
function finishForecastDrag(e){
 const d=forecastDrag;if(!d||d.id!==e.pointerId)return;
 forecastDrag=null;
 if(d.moved){
  ignoreForecastClick=true;d.strip.classList.remove('forecast-dragging');
  if(d.strip.hasPointerCapture(e.pointerId))d.strip.releasePointerCapture(e.pointerId);
 }
}
window.addEventListener('pointerup',finishForecastDrag);
window.addEventListener('pointercancel',finishForecastDrag);
screen.addEventListener('click',e=>{
 if(ignoreForecastClick){ignoreForecastClick=false;e.preventDefault();e.stopImmediatePropagation()}
},true);
screen.addEventListener('keydown',e=>{
 if(!e.target.matches('#forecastDays,#detailHours')||!['ArrowLeft','ArrowRight'].includes(e.key))return;
 e.preventDefault();e.target.scrollBy({left:e.key==='ArrowLeft'?-180:180,behavior:'auto'});
});

if(glucoseLive.enabled){
 glucoseLive.onChange=updateLiveGlucose;
 glucoseLive.refresh();
 setInterval(()=>{if(['home','glucose'].includes(active)&&!document.hidden)glucoseLive.refresh()},15000);
 setInterval(()=>{if(['home','glucose'].includes(active))updateLiveGlucose()},10000);
 document.addEventListener('visibilitychange',()=>{if(!document.hidden&&['home','glucose'].includes(active)){updateLiveGlucose();glucoseLive.refresh()}});
}

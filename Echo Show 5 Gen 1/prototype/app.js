'use strict';
const $=id=>document.getElementById(id), screen=$('screen'), page=$('page'), rail=$('rail'), drawer=$('drawer'), quick=$('quick'), shade=$('shade'), reveal=$('reveal');
const apps={home:'Home',spotify:'Spotify',weather:'Weather',glucose:'Glucose',settings:'Settings',calendar:'Calendar',system:'System Information'};
const icons={home:'<path d="M3 10 12 3l9 7v10h-6v-7H9v7H3z"/>',spotify:'<circle cx="12" cy="12" r="10"/><path d="M6 9q6-3 12 1M7 13q5-2 10 1M8 16q4-1 8 1"/>',weather:'<path d="M6 19a5 5 0 0 1-1-10 7 7 0 0 1 13 1 4.5 4.5 0 0 1 0 9z"/>',glucose:'<path d="M12 2C8 8 4 12 4 16a8 8 0 0 0 16 0c0-4-4-8-8-14z"/>',settings:'<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M12 1v3M12 20v3M1 12h3M20 12h3M4 4l2 2M18 18l2 2M4 20l2-2M18 6l2-2"/>',calendar:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M7 2v6M17 2v6M7 14h3M14 14h3M7 18h3"/>',system:'<rect x="2" y="4" width="20" height="14" rx="2"/><path d="M8 22h8M12 18v4M5 11h4l2-4 3 8 2-4h3"/>',apps:'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>'};
const icon=id=>'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">'+icons[id]+'</svg>';
const defaults=()=>({theme:'graphite',railStyle:'floating',opacity:100,delay:10,animation:'slide',speed:180,brightness:100,night:'off',spotifyBackground:'album',weatherDays:'3',weatherIcons:'colour',glucoseView:'both',glucoseBackground:'green',autoHide:{home:true,spotify:true,weather:true,glucose:true,settings:false,calendar:true,system:true}});
const weather=window.EchoWeatherLive.enabled?window.EchoWeatherLive:window.EchoWeatherPreview;let weatherDay=0,weatherView='hourly';
const music=window.EchoSpotifyPreview;let playback=music.initial();const live=window.EchoSpotifyLive;const liveEnabled=live.enabled;
const glucosePreview=window.EchoGlucosePreview,glucoseLive=window.EchoGlucoseLive;let glucoseHours=6,glucoseScale='auto',glucoseScenario='range',glucoseData=glucoseLive.enabled?glucoseLive.data:glucosePreview.make();
const key='echo-show-preview-prefs-v1';let prefs=defaults(),active='home',category='navigation',expanded=true,timer,overlay=null,gesture=null;
try{const p=JSON.parse(localStorage.getItem(key)||'null');if(p&&typeof p==='object'){for(const [k,allowed] of Object.entries({theme:['graphite','black'],railStyle:['floating','transparent','edge'],animation:['none','fade','slide'],night:['off','manual','scheduled'],spotifyBackground:['album','art','theme'],weatherDays:['3','5','7'],weatherIcons:['colour','outline'],glucoseView:['live','graph','both'],glucoseBackground:['green','dynamic','theme']}))if(allowed.includes(p[k]))prefs[k]=p[k];for(const [k,min,max] of [['opacity',25,100],['delay',5,60],['speed',100,350],['brightness',10,100]])if(Number.isFinite(p[k])&&p[k]>=min&&p[k]<=max)prefs[k]=p[k];for(const id of Object.keys(apps))if(typeof p.autoHide?.[id]==='boolean')prefs.autoHide[id]=p.autoHide[id]}}catch{}
function apply(){screen.dataset.glucoseBackground=prefs.glucoseBackground;screen.dataset.glucoseBand=glucosePreview.theme(glucoseData.latest?.mmol,glucoseData.status);screen.dataset.spotifyBackground=prefs.spotifyBackground;screen.dataset.theme=prefs.theme;screen.dataset.rail=prefs.railStyle;screen.dataset.animation=prefs.animation;screen.style.setProperty('--rail-opacity',prefs.opacity/100);screen.style.setProperty('--speed',prefs.speed+'ms');$('dim').style.opacity=String(Math.max((100-prefs.brightness)/100*.75,prefs.night==='manual'?.55:0));}
function save(){try{localStorage.setItem(key,JSON.stringify(prefs))}catch{}apply();schedule()}
function schedule(){clearTimeout(timer);if(expanded&&!overlay&&prefs.autoHide[active]&&!rail.contains(document.activeElement))timer=setTimeout(()=>setRail(false),prefs.delay*1000)}
function setRail(value){expanded=value;screen.classList.toggle('expanded',value);rail.inert=!value;rail.setAttribute('aria-hidden',String(!value));reveal.hidden=value;schedule()}
function renderRail(){rail.innerHTML=['home','spotify','weather','glucose'].map(id=>'<button data-page="'+id+'" aria-label="'+apps[id]+'" '+(active===id?'aria-current="page"':'')+'>'+icon(id)+'</button>').join('')+'<button data-open="drawer" aria-label="Apps" aria-expanded="'+(overlay==='drawer')+'">'+icon('apps')+'</button>'}
function clock(){if(active!=='home')return;const now=new Date();$('clock').textContent=new Intl.DateTimeFormat('en-GB',{hour:'2-digit',minute:'2-digit',hour12:false}).format(now);$('date').textContent=new Intl.DateTimeFormat('en-GB',{weekday:'long',day:'numeric',month:'long'}).format(now)}
function renderPage(){screen.dataset.page=active;renderRail();if(active==='home'){page.innerHTML='<div class="home"><div id="clock" class="clock"></div><div id="date" class="date"></div></div><div class="tiles"><button class="tile" data-page="weather"><span id="homeWeatherLabel">Weather · Bournemouth</span><strong id="homeWeatherReading" class="home-weather">'+weather.icon(weather.current.condition,prefs.weatherIcons)+'<span>'+weather.current.temp+'° · '+weather.conditions[weather.current.condition]+'</span></strong></button><button class="tile" data-page="spotify"><span>Spotify</span><strong id="homeTrack">'+(liveEnabled?'Spotify — connecting':music.tracks[playback.index].title)+'</strong></button><button class="tile" data-page="glucose"><span id="homeGlucoseLabel">Glucose</span><strong id="homeGlucose"></strong></button></div>';clock();updateHomeWeather();updateHomeGlucose()}else if(active==='spotify'){renderSpotify();if(liveEnabled)live.refresh()}else if(active==='weather'){renderWeather()}else if(active==='glucose'){renderGlucose()}else if(active==='settings'){renderSettings()}else{page.innerHTML='<div class="placeholder"><h1>'+apps[active]+'</h1><p>This page is planned for a later prototype increment. No live service is connected.</p><button data-page="home">Return Home</button></div>'}}
function navigate(id){if(!Object.hasOwnProperty.call(apps,id))return;if(glucoseObserver){glucoseObserver.disconnect();glucoseObserver=null}closeOverlay(false);active=id;renderPage();setRail(true);if(weather.enabled&&['home','weather'].includes(active))weather.refresh();if(glucoseLive.enabled&&['home','glucose'].includes(active)){updateLiveGlucose();glucoseLive.refresh()}}
function closeOverlay(restore=true){const previous=overlay;overlay=null;drawer.hidden=true;quick.hidden=true;$('devices').hidden=true;$('weatherDetails').hidden=true;shade.hidden=true;renderRail();if(restore){if(previous==='quick')$('quickHandle').focus();else if(previous==='devices')$('deviceSelect')?.focus();else if(previous==='weather')(page.querySelector('[data-weather-day="'+weatherDay+'"]')||page.querySelector('[data-hour-day="'+weatherDay+'"]')||$('forecastDays'))?.focus();else rail.querySelector('[data-open=drawer]')?.focus()}schedule()}
function openOverlay(id){overlay=id;clearTimeout(timer);shade.hidden=false;drawer.hidden=id!=='drawer';quick.hidden=id!=='quick';$('devices').hidden=id!=='devices';$('weatherDetails').hidden=id!=='weather';if(id==='drawer'){setRail(true);drawer.innerHTML='<header>Apps<button data-close aria-label="Close Apps">×</button></header><div class="app-grid">'+['settings','calendar','system'].map(a=>'<button data-page="'+a+'">'+icon(a)+apps[a]+(a==='settings'?'':'<small>Planned</small>')+'</button>').join('')+'</div>'}else if(id==='devices'){renderDevices()}else if(id==='weather'){renderWeatherDetails()}else{renderQuick()}renderRail();(id==='drawer'?drawer:id==='devices'?$('devices'):id==='weather'?$('weatherDetails'):quick).querySelector('[data-close]')?.focus()}
function selectRow(label,k,options){return '<div class="setting"><label>'+label+'</label><select aria-label="'+label+'" data-pref="'+k+'">'+options.map(([v,t])=>'<option value="'+v+'" '+(String(prefs[k])===String(v)?'selected':'')+'>'+t+'</option>').join('')+'</select></div>'}
function rangeRow(label,k,min,max,step,suffix,note=''){return '<div class="setting"><label>'+label+(note?'<small>'+note+'</small>':'')+'</label><input aria-label="'+label+'" type="range" data-pref="'+k+'" min="'+min+'" max="'+max+'" step="'+step+'" value="'+prefs[k]+'"><output data-output="'+k+'">'+prefs[k]+suffix+'</output></div>'}
const themeRow=()=>selectRow('Theme','theme',[['graphite','Graphite'],['black','Black']]);
const nightRow=()=>selectRow('Night mode','night',[['off','Off'],['manual','Manual (preview)'],['scheduled','Scheduled (planned)']]);
const brightnessRow=()=>rangeRow('Brightness','brightness',10,100,5,'%','Visual dimming only; not hardware backlight');
const delayRow=()=>selectRow('Auto-hide delay','delay',[[5,'5 seconds'],[10,'10 seconds'],[15,'15 seconds'],[30,'30 seconds'],[60,'60 seconds']]);
function renderQuick(){if(active==='glucose'){quick.innerHTML='<header>Glucose quick settings<button data-close aria-label="Close quick settings">×</button></header>'+glucoseRows(true)+'<button data-page="settings">All settings</button>';return}if(active==='weather'){quick.innerHTML='<header>Weather quick settings<button data-close aria-label="Close quick settings">×</button></header>'+weatherRows()+brightnessRow()+'<button data-page="settings">All settings</button>';return}if(active==='spotify'&&liveEnabled){quick.innerHTML='<header>Spotify quick settings<button data-close aria-label="Close quick settings">×</button></header>'+spotifyBackgroundRow()+'<div class="setting"><label>Playback mode</label><span>Wi-Fi</span></div><button data-open="devices">Playback devices</button> <button data-page="settings">All settings</button>';return}if(active==='spotify'){quick.innerHTML='<header>Spotify quick settings<button data-close aria-label="Close quick settings">×</button></header>'+spotifyModeRow()+spotifyBackgroundRow()+ '<div class="setting"><label>Playback device</label><button data-open="devices">'+playback.device+'</button></div><button data-page="settings">All settings</button>';return}quick.innerHTML='<header>'+apps[active]+' quick settings<button data-close aria-label="Close quick settings">×</button></header>'+brightnessRow()+nightRow()+themeRow()+delayRow()+(active==='home'||active==='settings'?'':'<p>App-specific controls will be added with the '+apps[active]+' page.</p>')+'<button data-page="settings">All settings</button>'}
function renderSettings(){page.innerHTML='<h1>Settings</h1><div class="settings-layout"><nav class="categories" aria-label="Settings categories">'+[['general','General'],['navigation','Navigation'],['home','Home'],['spotify','Spotify'],['weather','Weather'],['glucose','Glucose'],['connections','Connections'],['system','System']].map(([id,name])=>'<button data-category="'+id+'" class="'+(category===id?'active':'')+'">'+name+'</button>').join('')+'</nav><div class="details" id="settingsDetails"></div></div>';const d=$('settingsDetails');if(category==='navigation'){d.innerHTML='<h2>Navigation</h2>'+delayRow()+selectRow('Rail style','railStyle',[['floating','Floating'],['transparent','Transparent'],['edge','Edge aligned']])+rangeRow('Opacity','opacity',25,100,5,'%')+Object.entries(apps).map(([id,name])=>'<div class="setting"><label for="hide-'+id+'">Auto-hide on '+name+'</label><input id="hide-'+id+'" type="checkbox" data-hide="'+id+'" '+(prefs.autoHide[id]?'checked':'')+'></div>').join('')+'<p>App pinning and ordering are planned.</p>'}else if(category==='general'){d.innerHTML='<h2>General</h2>'+themeRow()+brightnessRow()+nightRow()+selectRow('Animation','animation',[['none','None'],['fade','Fade'],['slide','Slide']])+rangeRow('Animation speed','speed',100,350,50,' ms')+'<p>Startup: Home · Screen: always on (hardware validation pending).</p>'}else if(category==='glucose'){d.innerHTML='<h2>Glucose</h2>'+glucoseRows(false)+'<p>'+(glucoseLive.enabled?'Gluroo · local connection · minimum 150s source polling.':'Sample readings only.')+' Use the Libre app for monitoring, decisions and alarms.</p>'}else if(category==='weather'){d.innerHTML='<h2>Weather</h2><p>Bournemouth · Fixed location</p>'+weatherRows()+'<p>'+(weather.enabled?'Open-Meteo · refresh every 15 minutes.':'Sample forecast only.')+'</p>'}else if(category==='spotify'){d.innerHTML='<h2>Spotify</h2>'+spotifyBackgroundRow()+'<p>'+(liveEnabled?'Live Wi-Fi playback.':'Sample playback only.')+' Hardware buttons and Echo speaker integration are pending.</p>'}else{d.innerHTML='<h2>'+({home:'Home',spotify:'Spotify',weather:'Weather',glucose:'Glucose',connections:'Connections',system:'System'}[category])+'</h2><p>Settings for this category will be added in a later increment.</p>'}d.insertAdjacentHTML('beforeend','<button data-reset>Reset preview preferences</button>')}
screen.addEventListener('click',e=>{const b=e.target.closest('button');if(e.target===shade){closeOverlay();return}if(!b){if(expanded&&!overlay&&prefs.autoHide[active]&&page.contains(e.target)&&!e.target.closest('input,select,a,label,textarea,[contenteditable]'))setRail(false);return}if(b.id==='reveal'){setRail(true);return}if(b.id==='quickHandle'){openOverlay('quick');return}if(b.hasAttribute('data-close')){closeOverlay();return}if(b.dataset.hourDay!==undefined){weatherDay=Number(b.dataset.hourDay);openOverlay('weather');return}if(b.dataset.weatherDay!==undefined){const i=Number(b.dataset.weatherDay);if(Number.isInteger(i)&&i>=0&&i<weather.validDuration(prefs.weatherDays)){weatherDay=i;openOverlay('weather')}return}if(b.dataset.open){openOverlay(b.dataset.open);return}if(b.dataset.music){musicAction(b.dataset.music);return}if(b.dataset.liveDevice){live.command('device',b.dataset.liveDevice);closeOverlay(false);return}if(b.dataset.device){playback=music.reduce(playback,'device',b.dataset.device);closeOverlay(false);renderSpotify();$('deviceSelect')?.focus();return}if(b.dataset.page){navigate(b.dataset.page);return}if(b.dataset.category){category=b.dataset.category;renderSettings();return}if(b.hasAttribute('data-reset')&&confirm('Reset preview preferences only?')){prefs=defaults();save();renderSettings()}});
screen.addEventListener('input',e=>{const el=e.target,k=el.dataset.pref;if(el.id==='seek'){if(liveEnabled){$('elapsed').textContent=music.time(Number(el.value));return}musicAction('seek',Number(el.value),false);return}if(!k||el.type!=='range')return;prefs[k]=Number(el.value);const o=el.parentElement.querySelector('output');if(o)o.textContent=el.value+(k==='speed'?' ms':'%');save()});
screen.addEventListener('change',e=>{const el=e.target,k=el.dataset.pref;if(el.dataset.glucoseControl){changeGlucose(el.dataset.glucoseControl,el.value);return}if(el.id==='weatherView'){if(['hourly','daily'].includes(el.value)&&el.value!==weatherView){weatherView=el.value;renderWeather(true);$('weatherView')?.focus()}return}if(el.id==='seek'&&liveEnabled){live.command('seek',Number(el.value));return}if(el.dataset.mode!==undefined){musicAction('mode',el.value);if(overlay==='quick')renderQuick();return}if(el.dataset.hide){prefs.autoHide[el.dataset.hide]=el.checked;save();return}if(k&&el.tagName==='SELECT'){prefs[k]=k==='delay'?Number(el.value):el.value;save();if(active==='weather'&&['weatherDays','weatherIcons'].includes(k))renderWeather();if(active==='glucose'&&['glucoseView','glucoseBackground'].includes(k))renderGlucose()}});
screen.addEventListener('pointerdown',e=>{const r=screen.getBoundingClientRect();gesture={x:e.clientX,y:e.clientY,top:e.clientY-r.top<28,edge:r.right-e.clientX<30,control:!!e.target.closest('input,select,button:not(#quickHandle):not(#reveal)')};schedule()});
screen.addEventListener('pointerup',e=>{if(!gesture)return;const dx=e.clientX-gesture.x,dy=e.clientY-gesture.y;const g=gesture;gesture=null;if(overlay||g.control)return;if(g.top&&dy>50&&dy>Math.abs(dx)*1.4)openOverlay('quick');else if(g.edge&&dx< -45&&Math.abs(dx)>Math.abs(dy)*1.4)setRail(true)});
screen.addEventListener('pointercancel',()=>{gesture=null});rail.addEventListener('focusout',()=>setTimeout(schedule,0));screen.addEventListener('keydown',e=>{if(e.key==='Escape'&&overlay){closeOverlay();return}if(e.key==='Escape'&&expanded&&prefs.autoHide[active]){setRail(false);return}schedule()});

// All playback here is deterministic sample state. No audio/API requests.
const transportIcons={previous:'<path d="M5 4v16M19 4 7 12l12 8z" fill="currentColor"/>',next:'<path d="M19 4v16M5 4l12 8-12 8z" fill="currentColor"/>',play:'<path d="m8 4 13 8-13 8z" fill="currentColor"/>',pause:'<path d="M8 5v14M16 5v14" stroke-width="4"/>',shuffle:'<path d="M3 6h3c4 0 8 12 12 12h3m-4-4 4 4-4 4M3 18h3c1.5 0 3-2 4-4m4-4c1-2 3-4 4-4h3m-4-4 4 4-4 4"/>',repeat:'<path d="M4 10V6h15m-4-4 4 4-4 4M20 14v4H5m4-4-4 4 4 4"/>',save:'<circle cx="12" cy="12" r="10"/><path d="M7 12h10M12 7v10"/>',saved:'<circle cx="12" cy="12" r="10"/><path d="m7 12 3 3 7-7"/>'};
const transportIcon=id=>'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">'+transportIcons[id]+'</svg>';
function modeOptions(){if(liveEnabled)return '<option value="wifi">Wi-Fi</option><option disabled>PC · pending</option><option disabled>Echo · pending</option>';return [['wifi','Wi-Fi'],['pc','PC'],['echo','Echo · pending']].map(([id,label])=>'<option value="'+id+'" '+(id===playback.mode?'selected ':'')+(id==='echo'?'disabled':'')+'>'+label+'</option>').join('')}
function spotifyModeRow(){return '<div class="setting"><label>Playback mode</label><select data-mode aria-label="Playback mode">'+modeOptions()+'</select></div>'}
function spotifyBackgroundRow(){return selectRow('Background','spotifyBackground',[['album','Album colours'],['art','Dimmed album artwork'],['theme','Global theme']])}
function artwork(t){return '<svg viewBox="0 0 320 320" role="img" aria-label="Abstract sample album artwork"><rect width="320" height="320" fill="'+t.colors[0]+'"/><circle cx="190" cy="105" r="94" fill="'+t.colors[1]+'"/><path d="M0 235 100 70 210 235 320 115V320H0Z" fill="'+t.colors[2]+'"/><circle cx="112" cy="215" r="66" fill="none" stroke="'+t.colors[1]+'" opacity=".6" stroke-width="12"/><text x="160" y="290" text-anchor="middle" fill="white" font-size="12" letter-spacing="4">SAMPLE ART</text></svg>'}
function renderSpotify(){page.innerHTML='<header class="spotify-header"><span>SPOTIFY</span><select id="playMode" data-mode aria-label="Playback mode">'+modeOptions()+'</select></header><div class="spotify-layout"><div class="album" id="album"></div><section class="player"><div class="song"><small id="playStatus"></small><h1 id="songTitle"></h1><div id="songArtist"></div></div><div class="timeline"><input id="seek" type="range" min="0" step="1" aria-label="Seek track"><div class="times"><span id="elapsed"></span><span id="duration"></span></div></div><div class="transport"><button data-music="shuffle" aria-label="Shuffle" id="shuffle">'+transportIcon('shuffle')+'</button><button data-music="previous" aria-label="Previous">'+transportIcon('previous')+'</button><button class="play" id="playToggle" data-music="toggle" aria-label="Pause"></button><button data-music="next" aria-label="Next">'+transportIcon('next')+'</button><button data-music="repeat" aria-label="Repeat" id="repeat">'+transportIcon('repeat')+'<small id="repeatOne" hidden>1</small></button></div><div class="player-bottom"><button id="deviceSelect" data-open="devices" aria-label="Select playback device">'+icon('system')+'<span id="deviceLabel"></span><span class="chevron">⌄</span></button><button id="saveSong" data-music="save" aria-label="Save sample song"></button></div><p class="live-error" id="liveError" role="status"></p></section></div>';if(liveEnabled)renderLiveState();else updateSpotify()}
let drawnTrack=-1, drawnAlbum=null;
function updateSpotify(){const t=music.tracks[playback.index],album=$('album');if(!album)return;if(drawnTrack!==playback.index||drawnAlbum!==album){album.innerHTML=artwork(t);drawnTrack=playback.index;drawnAlbum=album;screen.style.setProperty('--album-color',t.colors[0]);screen.style.setProperty('--album-dark',t.colors[2]);$('songTitle').textContent=t.title;$('songArtist').textContent=t.artist;}const put=(id,v)=>{const el=$(id);if(el.textContent!==v)el.textContent=v};put('playStatus',playback.playing?'PLAYING · SAMPLE':'PAUSED · SAMPLE');put('elapsed',music.time(playback.position));put('duration',music.time(t.duration));const seek=$('seek');seek.max=t.duration;if(document.activeElement!==seek||!seeking)seek.value=playback.position;seek.style.setProperty('--progress',100*playback.position/t.duration+'%');const p=$('playToggle'),pLabel=playback.playing?'Pause':'Play';if(p.getAttribute('aria-label')!==pLabel||!p.firstChild){p.innerHTML=transportIcon(playback.playing?'pause':'play');p.setAttribute('aria-label',pLabel)}$('shuffle').setAttribute('aria-pressed',String(playback.shuffle));$('repeat').setAttribute('aria-pressed',String(playback.repeat!=='off'));$('repeat').setAttribute('aria-label','Repeat: '+playback.repeat);$('repeatOne').hidden=playback.repeat!=='one';const saved=playback.saved.includes(playback.index),s=$('saveSong'),label=saved?'Remove saved sample song':'Save sample song';if(s.getAttribute('aria-label')!==label||!s.firstChild){s.innerHTML=transportIcon(saved?'saved':'save');s.setAttribute('aria-label',label)}s.setAttribute('aria-pressed',String(saved));put('deviceLabel',(playback.playing?'Playing on ':'Selected: ')+playback.device);$('playMode').value=playback.mode}
let seeking=false;
screen.addEventListener('pointerdown',e=>{if(e.target.id==='seek')seeking=true});
window.addEventListener('pointerup',()=>{seeking=false});window.addEventListener('pointercancel',()=>{seeking=false});
function musicAction(action,value,refresh=true){if(liveEnabled){if(action!=='mode')live.command(action,value);return}playback=music.reduce(playback,action,value);if(active==='spotify')updateSpotify();schedule()}
function renderDevices(){if(liveEnabled){live.devices().then(list=>{if(overlay!=='devices')return;const host=$('devices');host.replaceChildren();const header=document.createElement('header');header.textContent='Playback devices';const close=document.createElement('button');close.dataset.close='';close.setAttribute('aria-label','Close playback devices');close.textContent='×';header.append(close);host.append(header);if(!list.length){const p=document.createElement('p');p.textContent='No available Spotify devices. Open Spotify on your target device.';host.append(p)}for(const d of list){const b=document.createElement('button');b.className='device-option';b.dataset.liveDevice=d.id||'';b.disabled=!d.id||d.restricted;b.setAttribute('aria-pressed',String(d.active));b.textContent=d.name+(d.active?' · Active':d.restricted?' · Restricted':'');host.append(b)}close.focus()}).catch(()=>{if(overlay==='devices')$('devices').innerHTML='<header>Playback devices<button data-close aria-label="Close">×</button></header><p>Could not load devices. Check Spotify connection.</p>'});$('devices').innerHTML='<header>Playback devices<button data-close aria-label="Close">×</button></header><p>Loading…</p>';return}$('devices').innerHTML='<header>Playback devices<button data-close aria-label="Close playback devices">×</button></header><p class="device-note">Sample devices only · no Spotify connection</p>'+music.devices(playback.mode).map(d=>'<button class="device-option" data-device="'+d+'" aria-pressed="'+(d===playback.device)+'">'+icon('system')+'<span>'+d+'</span><span>'+(d===playback.device?'Selected':'Available')+'</span></button>').join('')}

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
const err=$('liveError');err.replaceChildren();if(!s.connected){const a=document.createElement('a');a.href='/spotify/login';a.className='live-link';a.textContent='Connect Spotify';err.append(a)}if(s.error||live.message){const span=document.createElement('span');span.textContent=' '+(live.message||s.error);err.append(span)}
}
function updateLiveProgress(){if(!liveEnabled||active!=='spotify'||!$('seek')||seeking)return;const pos=live.position(),seek=$('seek');seek.value=Math.floor(pos);const elapsed=music.time(Math.floor(pos));if($('elapsed').textContent!==elapsed)$('elapsed').textContent=elapsed;}
apply();renderPage();setRail(true);
if(liveEnabled){$('demo').textContent='LOCAL TEST · SECONDARY DISPLAY';screen.style.setProperty('--album-color','#40434c');screen.style.setProperty('--album-dark','#15171a');live.onChange=renderLiveState;live.refresh();setInterval(()=>{if(active==='spotify'||active==='home')live.refresh()},5000);setInterval(updateLiveProgress,200)}
setInterval(()=>{clock();if(!liveEnabled){playback=music.reduce(playback,'tick');if(active==='spotify'&&!overlay)updateSpotify()}},1000);

if(weather.enabled){weather.onChange=()=>{if(active==='home')updateHomeWeather();else if(active==='weather'){renderWeather();if(overlay==='weather')renderWeatherDetails(true)}};weather.refresh();setInterval(()=>{if(['home','weather'].includes(active)&&!document.hidden)weather.refresh()},15000);}

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

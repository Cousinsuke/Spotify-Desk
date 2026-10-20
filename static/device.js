/* Phase 5.2. The physical-device view uses exactly the same screen styles,
 * colour extraction and icon rendering as the established Desk Thing UI.
 * This controller talks ONLY to authenticated /api/device endpoints. */
'use strict';
const $ = id => document.getElementById(id);
let token = '';
try { token = localStorage.getItem('desk_device_token_v1') || ''; } catch {}
let mode = 'pc', state = null, lastStateTime = 0;
let stream = null, reconnectTimer = null, fallbackTimer = null;
let artKey = '', artworkObjectUrl = null, artworkRequest = null;
let artRetryTimer = null, artRetryFor = '', artRetryCount = 0;
let commandBusy = false, pendingSkip = null, optimisticPlay = null, optimisticVolume = null;
const authHeaders = () => ({Authorization: `Bearer ${token}`});
async function api(path, body=undefined) {
  const options = {headers:{...authHeaders()}, cache:'no-store'};
  if (body !== undefined) {options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(body);}
  const response = await fetch(path,options);
  const data = await response.json().catch(()=>({}));
  if(response.status===401){unpair('Pairing expired or revoked.');throw Error('Pair again.');}
  if(!response.ok||data.ok===false)throw Error(data.error||`HTTP ${response.status}`);
  return data;
}
function hint(text){$('hint').textContent=text;}
function markNetwork(ok,text){$('networkDot').style.background=ok?'#67e6a2':'#5a606b';$('networkText').textContent=text;$('networkText').parentElement.classList.toggle('online',ok);}
function unpair(message=''){
  token='';try{localStorage.removeItem('desk_device_token_v1');}catch{}
  if(stream){stream.abort();stream=null;}
  if(fallbackTimer){clearInterval(fallbackTimer);fallbackTimer=null;}
  if(reconnectTimer){clearTimeout(reconnectTimer);reconnectTimer=null;}
  $('pairOverlay').hidden=false;$('disconnect').hidden=true;
  $('pairError').textContent=message;
  markNetwork(false,'Not paired');$('statusLamp').classList.remove('online');
  $('connectionText').textContent='NOT PAIRED';
}
const DEFAULT_AMBIENT = { rgb:[30,215,96], soft:[65,238,126] };
function applyAmbient(colors = DEFAULT_AMBIENT) {
  const rgb = (colors.rgb || DEFAULT_AMBIENT.rgb).map(v => Math.max(0, Math.min(255, Math.round(v))));
  const soft = (colors.soft || DEFAULT_AMBIENT.soft).map(v => Math.max(0, Math.min(255, Math.round(v))));
  document.documentElement.style.setProperty('--ambient-rgb', rgb.join(', '));
  document.documentElement.style.setProperty('--ambient-soft-rgb', soft.join(', '));
}
function defaultAmbient() { applyAmbient(DEFAULT_AMBIENT); }
function clamp(v,min,max){ return Math.max(min, Math.min(max, v)); }
function rgbToHsl(r,g,b) {
  r/=255; g/=255; b/=255;
  const max = Math.max(r,g,b), min = Math.min(r,g,b);
  let h, s, l = (max + min) / 2;
  if (max === min) { h = s = 0; } else {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = (g - b) / d + (g < b ? 6 : 0); break;
      case g: h = (b - r) / d + 2; break;
      default: h = (r - g) / d + 4; break;
    }
    h /= 6;
  }
  return [h, s, l];
}
function hslToRgb(h,s,l) {
  let r, g, b;
  if (s === 0) { r = g = b = l; } else {
    const hue2rgb = (p,q,t) => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1/6) return p + (q - p) * 6 * t;
      if (t < 1/2) return q;
      if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
      return p;
    };
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    r = hue2rgb(p, q, h + 1/3);
    g = hue2rgb(p, q, h);
    b = hue2rgb(p, q, h - 1/3);
  }
  return [Math.round(r*255), Math.round(g*255), Math.round(b*255)];
}
function boostAmbientColor(rgb) {
  let [h,s,l] = rgbToHsl(rgb[0], rgb[1], rgb[2]);
  s = clamp(Math.max(s, 0.45), 0, 0.8);
  l = clamp(Math.max(l, 0.34), 0.28, 0.56);
  const base = hslToRgb(h,s,l);
  const soft = hslToRgb(h, clamp(s * 0.85, 0.35, 0.75), clamp(l + 0.12, 0.42, 0.72));
  return { rgb: base, soft };
}
function extractAmbientFromImage(img) {
  try {
    const sample = document.createElement('canvas');
    const side = 24;
    sample.width = side; sample.height = side;
    const ctx = sample.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(img, 0, 0, side, side);
    const { data } = ctx.getImageData(0, 0, side, side);
    let r = 0, g = 0, b = 0, wTotal = 0;
    for (let i = 0; i < data.length; i += 4) {
      const alpha = data[i + 3] / 255;
      if (alpha < 0.35) continue;
      const pr = data[i], pg = data[i+1], pb = data[i+2];
      const max = Math.max(pr,pg,pb), min = Math.min(pr,pg,pb);
      const sat = max === 0 ? 0 : (max - min) / max;
      const lum = (pr + pg + pb) / 765;
      let weight = 0.25 + sat * 1.3;
      if (lum < 0.08 || lum > 0.92) weight *= 0.35;
      r += pr * weight; g += pg * weight; b += pb * weight; wTotal += weight;
    }
    if (wTotal <= 0.001) return DEFAULT_AMBIENT;
    return boostAmbientColor([r / wTotal, g / wTotal, b / wTotal]);
  } catch {
    return DEFAULT_AMBIENT;
  }
}
function updateAmbientFromCover() {
  const img = $('cover');
  if (!img || img.hidden || !img.complete || !img.naturalWidth) { defaultAmbient(); return; }
  applyAmbient(extractAmbientFromImage(img));
}

/* Icons are SVG instead of font glyphs, preventing font-dependent misalignment. */
// Both icons share a 24px coordinate space, 28px rendered size and 15px visual height.
// Slight optical offset on the triangle balances it against the symmetrical pause bars.
const PLAY_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 4.5c0-.5.55-.8.99-.5L19.4 11.5c.39.25.39.75 0 1L7.49 20c-.44.3-.99 0-.99-.5V4.5Z"/></svg>';
const PAUSE_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5.8" y="4.5" width="5.15" height="15" rx="1.6"/><rect x="13.05" y="4.5" width="5.15" height="15" rx="1.6"/></svg>';
function setPlaybackIcon(isPlaying) {
  const button = $('play');
  button.innerHTML = isPlaying ? PAUSE_ICON : PLAY_ICON;
  button.dataset.state = isPlaying ? 'playing' : 'paused';
  button.setAttribute('aria-label', isPlaying ? 'Pause' : 'Play');
  document.body.classList.toggle('is-playing', !!isPlaying);
}
function setVolumeSource(source) {
  const isSystem = source === 'system';
  $('volumeSource').textContent = isSystem ? 'SYSTEM' : 'SPOTIFY';
  const description = isSystem ? 'Computer output volume' : 'Spotify device volume';
  $('volume').setAttribute('aria-label', description);
  $('volume').title = description;
}
function setVolumeIcon(percent) {
  const icon = $('volumeIcon');
  const known = Number.isInteger(percent) && percent >= 0 && percent <= 100;
  const level = !known ? 'unknown' : percent === 0 ? 'muted' : percent <= 33 ? 'low' : percent <= 66 ? 'medium' : 'high';
  const speaker = '<path d="M11 5 6 9H3v6h3l5 4V5Z"/>';
  const wave1 = '<path d="M14.5 9a4.2 4.2 0 0 1 0 6"/>';
  const wave2 = '<path d="M17 6.7a7.2 7.2 0 0 1 0 10.6"/>';
  const wave3 = '<path d="M19 4.6a10.5 10.5 0 0 1 0 14.8"/>';
  const mute = '<path d="m15 9 6 6m0-6-6 6"/>';
  let paths = speaker;
  if (level === 'muted') paths += mute;
  else if (level === 'low') paths += wave1;
  else if (level === 'medium') paths += wave1 + wave2;
  else if (level === 'high') paths += wave1 + wave2 + wave3;
  icon.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true">${paths}</svg>`;
  icon.setAttribute('aria-label', known ? `Volume ${percent}%, ${level}` : 'Volume unavailable');
}



function identity(item){return String(item?.track_key||[item?.title,item?.artist,item?.duration_ms].join('|'));}
function fmt(ms){const s=Math.floor(Math.max(0,ms||0)/1000);return `${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`;}
function trackHasChanged(next,pending){
  if(next.has_playback===false)return true;
  if(identity(next)!==pending.key)return true;
  return pending.action==='previous' && pending.progress>8000 &&
    Number(next.progress_ms)<5000 && Number(next.progress_ms)+6500<pending.progress;
}
function setSkipFeedback(action){
  if(!state?.has_playback)return;
  const elapsed=state.playing?Date.now()-lastStateTime:0;
  pendingSkip={action,key:identity(state),progress:(Number(state.progress_ms)||0)+elapsed,
    expires:Date.now()+7000};
  $('artFrame').classList.add('is-changing');
  document.querySelector('.details').classList.add('is-changing');
  $('track').textContent=action==='next'?'Skipping track…':'Going back…';
  $('artist').textContent='Waiting for the new track';$('album').textContent='';
  hint('Changing track…');
}
function clearSkip(){
  pendingSkip=null;
  $('artFrame').classList.remove('is-changing');
  document.querySelector('.details').classList.remove('is-changing');
}
function setMode(next){
  mode=next;
  if(mode!=='pc')document.body.classList.remove('pc-audio');
  $('modeSpotify').classList.toggle('active',mode==='spotify');
  $('modePC').classList.toggle('active',mode==='pc');
  $('modeSpotify').setAttribute('aria-pressed',String(mode==='spotify'));
  $('modePC').setAttribute('aria-pressed',String(mode==='pc'));
}
function renderProgress(){
  if(pendingSkip)return;
  if(!state?.has_playback){$('elapsed').textContent='0:00';$('duration').textContent='0:00';$('progressFill').style.width='0%';return;}
  const duration=Math.max(0,Number(state.duration_ms)||0);
  const offset=(optimisticPlay?.playing ?? state.playing)?Date.now()-lastStateTime:0;
  const progress=Math.max(0,Math.min(duration,(Number(state.progress_ms)||0)+Math.max(0,offset)));
  $('elapsed').textContent=fmt(progress);$('duration').textContent=fmt(duration);
  $('progressFill').style.width=duration?`${100*progress/duration}%`:'0%';
}
function showArtworkFallback(){
  const img=$('cover');
  img.hidden=true;
  img.removeAttribute('src');
  $('fallback').hidden=false;
  if(artworkObjectUrl){URL.revokeObjectURL(artworkObjectUrl);artworkObjectUrl=null;}
  defaultAmbient();
}
function retryArtwork(key){
  if(key!==artKey || artRetryCount>=3)return;
  artRetryCount++;
  clearTimeout(artRetryTimer);
  const delay=[850,2000,4000][artRetryCount-1];
  artRetryTimer=setTimeout(()=>{
    if(key!==artKey || !state || !token || document.hidden)return;
    // A failed request must NOT be treated as a successfully loaded cover.
    artKey='';
    void coverArt(state);
  },delay);
}
async function coverArt(next){
  const key=[mode,identity(next),next.artwork].join('|');
  if(key===artKey)return;
  if(key!==artRetryFor){artRetryFor=key;artRetryCount=0;}
  artKey=key;
  clearTimeout(artRetryTimer);
  if(artworkRequest){artworkRequest.abort();artworkRequest=null;}
  const img=$('cover');
  if(!next.artwork){showArtworkFallback();return;}
  // Don't display the previous song's artwork while the current one is loading.
  img.hidden=true;$('fallback').hidden=false;
  let nextObjectUrl=null;
  try{
    let src=next.artwork;
    if(src.startsWith('/api/device/artwork?key=')){
      const controller=new AbortController();artworkRequest=controller;
      const timeout=setTimeout(()=>controller.abort(),4500);
      let response;
      try{
        response=await fetch(src,{headers:authHeaders(),cache:'no-store',signal:controller.signal});
      }finally{
        clearTimeout(timeout);
        if(artworkRequest===controller)artworkRequest=null;
      }
      if(!response.ok)throw Error(`Artwork not ready (${response.status})`);
      const blob=await response.blob();
      if(!blob.size || !/^image\/(png|jpeg|webp)/.test(blob.type))throw Error('Artwork unavailable');
      nextObjectUrl=URL.createObjectURL(blob);
      src=nextObjectUrl;
    }else if(!src.startsWith('https://'))throw Error('Invalid artwork URL');
    if(key!==artKey){if(nextObjectUrl)URL.revokeObjectURL(nextObjectUrl);return;}
    if(artworkObjectUrl && artworkObjectUrl!==nextObjectUrl)URL.revokeObjectURL(artworkObjectUrl);
    artworkObjectUrl=nextObjectUrl;
    img.src=src;
    if(img.complete&&img.naturalWidth){img.hidden=false;$('fallback').hidden=true;updateAmbientFromCover();}
  }catch(error){
    if(nextObjectUrl)URL.revokeObjectURL(nextObjectUrl);
    if(key!==artKey)return;
    showArtworkFallback();
    retryArtwork(key);
  }
}

function render(next){
  if(!next||!token)return;
  const incomingMode=next.mode||mode;
  if(incomingMode!==mode){clearSkip();optimisticPlay=null;optimisticVolume=null;artKey='';}
  setMode(incomingMode);
  state=next;lastStateTime=Date.now();
  $('pairOverlay').hidden=true;$('disconnect').hidden=false;
  markNetwork(true,`${mode==='pc'?'PC':'WI-FI'} · Paired`);
  $('statusLamp').classList.add('online');$('connectionText').textContent=next.connected===false?'OFFLINE':'CONNECTED';
  if(pendingSkip){
    if(trackHasChanged(next,pendingSkip)||Date.now()>pendingSkip.expires)clearSkip();
  }
  if(optimisticPlay){
    if(next.playing===optimisticPlay.playing||Date.now()>optimisticPlay.expires||!next.has_playback)optimisticPlay=null;
  }
  let playing=optimisticPlay?.playing??Boolean(next.playing);
  setPlaybackIcon(playing&&Boolean(next.has_playback));
  if(!pendingSkip){
    $('track').textContent=next.has_playback?(next.title||'Unknown track'):'Nothing playing';
    $('artist').textContent=next.has_playback?(next.artist||'Unknown artist'):(next.error||'Start a song on your companion');
    $('album').textContent=next.album||'';
    coverArt(next);
  }
  $('deviceName').textContent=next.device||(mode==='pc'?'Local media session':'Spotify Connect');
  setVolumeSource(next.volume_source==='system'?'system':'spotify');
  if(optimisticVolume){
    if(next.volume===optimisticVolume.value||Date.now()>optimisticVolume.expires)optimisticVolume=null;
  }
  const volume=optimisticVolume?.value??next.volume;
  if(Number.isInteger(volume)&&!$('volume').matches(':active')){
    $('volume').value=volume;$('volumeLabel').textContent=`${volume}%`;setVolumeIcon(volume);
    $('knob').style.setProperty('--knob-rotation',`${(volume-50)*2.8}deg`);
  }else if(!Number.isInteger(volume)){
    $('volumeLabel').textContent='--%';setVolumeIcon(null);
  }
  const playable=Boolean(next.has_playback);
  for(const id of ['back','play','next'])$(id).disabled=!playable;
  $('volume').disabled=!next.supports_volume||!Number.isInteger(next.volume);
  renderProgress();
}
async function requestState(){if(!token)return;try{render(await api('/api/device/state'));}catch(e){hint(e.message);}}
// While the backend confirms an accepted command, run a handful of local
// status checks. PC reads its native media session; Spotify uses its shared
// 5s cache and rate-limit protection, never an unbounded API polling loop.
function scheduleConfirmation(){for(const delay of [250,750,1500,2600,4400])setTimeout(()=>{if(token&&!document.hidden)requestState();},delay);}
async function doCommand(action,value){
  if(!token||commandBusy)return;
  if(action!=='mode'&&action!=='volume'&&action!=='volume_step'&&!state?.has_playback)return;
  commandBusy=true;
  const prior=state?{...state}:null;
  const priorMode=mode;
  if(action==='toggle'&&state?.has_playback){
    const duration=Number(state.duration_ms)||0;
    const elapsed=state.playing?Date.now()-lastStateTime:0;
    state={...state,progress_ms:Math.min(duration,(Number(state.progress_ms)||0)+elapsed)};
    lastStateTime=Date.now();
    optimisticPlay={playing:!state.playing,expires:Date.now()+3500};
    setPlaybackIcon(optimisticPlay.playing);
  }
  if(action==='next'||action==='previous')setSkipFeedback(action);
  if(action==='volume'&&Number.isInteger(value)){
    optimisticVolume={value,expires:Date.now()+3000};
    $('volume').value=value;$('volumeLabel').textContent=`${value}%`;setVolumeIcon(value);
  }
  if(action==='volume_step'&&Number.isInteger(state?.volume)){
    const newValue=Math.min(100,Math.max(0,(optimisticVolume?.value??state.volume)+value));
    optimisticVolume={value:newValue,expires:Date.now()+3000};
    $('volume').value=newValue;$('volumeLabel').textContent=`${newValue}%`;setVolumeIcon(newValue);
  }
  if(action==='mode'){
    setMode(value);clearSkip();optimisticPlay=null;optimisticVolume=null;
    $('connectionText').textContent='SWITCHING…';
  }
  try{
    const result=await api('/api/device/action',value===undefined?{action}:{action,value});
    if(action==='mode'){setMode(result.mode||value);artKey='';}
    hint(action==='next'||action==='previous'?'Track command accepted · updating artwork…':'Command accepted · K1–K4 simulate mechanical switches');
    await requestState();scheduleConfirmation();
  }catch(e){
    hint(`Command failed: ${e.message}`);
    clearSkip();optimisticPlay=null;optimisticVolume=null;
    setMode(priorMode);
    if(prior)render(prior);
  }finally{commandBusy=false;}
}
const keyAction=a=>a==='mode'?doCommand('mode',mode==='pc'?'spotify':'pc'):doCommand(a);
for(const button of document.querySelectorAll('[data-action]'))button.addEventListener('click',()=>keyAction(button.dataset.action));
$('back').onclick=()=>keyAction('previous');
$('play').onclick=()=>keyAction('toggle');
$('next').onclick=()=>keyAction('next');
$('modePC').onclick=()=>{if(mode!=='pc')doCommand('mode','pc');};
$('modeSpotify').onclick=()=>{if(mode!=='spotify')doCommand('mode','spotify');};
$('volUp').onclick=()=>doCommand('volume_step',5);
$('volDown').onclick=()=>doCommand('volume_step',-5);
$('knob').addEventListener('wheel',e=>{e.preventDefault();doCommand('volume_step',e.deltaY<0?5:-5);},{passive:false});
$('knob').onclick=()=>doCommand('volume_step',5);
$('volume').addEventListener('input',event=>{$('volumeLabel').textContent=`${event.target.value}%`;setVolumeIcon(Number(event.target.value));});
$('volume').addEventListener('change',event=>doCommand('volume',Number(event.target.value)));
window.addEventListener('keydown',e=>{
  if(e.target instanceof HTMLInputElement||e.target instanceof HTMLTextAreaElement||e.ctrlKey||e.altKey||e.metaKey)return;
  const actions={'1':'previous','2':'toggle','3':'next','4':'mode'};
  if(actions[e.key]){e.preventDefault();keyAction(actions[e.key]);}
  else if(e.key==='ArrowUp'){e.preventDefault();doCommand('volume_step',5);}
  else if(e.key==='ArrowDown'){e.preventDefault();doCommand('volume_step',-5);}
});
$('disconnect').onclick=()=>unpair();
$('pairForm').addEventListener('submit',async e=>{
  e.preventDefault();$('pairError').textContent='Pairing…';
  try{
    const response=await fetch('/api/device/pair',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({name:'Browser Device Simulator',code:$('code').value.trim()})});
    const body=await response.json();
    if(!response.ok||!body.ok)throw Error(body.error||'Pairing failed');
    token=body.token;try{localStorage.setItem('desk_device_token_v1',token);}catch{}
    $('code').value='';$('pairError').textContent='';$('pairOverlay').hidden=true;begin();
  }catch(error){$('pairError').textContent=error.message;}
});
function updateAudio(sample){
  const level=Math.min(1,Math.max(0,Number(sample?.level)||0));
  document.documentElement.style.setProperty('--meter-strength',String(level));
  document.body.classList.toggle('pc-audio',mode==='pc'&&Boolean(sample?.available));
}
function parseSSE(block){
  let eventName='message',data='';
  for(const line of block.split('\n')){
    if(line.startsWith('event:'))eventName=line.slice(6).trim();
    else if(line.startsWith('data:'))data+=line.slice(5).trim();
  }
  if(!data)return;
  try{
    const payload=JSON.parse(data);
    if(eventName==='state')render(payload);
    if(eventName==='meter')updateAudio(payload);
    if(eventName==='revoked')unpair('Pairing revoked on the companion.');
  }catch{}
}
async function runStream(controller){
  const response=await fetch('/api/device/events',{headers:authHeaders(),cache:'no-store',signal:controller.signal});
  if(response.status===401){unpair('Pairing revoked.');return;}
  if(!response.ok||!response.body)throw Error('Streaming not supported');
  const reader=response.body.getReader(),decoder=new TextDecoder();
  let pending='';
  while(!controller.signal.aborted){
    const chunk=await reader.read();if(chunk.done)break;
    pending+=decoder.decode(chunk.value,{stream:true}).replace(/\r/g,'');
    let boundary;
    while((boundary=pending.indexOf('\n\n'))!==-1){
      const block=pending.slice(0,boundary);pending=pending.slice(boundary+2);parseSSE(block);
    }
    if(pending.length>65536)pending='';
  }
}
function begin(){
  if(!token||document.hidden)return;
  if(reconnectTimer){clearTimeout(reconnectTimer);reconnectTimer=null;}
  if(fallbackTimer){clearInterval(fallbackTimer);fallbackTimer=null;}
  if(stream)stream.abort();
  const controller=new AbortController();stream=controller;
  requestState();
  runStream(controller).catch(()=>{}).finally(()=>{
    if(stream!==controller||!token)return;
    stream=null;markNetwork(false,'Reconnecting…');
    if(!fallbackTimer)fallbackTimer=setInterval(requestState,2500);
    if(reconnectTimer)clearTimeout(reconnectTimer);
    reconnectTimer=setTimeout(()=>{if(token&&!document.hidden&&!stream)begin();},4500);
  });
}
document.addEventListener('visibilitychange',()=>{
  if(document.hidden){if(stream)stream.abort();stream=null;}
  else if(token)begin();
});
$('cover').addEventListener('load',()=>{
  $('cover').hidden=false;$('fallback').hidden=true;
  updateAmbientFromCover();
});
$('cover').addEventListener('error',()=>{
  const failed=artKey;
  showArtworkFallback();
  retryArtwork(failed);
});
setInterval(()=>{
  if(pendingSkip&&Date.now()>pendingSkip.expires){clearSkip();if(state)render(state);}
  if(optimisticPlay&&Date.now()>optimisticPlay.expires){optimisticPlay=null;if(state)render(state);}
  renderProgress();
},200);
setVolumeIcon(null);setPlaybackIcon(false);
if(token)begin();else unpair();

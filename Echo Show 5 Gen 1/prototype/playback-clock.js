(function(root){
'use strict';
// Pure clock projection: no timers, network, storage or invented next track.
const finite=(x,fallback=0)=>Number.isFinite(x)?x:fallback;
function position(s,received,now,freezeAt=null){
  if(!s.connected||s.error)return 0;
  const duration=Math.max(0,finite(s.duration));
  const base=Math.max(0,finite(s.positionMs,finite(s.position)*1000)/1000);
  const end=freezeAt===null?now:freezeAt;
  const elapsed=s.playing?Math.max(0,finite(end-received))/1000:0;
  // Bound extrapolation if polling stalls (15s freshness budget).
  return Math.min(duration,base+Math.min(elapsed,15));
}
function matchesIntent(s,intent){
  if(!s.connected||s.error)return false;
  if(intent.action==='toggle'){
    if(s.inactive)return intent.value===false&&(!s.deviceId||s.deviceId===intent.device);
    return s.deviceId===intent.device&&s.playing===intent.value;
  }
  if(intent.action==='device')return s.deviceId===intent.value&&!s.inactive;
  if(s.deviceId!==intent.device||s.inactive)return false;
  if(intent.action==='seek')return Math.abs((s.positionMs??(s.position||0)*1000)/1000-intent.value)<=2;
  if(intent.action==='next'||intent.action==='previous')return !!s.uri&&(s.uri!==intent.uri||(s.position||0)<Math.max(0,intent.position-2));
  if(intent.action==='shuffle')return s.shuffle!==intent.before;
  if(intent.action==='repeat')return s.repeat!==intent.before;
  if(intent.action==='save')return s.saved!==null&&s.saved!==intent.before;
  return true;
}
function acknowledged(s,intent,position){
  if(intent.action==='toggle')return {...s,playing:intent.value,inactive:false,position:Math.floor(position),positionMs:Math.floor(position*1000)};
  if(intent.action==='seek')return {...s,position:intent.value,positionMs:intent.value*1000};
  return s;
}
const api={position,matchesIntent,acknowledged};if(typeof module==='object'&&module.exports)module.exports=api;else root.EchoPlaybackClock=api;
})(typeof globalThis!=='undefined'?globalThis:this);

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
const api={position};if(typeof module==='object'&&module.exports)module.exports=api;else root.EchoPlaybackClock=api;
})(typeof globalThis!=='undefined'?globalThis:this);

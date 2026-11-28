(function(){
'use strict';
const enabled=new URLSearchParams(location.search).get('live')==='1';
const clock=window.EchoPlaybackClock;
let state={connected:false,saved:null},received=performance.now(),freezeAt=null,inFlight=null,commandBusy=false,message='',messageUntil=0,generation=0,override=null;
const trackPending=()=>!!override&&['next','previous'].includes(override.action);
const api={enabled,get state(){return state},get message(){return performance.now()<messageUntil?message:''},get pending(){return commandBusy},get syncing(){return !!override},get pendingTrack(){return override&&['next','previous'].includes(override.action)?override.action:null},position:()=>clock.position(state,received,performance.now(),freezeAt),onChange:null};
const emit=()=>api.onChange?.();
const warn=msg=>{message=msg;messageUntil=performance.now()+12000};
function accept(s,age=0){state=s;received=performance.now()-clock.sampleAge(age);freezeAt=null;emit()}
function reconcile(s){
  if(override){
    // Never discard a real track snapshot while a skip is pending. Keep only
    // the bounded confirmation marker, not a frozen copy of the old song.
    if(trackPending()&&performance.now()<override.expires&&s.connected&&!s.error&&!s.inactive&&s.deviceId===override.device&&!clock.matchesIntent(s,override)){
      accept(s,s.sampleAgeMs);return;
    }
    if(clock.holdIncoming(s,override,performance.now()))return;
    if(performance.now()>=override.expires&&!clock.matchesIntent(s,override)&&s.connected&&!s.error&&!s.inactive&&s.deviceId===override.device)warn('Spotify has not confirmed the update yet.');
    override=null;
  }
  accept(s,s.sampleAgeMs);
}
async function request(path,opts={}){
  let r;
  try{r=await fetch(path,{...opts,cache:'no-store',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Desk-Preview':'1',...(opts.headers||{})}})}
  catch{throw Error('Local Spotify server is unreachable. Check the terminal.')}
  let data;
  try{data=await r.json()}catch{throw Error(r.status===404?'Live API not found. Start live_server.py instead of http.server.':'Local Spotify server returned an invalid response (HTTP '+r.status+'). Check the terminal.')}
  if(!r.ok)throw Error(data.error||'Spotify request failed (HTTP '+r.status+')');
  return data;
}
api.refresh=async(fresh=false,fast=false)=>{
  if(!enabled||commandBusy)return;
  if(inFlight)return inFlight;
  const version=generation;
  fast=fast||trackPending();
  inFlight=(async()=>{try{const next=await request('/api/spotify/state'+(fast?'?fresh=1&fast=1':fresh?'?fresh=1':''));if(version!==generation)return;reconcile(next)}catch(e){if(version!==generation)return;override=null;accept({connected:false,saved:null,error:e.message})}})();
  try{await inFlight}finally{inFlight=null}
};
api.devices=async()=>{const d=await request('/api/spotify/devices');return d.devices||[]};
// Bounded sequential reads after a successful skip. A slow request cannot
// swallow the next confirmation timer, and confirmation stops the burst.
async function confirmTrack(version){
  const start=performance.now();
  for(const delay of [0,250,500,900,1400,2000,2000]){
    if(delay)await new Promise(resolve=>setTimeout(resolve,delay));
    if(version!==generation||commandBusy||document.hidden||!trackPending())break;
    if(performance.now()-start>=8500)break;
    if(inFlight)await inFlight;
    if(version!==generation||commandBusy||document.hidden||!trackPending())break;
    await api.refresh(true,true);
  }
  if(version!==generation||commandBusy||document.hidden)return;
  if(!trackPending()){
    // Metadata is already visible. Fill in any uncached library status later.
    setTimeout(()=>{if(version===generation&&!commandBusy&&!document.hidden&&!trackPending())api.refresh()},250);
  }else{
    // A final regular poll reconciles at/after expiry; never leave a permanent
    // pending label if intermediate responses were stale.
    setTimeout(()=>{if(version===generation&&!commandBusy&&!document.hidden&&trackPending())api.refresh(true)},Math.max(0,override.expires-performance.now()));
  }
}
api.command=async(action,value,expectedDevice=null)=>{
  if(!enabled||commandBusy||!state.connected||state.error)return;
  if(action==='volume'&&(!expectedDevice||state.deviceId!==expectedDevice||state.inactive||state.supportsVolume!==true))return;
  if(action==='toggle')value=!state.playing;
  const pos=api.position(), prior=state, priorReceived=received;
  const intent={action,value,uri:state.uri,trackKey:state.trackKey,device:state.deviceId,position:pos,before:action==='shuffle'?state.shuffle:action==='repeat'?state.repeat:state.saved};
  const payload={action,value,uri:intent.uri,device:intent.device};
  commandBusy=true;const version=++generation;message='';messageUntil=0;
  override=['toggle','seek','next','previous','shuffle','repeat','save'].includes(action)?{...intent,expires:Infinity}:null;
  // Match original Desk: immediate feedback on press; restore prior state on failed write.
  if(['toggle','seek','shuffle','repeat','save'].includes(action))accept(clock.acknowledged(state,intent,pos));
  else {if(action==='device')freezeAt=performance.now();emit()}
  let ok=false,result=null;
  try{
    if(inFlight)await inFlight;
    result=await request('/api/spotify/command',{method:'POST',body:JSON.stringify(payload)});
    ok=true;
    if(override)override.expires=performance.now()+(['next','previous'].includes(action)?7000:3500);
  }catch(e){
    override=null;state=prior;received=priorReceived;freezeAt=null;warn(e.message);
  }finally{
    commandBusy=false;
    if(!api.pendingTrack)freezeAt=null;
    emit();
  }
  // Confirm independently of the write lock. New commands invalidate old timers/results.
  if(ok&&['next','previous'].includes(action)){void confirmTrack(version);return result}
  const delays=!ok?[150]:action==='volume'?[950,3000]:[150,800,2000,3600];
  for(const delay of delays)setTimeout(()=>{if(version===generation&&!commandBusy&&!document.hidden)api.refresh(true)},delay);
  return ok?result:null;
};
window.EchoSpotifyLive=api;
})();

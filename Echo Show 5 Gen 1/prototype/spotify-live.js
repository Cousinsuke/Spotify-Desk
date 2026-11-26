(function(){
'use strict';
const enabled=new URLSearchParams(location.search).get('live')==='1';
const clock=window.EchoPlaybackClock;
let state={connected:false,saved:null},received=performance.now(),freezeAt=null,inFlight=null,commandBusy=false,message='',messageUntil=0,generation=0;
const api={enabled,get state(){return state},get message(){return performance.now()<messageUntil?message:''},get pending(){return commandBusy},position:()=>clock.position(state,received,performance.now(),freezeAt),onChange:null};
const emit=()=>api.onChange?.();
const warn=msg=>{message=msg;messageUntil=performance.now()+12000};
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
function accept(s){state=s;received=performance.now();freezeAt=null;emit()}
async function request(path,opts={}){
  let r;
  try{r=await fetch(path,{...opts,cache:'no-store',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Desk-Preview':'1',...(opts.headers||{})}})}
  catch{throw Error('Local Spotify server is unreachable. Check the terminal.')}
  let data;
  try{data=await r.json()}catch{throw Error(r.status===404?'Live API not found. Start live_server.py instead of http.server.':'Local Spotify server returned an invalid response (HTTP '+r.status+'). Check the terminal.')}
  if(!r.ok)throw Error(data.error||'Spotify request failed (HTTP '+r.status+')');
  return data;
}
api.refresh=async()=>{
  if(!enabled||commandBusy)return;
  if(inFlight)return inFlight;
  const version=generation;
  inFlight=(async()=>{try{const next=await request('/api/spotify/state');if(version!==generation)return;accept(next)}catch(e){if(version!==generation)return;accept({connected:false,saved:null,error:e.message})}})();
  try{await inFlight}finally{inFlight=null}
};
api.devices=async()=>{const d=await request('/api/spotify/devices');return d.devices||[]};
api.command=async(action,value)=>{
  if(!enabled||commandBusy||!state.connected||state.error)return;
  if(action==='toggle')value=!state.playing;
  const pos=api.position();
  const intent={action,value,uri:state.uri,device:state.deviceId,position:pos,before:action==='shuffle'?state.shuffle:action==='repeat'?state.repeat:state.saved};
  const payload={action,value,uri:intent.uri,device:intent.device};
  commandBusy=true;generation++;message='';messageUntil=0;freezeAt=performance.now();emit();
  let latest=null;
  try{
    if(inFlight)await inFlight;
    await request('/api/spotify/command',{method:'POST',body:JSON.stringify(payload)});
    // Show an acknowledged pause/resume/seek immediately; do not fabricate a new track.
    accept(clock.acknowledged(state,intent,pos));
    for(const delay of [250,650,1300]){
      await sleep(delay);
      latest=await request('/api/spotify/state?fresh=1');
      const changed=latest.deviceId&&intent.action!=='device'&&latest.deviceId!==intent.device;
      if(!latest.connected||latest.error||changed||clock.matchesIntent(latest,intent))break;
    }
    if(latest){
      if(latest.connected&&!latest.error&&!clock.matchesIntent(latest,intent))warn('Spotify has not confirmed the update yet.');
      accept(latest);
    }
  }catch(e){warn(e.message)}
  finally{commandBusy=false;freezeAt=null;if(!latest)await api.refresh();emit()}
};
window.EchoSpotifyLive=api;
})();

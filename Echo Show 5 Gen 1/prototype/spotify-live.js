(function(){
'use strict';
const enabled=new URLSearchParams(location.search).get('live')==='1';
let state={connected:false,saved:null},received=performance.now(),freezeAt=null,inFlight=null,commandBusy=false,message='',generation=0;
const api={enabled,get state(){return state},get message(){return message},get pending(){return commandBusy},position:()=>window.EchoPlaybackClock.position(state,received,performance.now(),freezeAt),onChange:null};
const emit=()=>api.onChange?.();
async function request(path,opts={}){
  let r;
  try{r=await fetch(path,{...opts,cache:'no-store',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Desk-Preview':'1',...(opts.headers||{})}})}
  catch{throw Error('Local Spotify server is unreachable. Check the terminal.')}
  let data;
  try{data=await r.json()}catch{
    throw Error(r.status===404?'Live API not found. Start live_server.py instead of http.server.':'Local Spotify server returned an invalid response (HTTP '+r.status+'). Check the terminal.')
  }
  if(!r.ok)throw Error(data.error||'Spotify request failed (HTTP '+r.status+')');
  return data;
}
api.refresh=async()=>{
  if(!enabled||commandBusy)return;
  if(inFlight)return inFlight;
  const version=generation;
  inFlight=(async()=>{try{const next=await request('/api/spotify/state');if(version!==generation)return;state=next;received=performance.now();emit()}catch(e){if(version!==generation)return;state={connected:false,saved:null,error:e.message};received=performance.now();emit()}})();
  try{await inFlight}finally{inFlight=null}
};
api.devices=async()=>{const d=await request('/api/spotify/devices');return d.devices||[]};
api.command=async(action,value)=>{
  if(!enabled||commandBusy||!state.connected||state.error)return;
  const payload={action,value,uri:state.uri,device:state.deviceId};
  commandBusy=true;generation++;message='';freezeAt=performance.now();emit();
  try{
    // Drop older poll results before issuing a command.
    if(inFlight)await inFlight;
    await request('/api/spotify/command',{method:'POST',body:JSON.stringify(payload)});
  }catch(e){message=e.message}
  finally{commandBusy=false;freezeAt=null;await api.refresh();emit()}
};
window.EchoSpotifyLive=api;
})();

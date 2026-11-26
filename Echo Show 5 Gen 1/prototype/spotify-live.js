(function(){
'use strict';
const enabled=new URLSearchParams(location.search).get('live')==='1';
let state={connected:false,saved:null},busy=false,commandBusy=false,message='';
const api={enabled,get state(){return state},get message(){return message},onChange:null};
const emit=()=>api.onChange?.();
async function request(path,opts={}){const r=await fetch(path,{...opts,cache:'no-store',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Desk-Preview':'1',...(opts.headers||{})}});let data;try{data=await r.json()}catch{throw Error('Local live server required. Start live_server.py instead of http.server.')}if(!r.ok)throw Error(data.error||'Spotify request failed');return data}
api.refresh=async()=>{if(!enabled||busy||commandBusy)return;busy=true;try{state=await request('/api/spotify/state');emit()}catch(e){state={connected:false,saved:null,error:e.message};emit()}finally{busy=false}};
api.devices=async()=>{const d=await request('/api/spotify/devices');return d.devices||[]};
api.command=async(action,value)=>{if(!enabled||commandBusy||!state.connected)return;commandBusy=true;message='';try{await request('/api/spotify/command',{method:'POST',body:JSON.stringify({action,value,uri:state.uri,device:state.deviceId})});}catch(e){message=e.message}finally{commandBusy=false;await api.refresh();emit()}};
window.EchoSpotifyLive=api;
})();

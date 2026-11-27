(function(root){
'use strict';
const values={low:3.5,range:6.2,above:10.4,high:16.2};
function theme(value,status){
 if(status!=='sample'&&status!=='live')return 'neutral';
 if(!Number.isFinite(value))return 'neutral';
 return value<4?'low':value<=7?'range':value<15?'above':'high';
}
function make(scenario='range',now=Date.now()){
 const end=Math.floor(now/60000)*60000-120000;
 const value=values[scenario]??values.range;
 // Entirely synthetic deterministic values, not derived from any user's history.
 const readings=Array.from({length:289},(_,i)=>{
   const distance=288-i;
   const v=value+1.05*Math.sin(distance*.13)+.36*Math.sin(distance*.39);
   return {timestamp:end-distance*300000,mmol:Math.round(Math.max(.5,v)*10)/10};
 });
 return {status:'sample',latest:{timestamp:end,mmol:value,arrow:'→'},readings,endTime:now};
}
const api={make,theme};
if(typeof module==='object'&&module.exports)module.exports=api;else root.EchoGlucosePreview=api;
})(typeof globalThis!=='undefined'?globalThis:this);

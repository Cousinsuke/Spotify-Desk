(function(root){
'use strict';
const conditions={clear:'Clear',partly:'Partly cloudy',cloud:'Cloudy',rain:'Light rain',storm:'Thunderstorms',snow:'Snow',fog:'Fog',night:'Clear night'};
const current=Object.freeze({temp:10,feels:7,condition:'partly',humidity:76,rain:20,sunrise:'07:43',sunset:'16:08'});
const days=Object.freeze([
 ['partly',12,7,20],['rain',11,6,70],['clear',13,8,10],['cloud',11,5,25],['rain',10,6,85],['fog',9,4,15],['clear',12,5,5]
].map(([condition,high,low,rain])=>Object.freeze({condition,high,low,rain})));
const validDuration=v=>[3,5,7].includes(Number(v))?Number(v):3;
function dateFor(index,now=new Date()){
 const parts=new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/London',year:'numeric',month:'numeric',day:'numeric'}).formatToParts(now);
 const n=k=>Number(parts.find(p=>p.type===k).value);
 return new Date(Date.UTC(n('year'),n('month')-1,n('day')+index,12));
}
function dayLabel(i,now){return i===0?'Today':i===1?'Tomorrow':new Intl.DateTimeFormat('en-GB',{weekday:'short',day:'numeric',timeZone:'UTC'}).format(dateFor(i,now))}
function fullDate(i,now){return new Intl.DateTimeFormat('en-GB',{weekday:'long',day:'numeric',month:'long',timeZone:'UTC'}).format(dateFor(i,now))}
function forecast(duration){return days.slice(0,validDuration(duration))}
function hourly(i){
 const day=days[i];if(!day)return [];
 return [6,9,12,15,18,21].map((h,j)=>({time:String(h).padStart(2,'0')+':00',temp:Math.round(day.low+(day.high-day.low)*[.15,.5,1,.85,.4,0][j]),rain:Math.min(100,Math.max(0,day.rain+[ -20,-10,0,5,-15,-25][j])),condition:day.condition}));
}
function icon(c,style='colour'){
 const colour=style==='colour',cloud=colour?'#d8e7f4':'none',sun=colour?'#ffd17c':'none',stroke=colour?'#e7f2fc':'currentColor';
 const sunShape='<circle cx="23" cy="23" r="11" fill="'+sun+'" stroke="'+(colour?'#ffd17c':stroke)+'"/><path d="M23 5v5m0 26v5M5 23h5m26 0h5M10 10l4 4m18 18 4 4M10 36l4-4m18-18 4-4" stroke="'+(colour?'#ffd17c':stroke)+'"/>';
 const cloudShape='<path d="M12 39a10 10 0 0 1 1-20 14 14 0 0 1 26 2 10 10 0 0 1-1 18z" fill="'+cloud+'" stroke="'+stroke+'"/>';
 const rain='<path d="m15 45-3 6m13-6-3 6m13-6-3 6" stroke="'+(colour?'#85c8ff':stroke)+'"/>';
 let shape=c==='clear'?sunShape:c==='partly'?'<g transform="translate(0 -1) scale(.8)">'+sunShape+'</g><g transform="translate(6 9) scale(.9)">'+cloudShape+'</g>':c==='night'?'<path d="M36 8a19 19 0 1 0 12 31A20 20 0 0 1 36 8z" fill="'+(colour?'#cbd5fd':'none')+'" stroke="'+stroke+'"/>':cloudShape+(c==='rain'?rain:c==='storm'?'<path d="m28 40-9 10h8l-4 8 14-14h-9l5-4" fill="'+sun+'" stroke="'+stroke+'"/>':c==='snow'?'<path d="M14 47h7m-3.5-3.5v7m11-3.5h7m-3.5-3.5v7" stroke="'+stroke+'"/>':c==='fog'?'<path d="M8 44h36M12 50h29" stroke="'+stroke+'"/>':'');
 return '<svg class="weather-symbol" viewBox="0 0 56 58" aria-hidden="true" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'+shape+'</svg>';
}
const api={conditions,current,forecast,validDuration,dayLabel,fullDate,hourly,icon};
if(typeof module==='object'&&module.exports)module.exports=api;else root.EchoWeatherPreview=api;
})(typeof globalThis!=='undefined'?globalThis:this);

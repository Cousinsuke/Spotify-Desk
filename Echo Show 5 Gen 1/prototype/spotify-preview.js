(function(root){
'use strict';
const tracks=Object.freeze([
{title:'After the Rain',artist:'Example artist',duration:226,colors:['#526c78','#a2c5b7','#234643']},
{title:'Midnight Motion',artist:'Example artist',duration:198,colors:['#514c85','#c3a8d1','#29263d']},
{title:'Drifting Away',artist:'Example artist',duration:258,colors:['#8b604b','#e1bd87','#493429']}
]);
function initial(){return {index:0,position:102,playing:true,shuffle:false,repeat:'off',saved:[],mode:'wifi',device:'Xbox (sample)'}}
const devices=mode=>mode==='wifi'?['Xbox (sample)','iPhone (sample)','Desktop (sample)']:mode==='pc'?['PC companion (sample)']:[];
function reduce(s,action,value){let n={...s,saved:[...s.saved]};const track=tracks[s.index];switch(action){
case 'toggle':n.playing=!s.playing;break;
case 'next':n.index=(s.index+(s.shuffle?2:1))%tracks.length;n.position=0;break;
case 'previous':n.index=(s.index+tracks.length-1)%tracks.length;n.position=0;break;
case 'seek':if(Number.isFinite(value))n.position=Math.max(0,Math.min(track.duration,Math.round(value)));break;
case 'shuffle':n.shuffle=!s.shuffle;break;
case 'repeat':n.repeat=({off:'all',all:'one',one:'off'})[s.repeat];break;
case 'save':n.saved=s.saved.includes(s.index)?s.saved.filter(i=>i!==s.index):[...s.saved,s.index];break;
case 'mode':if(['wifi','pc'].includes(value)&&value!==s.mode){n.mode=value;n.device=devices(value)[0];n.playing=false}break;
case 'device':if(devices(s.mode).includes(value)&&value!==s.device){n.device=value;n.playing=false}break;
case 'tick':if(!s.playing)return s;if(s.position+1<track.duration){n.position=s.position+1;break}if(s.repeat==='one'){n.position=0;break}if(s.index===tracks.length-1&&s.repeat==='off'&&!s.shuffle){n.position=track.duration;n.playing=false;break}return reduce(s,'next');
default:return s;}return n;}
const time=v=>Math.floor(v/60)+':'+String(v%60).padStart(2,'0');
const api={tracks,initial,devices,reduce,time};if(typeof module==='object'&&module.exports)module.exports=api;else root.EchoSpotifyPreview=api;
})(typeof globalThis!=='undefined'?globalThis:this);

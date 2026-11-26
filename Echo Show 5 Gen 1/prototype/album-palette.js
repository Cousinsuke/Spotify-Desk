(function(root){
'use strict';
// Adapted from original Spotify Desk static/ui.js ambient colour sampler.
const neutral=()=>({base:'#40434c',dark:'#15171a'});
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

function paletteFromPixels(data){
  let r=0,g=0,b=0,total=0;
  for(let i=0;i+3<data.length;i+=4){
    if(data[i+3]<89.25)continue;
    const pr=data[i],pg=data[i+1],pb=data[i+2];
    const max=Math.max(pr,pg,pb),min=Math.min(pr,pg,pb);
    const sat=max===0?0:(max-min)/max,lum=(pr+pg+pb)/765;
    let weight=0.25+sat*1.3;
    if(lum<0.08||lum>0.92)weight*=0.35;
    r+=pr*weight;g+=pg*weight;b+=pb*weight;total+=weight;
  }
  if(total<=0.001)return neutral();
  const [h,s,l]=rgbToHsl(r/total,g/total,b/total);
  const hex=rgb=>'#'+rgb.map(v=>v.toString(16).padStart(2,'0')).join('');
  if(s<.045)return {base:hex(hslToRgb(0,0,clamp(l*.45,.18,.32))),dark:'#151515'};
  const saturation=clamp(s*1.15,.16,.67);
  return {base:hex(hslToRgb(h,saturation,clamp(l*.55,.20,.35))),
          dark:hex(hslToRgb(h,saturation*.55,.105))};
}
function fromImage(img,doc){
  try{
    const canvas=doc.createElement('canvas');canvas.width=canvas.height=24;
    const ctx=canvas.getContext('2d',{willReadFrequently:true});
    if(!ctx)return null;
    ctx.drawImage(img,0,0,24,24);
    return paletteFromPixels(ctx.getImageData(0,0,24,24).data);
  }catch{return null}
}
function approvedUrl(raw){
  // Exact HTTPS CDN hosts, ordinary URL path/query characters only; no credentials,
  // ports, fragments, backslashes, quotes, control chars or CSS syntax.
  return typeof raw==='string'&&/^https:\/\/(?:i\.scdn\.co|image-cdn-ak\.spotifycdn\.com|image-cdn-fa\.spotifycdn\.com)\/[A-Za-z0-9_./%?=&+~:-]+$/.test(raw)?raw:'';
}
function createController(doc,apply){
  let key=null,cache=null,serial=0;
  function mount(album,raw,isCurrent){
    const url=approvedUrl(raw),id=++serial;
    const current=()=>id===serial&&isCurrent();
    album.replaceChildren();
    if(!url){
      key=null;cache=null;apply(neutral(),'');
      const p=doc.createElement('div');p.className='placeholder';p.textContent='Spotify';album.append(p);return;
    }
    if(key!==url){key=url;cache=null}
    apply(cache||neutral(),'');
    function load(cors){
      const img=doc.createElement('img');
      img.alt='Album artwork';img.referrerPolicy='no-referrer';
      if(cors)img.crossOrigin='anonymous';
      img.onload=()=>{
        if(!current())return;
        if(cors&&!cache)cache=fromImage(img,doc)||neutral();
        if(!cache)cache=neutral();
        apply(cache,url);
      };
      img.onerror=()=>{
        if(!current())return;
        if(cors){load(false);return}
        cache=null;apply(neutral(),'');
        const p=doc.createElement('div');p.className='placeholder';p.textContent='Artwork unavailable';album.replaceChildren(p);
      };
      album.replaceChildren(img);img.src=url;
    }
    load(!cache);
  }
  return {mount};
}
const api={neutral,paletteFromPixels,fromImage,approvedUrl,createController};
if(typeof module==='object'&&module.exports)module.exports=api;else root.EchoAlbumPalette=api;
})(typeof globalThis!=='undefined'?globalThis:this);

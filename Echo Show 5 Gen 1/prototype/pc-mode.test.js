'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const js=fs.readFileSync(path.join(__dirname,'app.js'),'utf8'),gw=fs.readFileSync(path.join(__dirname,'device_gateway.py'),'utf8');
for(const guard of ["if(pcSelected){renderPCState();return}","else if(!pcSelected)live.command(action,value)","if(!pcSelected)live.command('seek'","if(pcSelected||live.pending","if(pcSelected||document.hidden||volumeRoute","if(pcSelected){remoteVolumePopup('PC volume'","if(epoch!==pcEpoch||!pcSelected)return","if(!pcSelected||pcInFlight||document.hidden)return","if(pcSelected&&['spotify','home'].includes(active))refreshPC()"])assert.ok(js.includes(guard),guard);
assert.ok(gw.includes('"/api/pc/state"'));
assert.ok(!gw.includes('"/api/pc/command"'));
console.log('PC read-only mode source guards passed');

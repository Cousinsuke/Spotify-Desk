'use strict';
const $ = id => document.getElementById(id);
let last = null;
let busy = false;
let blockedUntil = 0;
let lastStatusTime = 0;
let statusInFlight = false;
let playbackOverride = null;
let skipPending = null;
let skipTimer = null;
const VISIBLE_REFRESH_MS = 5000;
const HIDDEN_REFRESH_MS = 20000;
let activeMode = 'spotify';
const PC_PLATFORM = window.DESK_PLATFORM === 'linux' ? 'Linux' : 'Windows';
let pcBusy = false;
let pcStatusBusy = false;
let lastPcArt = '';
let pcVolumeOptimistic = null;


const DEFAULT_AMBIENT = { rgb:[30,215,96], soft:[65,238,126] };
function applyAmbient(colors = DEFAULT_AMBIENT) {
  const rgb = (colors.rgb || DEFAULT_AMBIENT.rgb).map(v => Math.max(0, Math.min(255, Math.round(v))));
  const soft = (colors.soft || DEFAULT_AMBIENT.soft).map(v => Math.max(0, Math.min(255, Math.round(v))));
  document.documentElement.style.setProperty('--ambient-rgb', rgb.join(', '));
  document.documentElement.style.setProperty('--ambient-soft-rgb', soft.join(', '));
}
function defaultAmbient() { applyAmbient(DEFAULT_AMBIENT); }
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
function boostAmbientColor(rgb) {
  let [h,s,l] = rgbToHsl(rgb[0], rgb[1], rgb[2]);
  s = clamp(Math.max(s, 0.45), 0, 0.8);
  l = clamp(Math.max(l, 0.34), 0.28, 0.56);
  const base = hslToRgb(h,s,l);
  const soft = hslToRgb(h, clamp(s * 0.85, 0.35, 0.75), clamp(l + 0.12, 0.42, 0.72));
  return { rgb: base, soft };
}
function extractAmbientFromImage(img) {
  try {
    const sample = document.createElement('canvas');
    const side = 24;
    sample.width = side; sample.height = side;
    const ctx = sample.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(img, 0, 0, side, side);
    const { data } = ctx.getImageData(0, 0, side, side);
    let r = 0, g = 0, b = 0, wTotal = 0;
    for (let i = 0; i < data.length; i += 4) {
      const alpha = data[i + 3] / 255;
      if (alpha < 0.35) continue;
      const pr = data[i], pg = data[i+1], pb = data[i+2];
      const max = Math.max(pr,pg,pb), min = Math.min(pr,pg,pb);
      const sat = max === 0 ? 0 : (max - min) / max;
      const lum = (pr + pg + pb) / 765;
      let weight = 0.25 + sat * 1.3;
      if (lum < 0.08 || lum > 0.92) weight *= 0.35;
      r += pr * weight; g += pg * weight; b += pb * weight; wTotal += weight;
    }
    if (wTotal <= 0.001) return DEFAULT_AMBIENT;
    return boostAmbientColor([r / wTotal, g / wTotal, b / wTotal]);
  } catch {
    return DEFAULT_AMBIENT;
  }
}
function updateAmbientFromCover() {
  const img = $('cover');
  if (!img || img.hidden || !img.complete || !img.naturalWidth) { defaultAmbient(); return; }
  applyAmbient(extractAmbientFromImage(img));
}

/* Icons are SVG instead of font glyphs, preventing font-dependent misalignment. */
// Both icons share a 24px coordinate space, 28px rendered size and 15px visual height.
// Slight optical offset on the triangle balances it against the symmetrical pause bars.
const PLAY_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 4.5c0-.5.55-.8.99-.5L19.4 11.5c.39.25.39.75 0 1L7.49 20c-.44.3-.99 0-.99-.5V4.5Z"/></svg>';
const PAUSE_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5.8" y="4.5" width="5.15" height="15" rx="1.6"/><rect x="13.05" y="4.5" width="5.15" height="15" rx="1.6"/></svg>';
function setPlaybackIcon(isPlaying) {
  const button = $('play');
  button.innerHTML = isPlaying ? PAUSE_ICON : PLAY_ICON;
  button.dataset.state = isPlaying ? 'playing' : 'paused';
  button.setAttribute('aria-label', isPlaying ? 'Pause' : 'Play');
  document.body.classList.toggle('is-playing', !!isPlaying);
}
function setVolumeSource(source) {
  const isSystem = source === 'system';
  $('volumeSource').textContent = isSystem ? 'SYSTEM' : 'SPOTIFY';
  const description = isSystem ? 'Computer output volume' : 'Spotify device volume';
  $('volume').setAttribute('aria-label', description);
  $('volume').title = description;
}
function setVolumeIcon(percent) {
  const icon = $('volumeIcon');
  const known = Number.isInteger(percent) && percent >= 0 && percent <= 100;
  const level = !known ? 'unknown' : percent === 0 ? 'muted' : percent <= 33 ? 'low' : percent <= 66 ? 'medium' : 'high';
  const speaker = '<path d="M11 5 6 9H3v6h3l5 4V5Z"/>';
  const wave1 = '<path d="M14.5 9a4.2 4.2 0 0 1 0 6"/>';
  const wave2 = '<path d="M17 6.7a7.2 7.2 0 0 1 0 10.6"/>';
  const wave3 = '<path d="M19 4.6a10.5 10.5 0 0 1 0 14.8"/>';
  const mute = '<path d="m15 9 6 6m0-6-6 6"/>';
  let paths = speaker;
  if (level === 'muted') paths += mute;
  else if (level === 'low') paths += wave1;
  else if (level === 'medium') paths += wave1 + wave2;
  else if (level === 'high') paths += wave1 + wave2 + wave3;
  icon.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true">${paths}</svg>`;
  icon.setAttribute('aria-label', known ? `Volume ${percent}%, ${level}` : 'Volume unavailable');
}

function trackIdentity(data) {
  if (!data) return '';
  return data.track_key || [data.title, data.artist, data.duration_ms].join('|');
}
function clearSkipFeedback() {
  if (skipTimer !== null) clearTimeout(skipTimer);
  skipTimer = null;
  skipPending = null;
  document.querySelector('.details').classList.remove('is-changing');
  $('artFrame').classList.remove('is-changing');
}
function startSkipFeedback(action) {
  if (!last) return null;
  playbackOverride = null;
  const elapsed = last.playing ? Math.max(0, Date.now() - lastStatusTime) : 0;
  const pending = {
    action,
    oldIdentity: trackIdentity(last),
    oldDevice: last.device_id,
    oldProgress: (last.progress_ms || 0) + elapsed,
    expires: Date.now() + 7000,
  };
  skipPending = pending;
  document.querySelector('.details').classList.add('is-changing');
  $('artFrame').classList.add('is-changing');
  $('track').textContent = action === 'next' ? 'Skipping track…' : 'Going back…';
  $('artist').textContent = 'Waiting for Spotify';
  $('album').textContent = '';
  note('Track change requested…');
  return pending;
}
function skipIsConfirmed(data, pending) {
  if (!data.has_playback || data.device_id !== pending.oldDevice) return true;
  if (trackIdentity(data) !== pending.oldIdentity) return true;
  // Previous can restart the SAME track rather than selecting an earlier one.
  // A substantial backwards jump in playback position confirms that case.
  return pending.action === 'previous' && pending.oldProgress > 8000 &&
    Number.isFinite(data.progress_ms) && data.progress_ms < 5000 &&
    data.progress_ms + 6500 < pending.oldProgress;
}
function verifySkip(pending, attempt = 0) {
  if (skipPending !== pending) return;
  const delays = [280, 850, 1500];
  if (attempt >= delays.length) return; // normal 5-second polling continues
  skipTimer = setTimeout(async () => {
    if (skipPending !== pending) return;
    if (busy || statusInFlight) {
      // Don't drop the verification just because a normal refresh was running.
      skipTimer = setTimeout(() => verifySkip(pending, attempt), 160);
      return;
    }
    await fetchStatus(true);
    if (skipPending === pending) verifySkip(pending, attempt + 1);
  }, delays[attempt]);
}

function mmss(ms) {
  const total = Math.max(0, Math.floor(ms / 1000));
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, '0')}`;
}
function note(message) { $('message').textContent = message; }
function overlay(title, message, button = true) {
  $('overlay').hidden = false;
  $('overlayTitle').textContent = title;
  $('overlayMessage').textContent = message;
  $('connect').hidden = !button;
}
function showState(data) {
  if (skipPending) {
    if (skipIsConfirmed(data, skipPending) || Date.now() >= skipPending.expires) {
      const confirmed = skipIsConfirmed(data, skipPending);
      clearSkipFeedback();
      note(confirmed ? 'Track updated.' : 'Spotify has not confirmed the track change yet. You can refresh manually.');
    } else {
      // The API sometimes returns the OLD song after accepting Next/Previous.
      // Do not flash that stale song back over the pending-change message.
      return;
    }
  }
  if (playbackOverride) {
    if (Date.now() >= playbackOverride.expires || !data.has_playback ||
        data.device_id !== playbackOverride.deviceId ||
        data.playing === playbackOverride.playing) {
      playbackOverride = null;
    } else {
      // Temporarily preserve the pressed state while Spotify catches up.
      data = {
        ...data,
        playing: playbackOverride.playing,
        progress_ms: playbackOverride.progressMs,
      };
    }
  }
  if (!data.connected) {
    setPlaybackIcon(false);
    setVolumeIcon(null);
    defaultAmbient();
    $('statusLamp').classList.remove('online');
    $('connectionText').textContent = 'NOT CONNECTED';
    overlay('Connect to Spotify', 'Authorize the Desk Thing prototype with your existing Spotify developer app.');
    setEnabled(false);
    return;
  }
  $('statusLamp').classList.add('online');
  $('connectionText').textContent = 'CONNECTED';
  $('overlay').hidden = true;
  if (!data.has_playback) {
    setPlaybackIcon(false);
    setVolumeIcon(null);
    defaultAmbient();
    $('track').textContent = 'Nothing playing';
    $('artist').textContent = 'Start a song in Spotify';
    $('album').textContent = '';
    $('deviceName').textContent = 'No active Spotify device';
    $('cover').hidden = true;
    $('volumeLabel').textContent = '--%';
    last = null;
    tick();
    setEnabled(false);
    return;
  }
  setEnabled(true);
  last = data;
  lastStatusTime = Date.now();
  $('track').textContent = data.title;
  $('artist').textContent = data.artist;
  $('album').textContent = data.album;
  $('deviceName').textContent = data.device;
  setPlaybackIcon(data.playing);
  if (data.artwork) {
    const cover = $('cover');
    if (cover.src !== data.artwork) {
      cover.crossOrigin = 'anonymous';
      cover.src = data.artwork;
    }
    cover.hidden = false;
    if (cover.complete) updateAmbientFromCover();
  } else { $('cover').hidden = true; defaultAmbient(); }
  setVolumeSource(activeMode === 'pc' ? data.volume_source : 'spotify');
  if (activeMode === 'pc' && pcVolumeOptimistic) {
    if (Date.now() >= pcVolumeOptimistic.expires ||
        pcVolumeOptimistic.source !== data.volume_source ||
        data.volume === pcVolumeOptimistic.value) {
      pcVolumeOptimistic = null;
    } else {
      data = {...data, volume:pcVolumeOptimistic.value};
      last = data;
    }
  }
  if (Number.isInteger(data.volume)) {
    if (!$('volume').matches(':active')) {
      $('volume').value = data.volume;
      $('volumeLabel').textContent = `${data.volume}%`;
      setVolumeIcon(data.volume);
    }
  } else {
    $('volumeLabel').textContent = '--%';
    setVolumeIcon(null);
  }
  $('volume').disabled = !data.supports_volume || !Number.isInteger(data.volume);
  tick();
}
function setEnabled(enabled) {
  for (const name of ['back', 'play', 'next']) $(name).disabled = !enabled;
  $('volume').disabled = !enabled;
}
function tick() {
  if (skipPending) return; // Freeze progress until Spotify confirms the new track.
  if (!last) {
    $('elapsed').textContent = '0:00';
    $('duration').textContent = '0:00';
    $('progressFill').style.width = '0%';
    return;
  }
  const offset = last.playing ? Math.max(0, Date.now() - lastStatusTime) : 0;
  const progress = Math.min(last.duration_ms, last.progress_ms + offset);
  $('elapsed').textContent = mmss(progress);
  $('duration').textContent = mmss(last.duration_ms);
  $('progressFill').style.width = last.duration_ms ? `${100 * progress / last.duration_ms}%` : '0%';
}
async function fetchStatus(force = false) {
  if (activeMode !== 'spotify') return;
  if (statusInFlight || busy || Date.now() < blockedUntil) return;
  statusInFlight = true;
  try {
    const response = await fetch(force ? '/api/status?fresh=1' : '/api/status', { cache: 'no-store' });
    const json = await response.json();
    if (response.status === 429) {
      blockedUntil = Date.now() + (json.retry_after || 60) * 1000;
      note(`Spotify rate limited. Next automatic attempt after ${json.retry_after || 60} seconds.`);
      return;
    }
    if (!response.ok || !json.ok) throw new Error(json.error || `HTTP ${response.status}`);
    if (activeMode !== 'spotify') return;
    showState(json);
    if (json.connected && !skipPending) {
      // Keep explicit confirmation/error notes from a just-finished skip.
      if (!json.has_playback) note('No active Spotify playback. Start a song in Spotify, then click Refresh track. Or select Find Spotify devices.');
    }
  } catch (error) {
    note(`Unable to refresh status: ${error.message}`);
  } finally {
    statusInFlight = false;
  }
}
function optimisticUpdate(action, value) {
  if (!last) return;
  if (action === 'toggle') {
    const elapsed = last.playing ? Math.max(0, Date.now() - lastStatusTime) : 0;
    const progressMs = Math.min(last.duration_ms, last.progress_ms + elapsed);
    const nowPlaying = !last.playing;
    last = { ...last, playing: nowPlaying, progress_ms: progressMs };
    lastStatusTime = Date.now();
    playbackOverride = {
      deviceId: last.device_id,
      playing: nowPlaying,
      progressMs,
      expires: Date.now() + 3500,
    };
    setPlaybackIcon(nowPlaying);
    tick();
  } else if (action === 'volume' && Number.isInteger(value)) {
    last = { ...last, volume: value };
    $('volume').value = value;
    $('volumeLabel').textContent = `${value}%`;
    setVolumeIcon(value);
  } else if (action === 'next' || action === 'previous') {
    startSkipFeedback(action);
  }
}
async function command(action, value) {
  if (activeMode === 'pc') return pcCommand(action, value);
  if (busy || Date.now() < blockedUntil) return;
  busy = true;
  const previousState = last ? {...last} : null;
  const previousStatusTime = lastStatusTime;
  optimisticUpdate(action, value);
  try {
    const response = await fetch('/api/control', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(value === undefined ? {action} : {action, value}),
    });
    const json = await response.json();
    if (!response.ok || !json.ok) {
      if (response.status === 429) blockedUntil = Date.now() + (json.retry_after || 60) * 1000;
      if (response.status === 409) {
        await fetchStatus(true); // Remove any stale track immediately.
      }
      throw new Error(json.error || `HTTP ${response.status}`);
    }
    if ((action === 'next' || action === 'previous') && skipPending) {
      const pending = skipPending;
      note('Track change sent. Waiting for Spotify to report the new track…');
      verifySkip(pending);
      // Never get stuck indefinitely in the pending visual state.
      setTimeout(() => {
        if (skipPending !== pending) return;
        clearSkipFeedback();
        if (last) showState(last);
        note('Spotify has not confirmed the new track. Use Refresh track if needed.');
      }, 7100);
    } else {
      note(`${action === 'toggle' ? 'Play/pause' : action} command sent.`);
      setTimeout(() => fetchStatus(true), 950);
      setTimeout(() => fetchStatus(true), 3000);
    }
  } catch (error) {
    playbackOverride = null;
    clearSkipFeedback();
    if (previousState) {
      last = previousState;
      lastStatusTime = previousStatusTime;
      setPlaybackIcon(previousState.playing);
      if (Number.isInteger(previousState.volume)) {
        $('volume').value = previousState.volume;
        $('volumeLabel').textContent = `${previousState.volume}%`;
        setVolumeIcon(previousState.volume);
      }
      showState(previousState);
      tick();
    }
    note(`Command failed: ${error.message}`);
    // Reconcile with Spotify as soon as possible; respect any 429 cooldown.
    setTimeout(() => fetchStatus(true), 250);
  } finally {
    busy = false;
    if (last) setEnabled(true);
  }
}
$('play').onclick = () => command('toggle');
$('next').onclick = () => command('next');
$('back').onclick = () => command('previous');
$('refresh').onclick = () => activeMode === 'pc' ? fetchPcStatus(true) : fetchStatus(true);
$('volume').addEventListener('input', event => {
  $('volumeLabel').textContent = `${event.target.value}%`;
  setVolumeIcon(Number(event.target.value));
});
$('volume').addEventListener('change', event => command('volume', Number(event.target.value)));
window.addEventListener('keydown', event => {
  if (event.target.matches('input, textarea, select')) return;
  const action = event.code === 'Space' ? 'toggle' : event.code === 'ArrowRight' ? 'next' : event.code === 'ArrowLeft' ? 'previous' : null;
  if (action) { event.preventDefault(); command(action); }
});
async function findDevices() {
  if (activeMode !== 'spotify') { note('Spotify Connect device selection is only available in Wi-Fi mode.'); return; }
  const panel = $('devicePicker');
  panel.hidden = false;
  panel.replaceChildren();
  const heading = document.createElement('h2');
  heading.textContent = 'Spotify Connect devices';
  panel.append(heading);
  const info = document.createElement('p');
  info.textContent = 'Looking for available devices…';
  panel.append(info);
  try {
    const response = await fetch('/api/devices', {cache:'no-store'});
    const data = await response.json();
    if (!response.ok || !data.ok) {
      if (response.status === 429) blockedUntil = Date.now() + (data.retry_after || 60) * 1000;
      throw new Error(data.error || `HTTP ${response.status}`);
    }
    if (!data.devices.length) {
      info.textContent = 'No Spotify devices found. Open Spotify on your PC or phone, start a song, then click Find Spotify devices again.';
      return;
    }
    info.textContent = 'Choose where Spotify should play. Selecting a device will not automatically start music.';
    for (const d of data.devices) {
      const line = document.createElement('div');
      line.className = 'device-option';
      const label = document.createElement('span');
      label.textContent = `${d.name} (${d.type})${d.active ? ' · active' : ''}`;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = d.restricted ? 'Unavailable' : (d.active ? 'Use device' : 'Select device');
      btn.disabled = d.restricted;
      btn.onclick = async () => {
        btn.disabled = true;
        try {
          const r = await fetch('/api/activate', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({device_id:d.id})
          });
          const result = await r.json();
          if (!r.ok || !result.ok) {
            if (r.status === 429) blockedUntil = Date.now() + (result.retry_after || 60) * 1000;
            throw new Error(result.error || `HTTP ${r.status}`);
          }
          panel.hidden = true;
          await fetchStatus(true);
          note(result.message);
        } catch (e) {
          note(`Device selection failed: ${e.message}`);
          btn.disabled = false;
        }
      };
      line.append(label, btn);
      panel.append(line);
    }
  } catch(e) { info.textContent = `Device lookup failed: ${e.message}`; }
}
$('devices').onclick = findDevices;
setPlaybackIcon(false);
setVolumeIcon(null);
setEnabled(false);
fetchStatus();
// Spotify's public Web API is poll-based; a 5-second foreground check balances latency and quota.
// Never poll the Web API every second. Use the local desktop companion for event-driven updates later.
let lastBackgroundCheckAt = 0;
setInterval(() => {
  if (!document.hidden) {
    fetchStatus();
  } else if (Date.now() - lastBackgroundCheckAt >= HIDDEN_REFRESH_MS) {
    lastBackgroundCheckAt = Date.now();
    fetchStatus();
  }
}, VISIBLE_REFRESH_MS);
setInterval(tick, 250);
let lastFocusRefreshAt = 0;
function refreshWhenReturning() {
  if (document.hidden || Date.now() - lastFocusRefreshAt < 2000) return;
  lastFocusRefreshAt = Date.now();
  if (activeMode === 'pc') fetchPcStatus(true); else fetchStatus(true);
}
document.addEventListener('visibilitychange', () => {
  if (!document.hidden) refreshWhenReturning();
});
window.addEventListener('focus', refreshWhenReturning);

$('cover').addEventListener('load', updateAmbientFromCover);
$('cover').addEventListener('error', defaultAmbient);
defaultAmbient();


// Local mode uses Windows GSMTC/WASAPI or Linux MPRIS/PipeWire via the same localhost Flask app.
function switchMode(mode) {
  if (mode !== 'pc' && mode !== 'spotify') return;
  activeMode = mode;
  pcVolumeOptimistic = null;
  setVolumeSource(mode === 'pc' ? 'system' : 'spotify');
  playbackOverride = null;
  clearSkipFeedback();
  last = null;
  lastStatusTime = Date.now();
  lastPcArt = '';
  $('cover').hidden = true;
  $('track').textContent = 'Connecting…';
  $('artist').textContent = mode === 'pc' ? `${PC_PLATFORM} media sessions` : 'Spotify API';
  $('album').textContent = '';
  $('deviceName').textContent = 'Checking playback';
  $('devicePicker').hidden = true;
  $('devices').hidden = mode === 'pc';
  $('modeSpotify').classList.toggle('active', mode === 'spotify');
  $('modePC').classList.toggle('active', mode === 'pc');
  $('modeSpotify').setAttribute('aria-pressed', String(mode === 'spotify'));
  $('modePC').setAttribute('aria-pressed', String(mode === 'pc'));
  $('audioStatus').hidden = mode !== 'pc';
  $('audioStatus').textContent = mode === 'pc' ? `Checking ${PC_PLATFORM} output audio…` : '';
  document.body.classList.remove('pc-audio');
  document.documentElement.style.setProperty('--meter-strength', '0');
  setPlaybackIcon(false);
  setEnabled(false);
  defaultAmbient();
  stopPcAudioStream();
  if (mode === 'pc') {
    fetchPcStatus(true);
    startPcAudioStream();
  } else fetchStatus(true);
}
async function fetchPcStatus(force = false) {
  if (activeMode !== 'pc' || pcStatusBusy) return;
  pcStatusBusy = true;
  try {
    const r = await fetch(force ? '/api/pc/status?fresh=1':'/api/pc/status', {cache:'no-store'});
    const data = await r.json();
    if (!r.ok || !data.ok) throw new Error(data.error || `HTTP ${r.status}`);
    if (activeMode !== 'pc') return;
    // Linux MPRIS and Windows GSMTC share the same display data shape.
    showState(data);
    $('overlay').hidden = true;
    if (data.has_playback) note(`PC MODE · ${data.source || PC_PLATFORM} · Local controls active`);
    else note(`PC MODE · No ${PC_PLATFORM} media session. Start a local media player.`);
  } catch (error) {
    if (activeMode !== 'pc') return;
    $('overlay').hidden = true;
    setEnabled(false);
    $('track').textContent = 'PC mode unavailable';
    $('artist').textContent = `Check ${PC_PLATFORM} media dependencies`;
    note(`PC mode: ${error.message}`);
  } finally { pcStatusBusy = false; }
}
async function pcCommand(action, value) {
  if (activeMode !== 'pc' || pcBusy) return;
  pcBusy = true;
  const old = last ? { ...last } : null;
  if (action === 'volume' && last) {
    pcVolumeOptimistic = {value, source:last.volume_source, expires:Date.now() + 3000};
    last = {...last, volume:value};
    $('volumeLabel').textContent = `${value}%`;
    setVolumeIcon(value);
  }
  if (action === 'toggle' && last) {
    last = {...last, playing:!last.playing};
    setPlaybackIcon(last.playing);
  } else if (action === 'next' || action === 'previous') {
    $('track').textContent = action === 'next' ? 'Skipping track…' : 'Going back…';
    $('artist').textContent = `${PC_PLATFORM} media session`;
  }
  try {
    const r = await fetch('/api/pc/control', {method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify(value === undefined ? {action} : {action,value})});
    const data = await r.json();
    if (!r.ok || !data.ok) throw new Error(data.error || `HTTP ${r.status}`);
    note(`PC MODE · ${action} command accepted`);
    setTimeout(() => fetchPcStatus(true), 180);
    setTimeout(() => fetchPcStatus(true), 650);
  } catch (err) {
    pcVolumeOptimistic = null;
    if (old) {last=old; showState(old); setPlaybackIcon(old.playing);}
    note(`${PC_PLATFORM} control failed: ` + err.message);
    setTimeout(() => fetchPcStatus(true), 250);
  } finally {pcBusy = false;}
}
// A persistent EventSource replaces the ~6 GET requests/sec of Phase 3.2.
// Only local RMS sound-level values are streamed, never audio samples.
let pcAudioSource = null;
let pcAudioFallbackBusy = false;
let pcAudioStreamFailureAt = 0;
let pcAudioStreamConnected = false;

function showPcMeter(meter) {
  if (activeMode !== 'pc' || document.hidden) return;
  const available = !!meter.available;
  document.body.classList.toggle('pc-audio', available);
  document.documentElement.style.setProperty('--meter-strength',
    String(Math.max(0, Math.min(1, Number(meter.level) || 0))));
  const label = available
    ? `Audio-reactive glow active · Output: ${meter.device || `${PC_PLATFORM} default`}`
    : `Timed glow fallback · ${meter.message || 'No loopback audio'}`;
  if ($('audioStatus').textContent !== label) $('audioStatus').textContent = label;
}

function stopPcAudioStream() {
  if (pcAudioSource) pcAudioSource.close();
  pcAudioSource = null;
  pcAudioStreamConnected = false;
}

function startPcAudioStream() {
  if (activeMode !== 'pc' || document.hidden || pcAudioSource || !window.EventSource) return;
  const source = new EventSource('/api/pc/audio/stream');
  pcAudioSource = source;
  pcAudioStreamConnected = false;
  source.onopen = () => {
    if (pcAudioSource === source) pcAudioStreamConnected = true;
  };
  source.onmessage = (event) => {
    if (pcAudioSource !== source || activeMode !== 'pc') return;
    try { showPcMeter(JSON.parse(event.data)); } catch { /* malformed sample: ignore */ }
  };
  source.onerror = () => {
    if (pcAudioSource !== source) return;
    stopPcAudioStream();
    pcAudioStreamFailureAt = Date.now();
    // The fallback uses low-rate polling; retry streaming later.
  };
}

async function updatePcMeter() {
  if (activeMode !== 'pc' || document.hidden || pcAudioSource || pcAudioFallbackBusy) return;
  pcAudioFallbackBusy = true;
  try {
    const r = await fetch('/api/pc/audio', {cache:'no-store'});
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const meter = await r.json();
    showPcMeter(meter);
  } catch {
    if (activeMode === 'pc') document.body.classList.remove('pc-audio');
  } finally { pcAudioFallbackBusy = false; }
}
$('modeSpotify').onclick = () => switchMode('spotify');
$('modePC').onclick = () => switchMode('pc');
setInterval(() => { if (activeMode === 'pc' && !document.hidden) fetchPcStatus(); }, 800);
// Stream is preferred; low-rate HTTP is a fallback only.
setInterval(() => {
  if (activeMode !== 'pc' || document.hidden) return;
  if (!pcAudioSource && (!window.EventSource || Date.now() - pcAudioStreamFailureAt >= 15000)) {
    startPcAudioStream();
  }
  if (!pcAudioSource) updatePcMeter();
}, 300);
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    stopPcAudioStream();
  } else if (activeMode === 'pc') {
    startPcAudioStream();
  }
});

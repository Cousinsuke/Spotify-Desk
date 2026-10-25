/* Desktop browser preview for Home / Weather / Glucose.
 * Deliberately independent from the accepted Spotify playback controller.
 * Glucose is sample data only: no Abbott sign-in, real reading or private API.
 */
(function () {
  'use strict';
  const surface = document.querySelector('.screen .surface');
  const topbar = surface && surface.querySelector('.topbar');
  if (!surface || !topbar) return;
  const byId = id => document.getElementById(id);
  const tabs = [
    ['home', 'Home'], ['spotify', 'Spotify'], ['weather', 'Weather'], ['glucose', 'Glucose']
  ];
  const brandSub = topbar.querySelector('.brand-sub');
  const nav = document.createElement('nav');
  nav.className = 'desk-tabs';
  nav.setAttribute('role', 'tablist');
  nav.setAttribute('aria-label', 'Desk screens');
  tabs.forEach(([name, label]) => {
    const button = document.createElement('button');
    button.className = 'desk-tab';
    button.type = 'button';
    button.setAttribute('role', 'tab');
    button.dataset.deskOpen = name;
    button.textContent = label;
    nav.appendChild(button);
  });
  topbar.insertBefore(nav, topbar.querySelector('.topright'));
  // Substitute the Spotify Wi-Fi/PC switch visually ONLY on the glucose page.
  // Never remove or modify the actual playback-mode buttons or their listeners.
  const topright = topbar.querySelector('.topright');
  const playbackModes = topright.querySelector('.mode-switch');
  const glucoseModes = document.createElement('div');
  glucoseModes.className = 'desk-glucose-modes';
  glucoseModes.setAttribute('role', 'group');
  glucoseModes.setAttribute('aria-label', 'Glucose display layout');
  for (const [mode, label] of [['live', 'LIVE'], ['graph', 'GRAPH'], ['both', 'BOTH']]) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'desk-glucose-mode';
    b.dataset.glucoseView = mode;
    b.textContent = label;
    glucoseModes.appendChild(b);
  }
  topright.insertBefore(glucoseModes, playbackModes);
  let glucoseViewMode = 'both';
  try {
    const previousMode = localStorage.getItem('desk_glucose_layout_v1');
    if (['live', 'graph', 'both'].includes(previousMode)) glucoseViewMode = previousMode;
  } catch {}
  function setGlucoseView(mode) {
    if (!['live', 'graph', 'both'].includes(mode)) return;
    glucoseViewMode = mode;
    const panel = byId('desk-glucose');
    if (panel) panel.dataset.glucoseView = mode;
    glucoseModes.querySelectorAll('button').forEach(b => {
      b.setAttribute('aria-pressed', String(b.dataset.glucoseView === mode));
    });
    try { localStorage.setItem('desk_glucose_layout_v1', mode); } catch {}
    if (mode !== 'live' && panel && surface.dataset.deskPage === 'glucose') drawGraph();
  }
  glucoseModes.addEventListener('click', event => {
    const target = event.target.closest('[data-glucose-view]');
    if (target) setGlucoseView(target.dataset.glucoseView);
  });

  const view = document.createElement('div');
  view.className = 'desk-view';
  view.id = 'deskView';
  view.innerHTML = [
    '<section class="desk-panel" id="desk-home" role="tabpanel" aria-label="Home">',
      '<div class="desk-hero"><div><span class="desk-kicker">YOUR DESK · AT A GLANCE</span>',
      '<div class="desk-clock" id="deskClock">--:--</div><div class="desk-date" id="deskDate">Loading date</div></div>',
      '<div class="desk-hero-note">YOUR DESK THING<strong>Home</strong><span>Swipe to explore</span></div></div>',
      '<div class="desk-cards">',
        '<button type="button" class="desk-card" data-desk-open="spotify"><span class="desk-card-icon" aria-hidden="true">♫</span><strong>Music</strong><span class="desk-card-value" id="deskMusicValue">Spotify</span><small id="deskMusicSub">Open player</small></button>',
        '<button type="button" class="desk-card" data-desk-open="weather"><span class="desk-card-icon" aria-hidden="true">☀</span><strong>Weather</strong><span class="desk-card-value" id="deskWeatherValue">--°</span><small id="deskWeatherSub">Choose a city</small></button>',
        '<button type="button" class="desk-card" data-desk-open="glucose"><span class="desk-card-icon" aria-hidden="true">◇</span><strong>Glucose</strong><span class="desk-card-value">Not connected</span><small>Sample graph only</small></button>',
      '</div>',
    '</section>',
    '<section class="desk-panel" id="desk-weather" role="tabpanel" aria-label="Weather" hidden>',
      '<div class="desk-panel-head"><div><span class="desk-kicker">FORECAST</span><h2>Weather</h2><p class="desk-muted" id="deskWeatherLocation">Location not loaded</p></div>',
      '<form class="desk-weather-search" id="deskWeatherForm"><label for="deskCity" class="desk-kicker">City</label>',
      '<input id="deskCity" type="text" maxlength="70" autocomplete="off" aria-label="Weather city" placeholder="City name" required>',
      '<button type="submit">Update</button></form></div>',
      '<div class="desk-weather-current"><div class="desk-weather-focus">',
      '<div class="desk-weather-icon" id="deskWeatherIcon" aria-hidden="true">☁</div><div>',
      '<div class="desk-temp" id="deskWeatherTemp">--°</div><p class="desk-muted" id="deskWeatherCondition">Checking forecast…</p></div></div>',
      '<div class="desk-weather-meta">',
      '<div class="desk-stat"><small>Feels like</small><strong id="deskFeels">--°</strong></div>',
      '<div class="desk-stat"><small>Humidity</small><strong id="deskHumidity">--%</strong></div>',
      '<div class="desk-stat"><small>Wind</small><strong id="deskWind">-- km/h</strong></div>',
      '<div class="desk-stat"><small>Rain now</small><strong id="deskRain">-- mm</strong></div>',
      '</div></div><div class="desk-forecast"><span class="desk-kicker">NEXT HOURS</span>',
      '<div id="deskHourly" class="desk-hourly" aria-label="Hourly weather forecast"></div></div>',
      '<p class="desk-weather-note" id="deskWeatherNote">Weather data: Open-Meteo</p>',
    '</section>',
    '<section class="desk-panel" id="desk-glucose" role="tabpanel" aria-label="Glucose" hidden>',
      '<div class="desk-panel-head"><div><span class="desk-kicker">GLUCOSE</span>',
      '<h2>Libre 2 Plus</h2><p class="desk-muted">No live glucose integration configured</p></div>',
      '<span class="desk-demo-badge">SAMPLE DATA</span></div>',
      '<div class="desk-glucose-info"><div class="desk-glucose-primary"><div class="desk-glucose-readout"><strong>--.-</strong><span class="desk-glucose-unit">mmol/L</span><span class="desk-glucose-trend" aria-label="No trend available"></span></div>',
      '<p class="desk-glucose-reading-note">Current glucose is unavailable.</p></div></div>',
      '<div class="desk-chart-head"><strong>GLUCOSE TREND · SAMPLE DATA</strong>',
      '<div class="desk-chart-tools"><div class="desk-chart-range" role="group" aria-label="Glucose chart time range">',
      '<button type="button" class="desk-range" data-hours="1">1h</button>',
      '<button type="button" class="desk-range" data-hours="3">3h</button>',
      '<button type="button" class="desk-range" data-hours="6">6h</button>',
      '<button type="button" class="desk-range" data-hours="12">12h</button>',
      '<button type="button" class="desk-range" data-hours="24">24h</button>',
      '</div><button type="button" class="desk-scale" id="deskChartScale" aria-label="Chart scale: automatic" title="Toggle automatic or full-range vertical scale">AUTO</button></div></div>',
      '<div class="desk-plot"><svg id="deskGlucosePlot" viewBox="0 0 700 196" preserveAspectRatio="none" role="img" aria-label="Synthetic glucose graph, not a live sensor reading"></svg>',
      '<span class="desk-plot-watermark">SAMPLE</span><span class="desk-plot-empty" hidden>No readings in this period</span></div>',
      '<div class="desk-plot-axis"><span id="deskGraphStart">6h ago</span><span></span><span>Now</span></div>',
      '<p class="desk-glucose-footer">NOT FOR TREATMENT <span aria-hidden="true">·</span> Use the Libre app for decisions and alarms.</p>',
    '</section>'
  ].join('');
  surface.insertBefore(view, surface.querySelector('#pairOverlay'));

  // Historical LibreView CSVs are read entirely in this browser. No upload,
  // localStorage, backend endpoint, Abbott credential, or LAN glucose API.
  const glucosePanel = byId('desk-glucose');
  glucosePanel.dataset.feedStatus = 'sample';
  setGlucoseView(glucoseViewMode);
  const glucoseHeader = glucosePanel.querySelector('.desk-panel-head');
  const glucoseSubtitle = glucoseHeader.querySelector('.desk-muted');
  const glucoseBadge = glucoseHeader.querySelector('.desk-demo-badge');
  const glucoseNumber = glucosePanel.querySelector('.desk-glucose-info strong');
  const glucoseReadingDetails = glucosePanel.querySelector('.desk-glucose-info p');
  const glucoseTrend = glucosePanel.querySelector('.desk-glucose-trend');
  const glucoseChartTitle = glucosePanel.querySelector('.desk-chart-head strong');
  const glucoseWatermark = glucosePanel.querySelector('.desk-plot-watermark');
  const glucoseAxis = glucosePanel.querySelector('.desk-plot-axis');
  const importActions = document.createElement('div');
  importActions.className = 'desk-glucose-actions';
  const importAllowed = location.hostname === '127.0.0.1' || location.hostname === 'localhost';
  if (importAllowed) {
    const dateFormat = document.createElement('select');
    dateFormat.id = 'deskCsvDateOrder';
    dateFormat.setAttribute('aria-label', 'CSV day month order');
    dateFormat.innerHTML = '<option value="DMY">UK D/M/Y</option><option value="MDY">US M/D/Y</option>';
    importActions.appendChild(dateFormat);
    const label = document.createElement('label');
    label.className = 'desk-csv-import';
    label.textContent = 'Import CSV';
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.csv,.tsv,text/csv,text/tab-separated-values';
    fileInput.id = 'deskHistoryInput';
    label.appendChild(fileInput);
    importActions.appendChild(label);
    const clearButton = document.createElement('button');
    clearButton.type = 'button';
    clearButton.textContent = 'Clear';
    clearButton.id = 'deskClearHistory';
    clearButton.hidden = true;
    importActions.appendChild(clearButton);
    fileInput.addEventListener('change', async () => {
      const file = fileInput.files && fileInput.files[0];
      fileInput.value = '';
      if (!file) return;
      if (!window.DeskGlucoseHistory) {
        glucoseSubtitle.textContent = 'Glucose history parser unavailable.';
        return;
      }
      try {
        if (file.size > 12000000) throw Error('Export is larger than 12 MB.');
        const text = await file.text();
        const parsed = window.DeskGlucoseHistory.parseLibreViewCsv(text, {dateOrder:dateFormat.value});
        historicalGlucose = parsed;
        clearButton.hidden = false;
        const latest = parsed.readings[parsed.readings.length - 1];
        const timeLabel = new Date(latest.timestamp).toLocaleString('en-GB',
          {day:'numeric',month:'short',year:'numeric',hour:'2-digit',minute:'2-digit'});
        glucoseBadge.textContent = 'HISTORY · NOT LIVE';
        glucoseSubtitle.textContent = parsed.readings.length + ' exported readings loaded locally';
        glucoseNumber.textContent = latest.mmol.toFixed(1);
        glucoseTrend.textContent = '';
        glucosePanel.dataset.feedStatus = 'history';
        glucoseReadingDetails.textContent = 'Exported ' + timeLabel + ' · not live';
        glucoseChartTitle.textContent = 'GLUCOSE TREND';
        glucoseWatermark.textContent = 'HISTORY';
        glucoseAxis.children[1].textContent = '';
        glucoseAxis.children[2].textContent = 'Last export';
        document.querySelector('[data-desk-open="glucose"] .desk-card-value').textContent = 'History loaded';
        const glucoseCard = document.querySelector('[data-desk-open="glucose"] small');
        if (glucoseCard) glucoseCard.textContent = 'Exported CSV · not live';
        drawGraph();
      } catch (error) {
        // Do not log file contents, names, glucose records or personally identifying data.
        glucoseSubtitle.textContent = 'Import failed: ' + String(error.message || 'Invalid CSV');
      }
    });
    clearButton.addEventListener('click', () => {
      historicalGlucose = null;
      clearButton.hidden = true;
      glucoseBadge.textContent = 'SAMPLE DATA';
      glucoseSubtitle.textContent = 'No live glucose integration configured';
      glucoseNumber.textContent = '--.-';
      glucoseTrend.textContent = '';
      glucosePanel.dataset.feedStatus = 'sample';
      glucoseReadingDetails.textContent = 'Current glucose is unavailable.';
      glucoseChartTitle.textContent = 'GLUCOSE TREND · SAMPLE DATA';
      glucoseWatermark.textContent = 'SAMPLE';
      glucoseAxis.children[1].textContent = '';
      glucoseAxis.children[2].textContent = 'Now';
      document.querySelector('[data-desk-open="glucose"] .desk-card-value').textContent = 'Not connected';
      const glucoseCard = document.querySelector('[data-desk-open="glucose"] small');
      if (glucoseCard) glucoseCard.textContent = 'Sample graph only';
      drawGraph();
    });
  } else {
    glucoseSubtitle.textContent = 'Import CSV on the PC using 127.0.0.1 · no live connection';
  }
  glucoseHeader.insertBefore(importActions, glucoseBadge);
  let historicalGlucose = null;

  // An independent optional feed: upstream HTTPS on PC, localhost bearer auth
  // to browser, never served to a LAN client. Browser polling does not bypass
  // the backend's >=150-second source cache. No direct Abbott connection.
  let liveGlucose = null;
  let liveConfigured = false;
  const TREND_SYMBOLS = {
    DoubleUp: '↑↑', SingleUp: '↑', FortyFiveUp: '↗', Flat: '→',
    FortyFiveDown: '↘', SingleDown: '↓', DoubleDown: '↓↓'
  };
  const liveAllowed = importAllowed; // Protect health information from HTTP LAN.
  const glucoseHome = document.querySelector('[data-desk-open="glucose"] .desk-card-value');
  const glucoseHomeHint = document.querySelector('[data-desk-open="glucose"] small');
  function historyLabel(timestamp) {
    return new Date(timestamp).toLocaleString('en-GB', {
      day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'
    });
  }
  function showLiveStatus(data) {
    if (historicalGlucose || !data || data.status === 'not_configured') return;
    liveConfigured = true;
    importActions.hidden = true; // Live mode takes precedence over CSV upload controls.
    const valid = data.latest && Number.isFinite(data.latest.mmol) &&
      Number.isFinite(data.latest.timestamp);
    const isLive = data.status === 'live' && valid;
    liveGlucose = valid ? data : null;
    if (isLive) {
      glucoseBadge.textContent = 'LIVE';
      glucoseSubtitle.textContent = '';
      glucoseNumber.textContent = data.latest.mmol.toFixed(1);
      glucoseTrend.textContent = TREND_SYMBOLS[data.latest.direction] || '';
      glucoseTrend.setAttribute('aria-label', data.latest.direction || 'Trend unavailable');
      glucosePanel.dataset.feedStatus = 'live';
      glucoseReadingDetails.textContent = 'Updated ' + Math.max(0, Math.floor(data.age_seconds / 60)) +
        'm ago · ' + historyLabel(data.latest.timestamp);
      glucoseChartTitle.textContent = 'GLUCOSE TREND';
      glucoseWatermark.textContent = '';
      glucoseHome.textContent = data.latest.mmol.toFixed(1) + ' mmol/L';
      glucoseHomeHint.textContent = 'Feed · ' + Math.floor(data.age_seconds / 60) + 'm old';
    } else {
      glucoseBadge.textContent = data.status === 'stale' ? 'STALE' : 'OFFLINE';
      glucoseTrend.textContent = '';
      glucoseTrend.setAttribute('aria-label', 'No current trend available');
      glucosePanel.dataset.feedStatus = data.status === 'stale' ? 'stale' : 'offline';
      glucoseSubtitle.textContent = 'Check Libre app';
      glucoseNumber.textContent = valid ? data.latest.mmol.toFixed(1) : '--.-';
      glucoseReadingDetails.textContent = valid
        ? 'Last reading ' + historyLabel(data.latest.timestamp) + ' · not current'
        : 'No recent readings · check Libre app';
      glucoseChartTitle.textContent = 'GLUCOSE TREND';
      glucoseWatermark.textContent = 'NOT LIVE';
      glucoseHome.textContent = 'Not live';
      glucoseHomeHint.textContent = 'Feed stale or unavailable';
    }
    drawGraph();
  }
  async function refreshLiveGlucose() {
    if (!liveAllowed || document.hidden) return;
    let bearer = '';
    try { bearer = localStorage.getItem('desk_device_token_v1') || ''; } catch {}
    if (!bearer) return;
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 14000);
      let response;
      try {
        response = await fetch('/api/device/glucose', {
          cache:'no-store', headers:{Authorization:'Bearer ' + bearer}, signal:controller.signal
        });
      } finally { clearTimeout(timeout); }
      if (!response.ok) {
        if (response.status === 401) return;
        throw Error('Glucose bridge unavailable');
      }
      const data = await response.json();
      if (data.status === 'not_configured') return;
      showLiveStatus(data);
    } catch {
      if (liveConfigured && !historicalGlucose) {
        showLiveStatus({status:'unavailable',latest:liveGlucose && liveGlucose.latest});
      }
    }
  }

  function drawLiveGraph() {
    paintGlucoseGraph(liveGlucose.readings || [], Date.now(), false);
  }

  let currentPage = 'home';
  let city = 'London';
  try {
    const savedCity = localStorage.getItem('desk_weather_city_v1');
    if (savedCity && savedCity.length >= 2 && savedCity.length <= 70) city = savedCity;
  } catch {}
  byId('deskCity').value = city;
  let weather = null;
  let weatherUpdated = 0;
  let weatherInFlight = null;
  let rangeHours = 6;
  let chartScale = 'auto';

  const setText = (id, value) => { const el = byId(id); if (el) el.textContent = value; };
  const finite = n => typeof n === 'number' && Number.isFinite(n);
  const rounded = (n, unit) => finite(n) ? Math.round(n) + unit : '--' + unit;
  const CONDITIONS = [
    [[0], 'Clear sky', '☀'],
    [[1, 2], 'Partly cloudy', '☀'],
    [[3], 'Overcast', '☁'],
    [[45, 48], 'Foggy', '≋'],
    [[51, 53, 55, 56, 57], 'Drizzle', '☂'],
    [[61, 63, 65, 66, 67, 80, 81, 82], 'Rain', '☂'],
    [[71, 73, 75, 77, 85, 86], 'Snow', '❄'],
    [[95, 96, 99], 'Thunderstorms', 'ϟ']
  ];
  function condition(code) {
    const match = CONDITIONS.find(entry => entry[0].includes(code));
    return match ? [match[1], match[2]] : ['Conditions unavailable', '☁'];
  }
  function updateClock() {
    const now = new Date();
    setText('deskClock', new Intl.DateTimeFormat('en-GB', {hour:'2-digit', minute:'2-digit', hour12:false}).format(now));
    setText('deskDate', new Intl.DateTimeFormat('en-GB', {weekday:'long', day:'numeric', month:'long'}).format(now));
    const track = byId('track') && byId('track').textContent;
    const artist = byId('artist') && byId('artist').textContent;
    if (track && track !== 'Waiting for companion' && track !== 'No track playing') {
      setText('deskMusicValue', track);
      setText('deskMusicSub', artist || 'Open player');
    } else {
      setText('deskMusicValue', 'Spotify');
      setText('deskMusicSub', 'Open player');
    }
  }
  function setPage(page) {
    if (!tabs.some(tab => tab[0] === page)) return;
    currentPage = page;
    surface.dataset.deskPage = page;
    if (brandSub) brandSub.textContent = '/ ' + page.toUpperCase();
    for (const button of nav.querySelectorAll('button')) {
      const selected = button.dataset.deskOpen === page;
      button.setAttribute('aria-selected', String(selected));
      button.tabIndex = selected ? 0 : -1;
    }
    for (const panel of view.querySelectorAll('.desk-panel')) {
      panel.hidden = panel.id !== 'desk-' + page;
    }
    if (page === 'weather' || page === 'home') {
      if (!weather || Date.now() - weatherUpdated > 15 * 60 * 1000) refreshWeather();
    }
    if (page === 'glucose') { drawGraph(); refreshLiveGlucose(); }
  }
  nav.addEventListener('keydown', event => {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    const current = tabs.findIndex(tab => tab[0] === currentPage);
    const direction = event.key === 'ArrowRight' ? 1 : -1;
    const next = tabs[(current + direction + tabs.length) % tabs.length][0];
    setPage(next);
    nav.querySelector('[data-desk-open="' + next + '"]').focus();
  });
  surface.addEventListener('click', event => {
    const button = event.target.closest('[data-desk-open]');
    if (button) setPage(button.dataset.deskOpen);
  });
  let touchStart = null;
  surface.addEventListener('touchstart', event => {
    if (event.touches.length === 1) {
      touchStart = {x:event.touches[0].clientX, y:event.touches[0].clientY};
    }
  }, {passive:true});
  surface.addEventListener('touchend', event => {
    if (!touchStart || event.changedTouches.length !== 1) return;
    const dx = event.changedTouches[0].clientX - touchStart.x;
    const dy = event.changedTouches[0].clientY - touchStart.y;
    touchStart = null;
    if (Math.abs(dx) < 65 || Math.abs(dx) < Math.abs(dy) * 1.7) return;
    if (event.target.closest('input,form,button,.pair-overlay,.transport,.volume-group')) return;
    const index = tabs.findIndex(tab => tab[0] === currentPage);
    setPage(tabs[(index + (dx < 0 ? 1 : -1) + tabs.length) % tabs.length][0]);
  }, {passive:true});

  async function getJson(url) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(url, {signal:controller.signal, cache:'no-store'});
      if (!response.ok) throw Error('Weather service HTTP ' + response.status);
      return await response.json();
    } finally {
      clearTimeout(timer);
    }
  }
  function updateWeatherUI() {
    if (!weather) return;
    const data = weather.data;
    const current = data.current || {};
    const place = weather.place;
    const [description, icon] = condition(current.weather_code);
    setText('deskWeatherLocation', place.name + (place.country ? ', ' + place.country : ''));
    setText('deskWeatherSub', place.name + ' · ' + description);
    setText('deskWeatherValue', rounded(current.temperature_2m, '°'));
    setText('deskWeatherIcon', icon);
    setText('deskWeatherTemp', rounded(current.temperature_2m, '°'));
    setText('deskWeatherCondition', description);
    setText('deskFeels', rounded(current.apparent_temperature, '°'));
    setText('deskHumidity', rounded(current.relative_humidity_2m, '%'));
    setText('deskWind', rounded(current.wind_speed_10m, ' km/h'));
    setText('deskRain', finite(current.precipitation) ? current.precipitation.toFixed(1) + ' mm' : '-- mm');
    const hourly = data.hourly || {};
    const times = Array.isArray(hourly.time) ? hourly.time : [];
    const now = typeof current.time === 'string' ? current.time.substring(0, 13) : '';
    let index = times.findIndex(time => typeof time === 'string' && time.substring(0, 13) >= now);
    if (index < 0) index = 0;
    const strip = byId('deskHourly');
    strip.replaceChildren();
    for (let i = index; i < Math.min(times.length, index + 5); i++) {
      const box = document.createElement('div');
      box.className = 'desk-hour';
      const hour = document.createElement('span');
      hour.textContent = times[i].slice(11, 16);
      const temp = document.createElement('strong');
      temp.textContent = rounded((hourly.temperature_2m || [])[i], '°');
      const rain = document.createElement('small');
      rain.textContent = rounded((hourly.precipitation_probability || [])[i], '% rain');
      box.append(hour, temp, rain);
      strip.appendChild(box);
    }
    setText('deskWeatherNote', 'Open-Meteo · Updated ' + new Date(weatherUpdated).toLocaleTimeString('en-GB', {hour:'2-digit',minute:'2-digit'}) + ' · Refreshes every 15 minutes');
  }
  async function refreshWeather() {
    if (weatherInFlight) return weatherInFlight;
    const requested = city;
    setText('deskWeatherNote', 'Updating weather from Open-Meteo…');
    weatherInFlight = (async () => {
      try {
        const geo = await getJson('https://geocoding-api.open-meteo.com/v1/search?name=' +
          encodeURIComponent(requested) + '&count=1&language=en&format=json');
        if (!Array.isArray(geo.results) || !geo.results.length) throw Error('City not found. Try a nearby town.');
        const place = geo.results[0];
        if (!finite(place.latitude) || !finite(place.longitude)) throw Error('Location data unavailable.');
        const url = 'https://api.open-meteo.com/v1/forecast?latitude=' +
          encodeURIComponent(place.latitude) + '&longitude=' + encodeURIComponent(place.longitude) +
          '&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,precipitation' +
          '&hourly=temperature_2m,precipitation_probability&forecast_days=2&timezone=auto';
        const data = await getJson(url);
        if (!data || !data.current) throw Error('Current forecast unavailable.');
        if (city !== requested) return;
        weather = {place, data};
        weatherUpdated = Date.now();
        updateWeatherUI();
      } catch (error) {
        const message = error.name === 'AbortError' ? 'Weather request timed out.' : error.message;
        setText('deskWeatherNote', message + (weather ? ' · Showing previous forecast.' : ' · Check internet access.'));
        if (!weather) {
          setText('deskWeatherLocation', requested);
          setText('deskWeatherCondition', 'Weather unavailable');
          setText('deskWeatherSub', 'Unavailable');
        }
      } finally {
        weatherInFlight = null;
      }
    })();
    return weatherInFlight;
  }
  byId('deskWeatherForm').addEventListener('submit', event => {
    event.preventDefault();
    const updated = byId('deskCity').value.trim().replace(/\s+/g, ' ');
    if (updated.length < 2 || updated.length > 70) {
      setText('deskWeatherNote', 'Enter a city between 2 and 70 characters.');
      return;
    }
    if (city !== updated) { weather = null; weatherUpdated = 0; }
    city = updated;
    try { localStorage.setItem('desk_weather_city_v1', city); } catch {}
    if (weatherInFlight) {
      // A pending old-city request will not overwrite the new city; rerun after it finishes.
      weatherInFlight.finally(() => refreshWeather());
    } else {
      refreshWeather();
    }
  });


  function paintGlucoseGraph(readings, endTime, isSample) {
    const svg = byId('deskGlucosePlot');
    const empty = glucosePanel.querySelector('.desk-plot-empty');
    const plotter = window.DeskGlucoseChart;
    if (!plotter) {
      svg.replaceChildren();
      empty.hidden = false;
      empty.textContent = 'Graph renderer unavailable';
      return;
    }
    const chart = plotter.render(readings, {
      hours:rangeHours, endTime, scale:chartScale
    });
    // SVG markup uses numeric samples and fixed static strings only.
    svg.innerHTML = chart.svg;
    svg.setAttribute('aria-label',
      (isSample ? 'Illustrative sample ' : 'Received glucose ') + rangeHours +
      '-hour graph, target band from 4 to 7 mmol/L with local time along the bottom');
    empty.hidden = !chart.noData || isSample;
    empty.textContent = 'No readings in this period';
    setText('deskGraphStart', rangeHours + (historicalGlucose ? 'h before export' : 'h ago'));
    // The actual x-axis is drawn from reading timestamps within the SVG.
    glucoseAxis.children[0].textContent = '';
    glucoseAxis.children[1].textContent = '';
    glucoseAxis.children[2].textContent = '';
    for (const b of view.querySelectorAll('.desk-range')) {
      b.setAttribute('aria-pressed',String(Number(b.dataset.hours) === rangeHours));
    }
    const scaleButton = byId('deskChartScale');
    scaleButton.textContent = chartScale === 'auto' ? 'AUTO' : 'FULL';
    scaleButton.setAttribute('aria-label', chartScale === 'auto'
      ? 'Automatic vertical scale. Select full 0 to 40 mmol/L scale'
      : 'Full 0 to 40 mmol/L scale. Select automatic vertical scale');
    scaleButton.setAttribute('aria-pressed',String(chartScale === 'fixed'));
  }
  function drawHistoricalGraph() {
    const readings = historicalGlucose.readings;
    const end = readings[readings.length-1].timestamp;
    paintGlucoseGraph(readings, end, false);
  }
  function drawGraph() {
    if (liveConfigured && !historicalGlucose) {
      if (liveGlucose) drawLiveGraph();
      else {
        // Never show a demo line as live data, including during a failure.
        paintGlucoseGraph([], Date.now(), false);
      }
      return;
    }
    if (historicalGlucose) { drawHistoricalGraph(); return; }
    // Explicitly labelled SAMPLE chart; sample points never become live values.
    const end = Date.now();
    const samples = Array.from({length:145}, (_, i) => {
      const t = end - (144-i) * 10 * 60000;
      const mmol = 6.3 + 1.05 * Math.sin(i * 0.27) + 0.36 * Math.cos(i * 0.69);
      return {timestamp:t,mmol};
    });
    paintGlucoseGraph(samples, end, true);
  }
  view.addEventListener('click', event => {
    const rangeButton = event.target.closest('[data-hours]');
    if (rangeButton) {
      const requested = Number(rangeButton.dataset.hours);
      if ([1,3,6,12,24].includes(requested)) {
        rangeHours = requested;
        drawGraph();
      }
      return;
    }
    if (event.target.closest('#deskChartScale')) {
      chartScale = chartScale === 'auto' ? 'fixed' : 'auto';
      drawGraph();
    }
  });
  updateClock();
  setInterval(updateClock, 1000);
  setInterval(() => {
    if (!document.hidden && (currentPage === 'weather' || currentPage === 'home') &&
      weatherUpdated && Date.now() - weatherUpdated > 15 * 60 * 1000) refreshWeather();
  }, 60 * 1000);
  refreshLiveGlucose();
  setInterval(refreshLiveGlucose, 30000);
  setPage('home');
})();

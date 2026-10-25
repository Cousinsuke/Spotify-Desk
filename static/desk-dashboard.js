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
      '<div class="desk-panel-head"><div><span class="desk-kicker">GLUCOSE DASHBOARD · PROTOTYPE</span>',
      '<h2>Libre 2 Plus</h2><p class="desk-muted">No live glucose integration configured</p></div>',
      '<span class="desk-demo-badge">SAMPLE DATA</span></div>',
      '<div class="desk-glucose-info"><div><strong>--.- mmol/L</strong><p>Sensor status: not connected<br>Current glucose is unavailable.</p></div>',
      '<span class="desk-demo-badge">NOT FOR TREATMENT</span></div>',
      '<div class="desk-chart-head"><strong>Illustrative glucose graph (not your readings)</strong>',
      '<div class="desk-chart-range" role="group" aria-label="Sample chart time range">',
      '<button type="button" class="desk-range" data-hours="3">3h</button>',
      '<button type="button" class="desk-range" data-hours="6">6h</button>',
      '<button type="button" class="desk-range" data-hours="12">12h</button>',
      '</div></div>',
      '<div class="desk-plot"><svg id="deskGlucosePlot" viewBox="0 0 700 150" preserveAspectRatio="none" role="img" aria-label="Synthetic glucose values for preview only"></svg>',
      '<span class="desk-plot-watermark">SAMPLE · NOT LIVE</span></div>',
      '<div class="desk-plot-axis"><span id="deskGraphStart">12 hours ago</span><span>Example data, mmol/L</span><span>Now</span></div>',
      '<p class="desk-glucose-footer">Your official Libre app remains the source for readings, alarms and treatment decisions.</p>',
    '</section>'
  ].join('');
  surface.insertBefore(view, surface.querySelector('#pairOverlay'));

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
    if (page === 'glucose') drawGraph();
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

  function drawGraph() {
    const all = Array.from({length:49}, (_, i) =>
      6.3 + 1.05 * Math.sin(i * 0.27) + 0.36 * Math.cos(i * 0.69));
    const data = all.slice(-(rangeHours * 4 + 1));
    const xAt = i => 34 + i * 644 / (data.length - 1);
    const yAt = v => 132 - (v - 3) * 14.2;
    const points = data.map((value,i) => xAt(i).toFixed(1) + ',' + yAt(value).toFixed(1)).join(' ');
    const grid = [4,6,8,10].map(n => '<line x1="34" y1="' + yAt(n) +
      '" x2="682" y2="' + yAt(n) + '" stroke="#ffffff1a" stroke-width="1"/>' +
      '<text x="2" y="' + (yAt(n)+4) + '" font-size="11" fill="#b6c4bd">' + n + '</text>').join('');
    byId('deskGlucosePlot').innerHTML = grid +
      '<polyline fill="none" stroke="#a5f2cd" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" points="' + points + '"/>' +
      '<circle cx="' + xAt(data.length-1) + '" cy="' + yAt(data[data.length-1]) +
      '" r="4" fill="#dffcec" stroke="#18332a" stroke-width="2"/>';
    setText('deskGraphStart', rangeHours + ' hours ago');
    for (const button of view.querySelectorAll('.desk-range')) {
      button.setAttribute('aria-pressed', String(Number(button.dataset.hours) === rangeHours));
    }
  }
  view.addEventListener('click', event => {
    const button = event.target.closest('[data-hours]');
    if (!button) return;
    const requested = Number(button.dataset.hours);
    if ([3,6,12].includes(requested)) { rangeHours = requested; drawGraph(); }
  });
  updateClock();
  setInterval(updateClock, 1000);
  setInterval(() => {
    if (!document.hidden && (currentPage === 'weather' || currentPage === 'home') &&
      weatherUpdated && Date.now() - weatherUpdated > 15 * 60 * 1000) refreshWeather();
  }, 60 * 1000);
  setPage('home');
})();

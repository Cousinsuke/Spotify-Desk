/* Glucose trend chart renderer: time-based, data-driven, no storage or network.
 * Secondary visualisation only. Never extrapolate gaps or present an old value
 * as current. Configured 4-7 mmol/L band is a user display preference.
 */
(function (root, create) {
  const api = create();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.DeskGlucoseChart = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const RANGES = Object.freeze([1, 3, 6, 12, 24]);
  const TARGET_LOW = 4;
  const TARGET_HIGH = 7;
  const WIDTH = 700;
  const LEFT = 48, RIGHT = 678, TOP = 16, BOTTOM = 160;
  const GAP_MS = 20 * 60 * 1000;
  const dateClock = new Intl.DateTimeFormat('en-GB', {hour:'2-digit', minute:'2-digit', hour12:false});
  const valid = n => typeof n === 'number' && Number.isFinite(n);
  const clamp = (n,min,max) => Math.max(min,Math.min(max,n));
  const f = n => Number(n).toFixed(2);

  function seriesWindow(rows, hours, endTime) {
    if (!RANGES.includes(hours) || !valid(endTime) || !Array.isArray(rows)) return [];
    const from = endTime - hours * 3600000;
    const validRows = rows.filter(p => p && valid(p.timestamp) &&
      valid(p.mmol) && p.mmol >= 0.5 && p.mmol <= 40 &&
      p.timestamp >= from && p.timestamp <= endTime + 120000);
    const unique = new Map();
    for (const p of validRows) unique.set(p.timestamp, {timestamp:p.timestamp, mmol:p.mmol});
    return Array.from(unique.values()).sort((a,b)=>a.timestamp-b.timestamp);
  }

  function yBounds(points, scale) {
    const values = points.map(p => p.mmol);
    if (scale === 'fixed') {
      // Libre-style ticks normally run 3, 6, 9 ... 21 mmol/L. If a
      // valid extreme reading falls outside that range, extend by 3
      // rather than silently plotting it beyond the visible chart.
      const minimum = values.length ? Math.min(...values) : 3;
      const maximum = values.length ? Math.max(...values) : 21;
      return {
        low: Math.max(0, Math.min(3, Math.floor(minimum / 3) * 3)),
        high: Math.max(21, Math.ceil(maximum / 3) * 3)
      };
    }
    // Keep a predictable Libre-like auto window until actual samples need
    // more space. All bounds remain whole mmol/L units. Do not pad the
    // usual 3–12 view based on arbitrary quartiles or fluctuations.
    const minimum = values.length ? Math.min(...values) : 3;
    const maximum = values.length ? Math.max(...values) : 12;
    return {
      low: minimum < 3 ? Math.max(0, Math.floor(minimum)) : 3,
      high: maximum > 12 ? Math.ceil(maximum / 3) * 3 : 12
    };
  }

  function yAxisTicks(bounds, scale) {
    if (scale === 'fixed') {
      // The normal 3..21 extent fits every three-unit label. If an extreme
      // reading expands the extent, thin *labels* by multiples of three to
      // prevent crowding; never crop the reading or reduce the 4..7 band.
      const tickSpacing = 3 * (BOTTOM-TOP) / (bounds.high-bounds.low);
      const stride = Math.max(1, Math.ceil(20 / tickSpacing));
      const ticks = [];
      for (let value = bounds.low; value <= bounds.high; value += 3 * stride) ticks.push(value);
      if (bounds.high - ticks[ticks.length-1] >= 3 &&
          (bounds.high - ticks[ticks.length-1]) * (BOTTOM-TOP) /
            (bounds.high-bounds.low) >= 20) ticks.push(bounds.high);
      return ticks;
    }
    // Only whole-number AUTO labels. Prefer the bottom/top bounds, target
    // limits and three-unit reference values. Keep any extra integer labels
    // a readable distance apart even if an outlier expands the axis.
    const y = value => BOTTOM - (value-bounds.low)/(bounds.high-bounds.low)*(BOTTOM-TOP);
    const selected = [];
    const candidates = [bounds.low, bounds.high, TARGET_LOW, TARGET_HIGH];
    for (let v = Math.floor(bounds.high / 3) * 3; v >= bounds.low; v -= 3) {
      candidates.push(v);
    }
    for (const tick of candidates) {
      if (!Number.isInteger(tick) || tick < bounds.low || tick > bounds.high) continue;
      // SVG font size 12: 15 px vertical separation is legible, including
      // the intentionally adjacent 3 and 4 labels in the standard 3–12 view.
      if (selected.some(other => Math.abs(y(other)-y(tick)) < 15)) continue;
      if (selected.length < 6) selected.push(tick);
    }
    return selected.sort((a,b)=>a-b);
  }

  function geometry(rows, options) {
    const hours = options && options.hours;
    const endTime = options && options.endTime;
    const mode = options && options.scale === 'fixed' ? 'fixed' : 'auto';
    const points = seriesWindow(rows, hours, endTime);
    const bounds = yBounds(points, mode);
    const start = endTime - hours * 3600000;
    const x = ms => LEFT + clamp((ms-start)/(endTime-start),0,1) * (RIGHT-LEFT);
    const y = value => BOTTOM - (value-bounds.low)/(bounds.high-bounds.low)*(BOTTOM-TOP);
    const segments = [];
    let segment = [];
    for (let i=0;i<points.length;i++) {
      if (i && points[i].timestamp-points[i-1].timestamp > GAP_MS) {
        if (segment.length) segments.push(segment);
        segment = [];
      }
      segment.push({x:x(points[i].timestamp), y:y(points[i].mmol)});
    }
    if (segment.length) segments.push(segment);
    return {points,segments,bounds,start,endTime,hours,x,y};
  }

  function render(rows, options) {
    if (!options || !RANGES.includes(options.hours) || !valid(options.endTime)) {
      throw Error('Chart requires a supported range and an epoch-millisecond end time.');
    }
    const g = geometry(rows,options);
    const lineGrid = [];
    // Fixed: exact multiples of 3. Auto: spaced labels without collisions.
    const tickValues = yAxisTicks(g.bounds, options.scale);
    for (const value of tickValues) {
      const y = f(g.y(value));
      const targetEdge = value===TARGET_LOW || value===TARGET_HIGH;
      lineGrid.push('<line x1="'+LEFT+'" x2="'+RIGHT+'" y1="'+y+'" y2="'+y+
        '" stroke="'+(targetEdge?'#8ac19a66':'#ffffff23')+
        '" stroke-width="1"'+(targetEdge?' stroke-dasharray="4 5"':'')+'/>');
      lineGrid.push('<text x="'+(LEFT-10)+'" y="'+f(g.y(value)+3.5)+
        '" fill="#acbeb4" font-size="12" text-anchor="end">'+
        (options.scale === 'fixed' || value !== TARGET_LOW && value !== TARGET_HIGH
          ? String(value) : value.toFixed(1))+'</text>');
    }

    // In 3-unit FULL scale, 4 and 7 are not labelled ticks; still outline
    // the shaded target band with its own subtle boundary lines.
    const targetEdges = [TARGET_LOW, TARGET_HIGH]
      .filter(value => !tickValues.some(tick => Math.abs(tick-value)<0.01))
      .map(value => '<line x1="'+LEFT+'" x2="'+RIGHT+'" y1="'+f(g.y(value))+
        '" y2="'+f(g.y(value))+
        '" stroke="#8ac19a66" stroke-width="1" stroke-dasharray="4 5"/>')
      .join('');
    const bandTop = clamp(g.y(TARGET_HIGH),TOP,BOTTOM);
    const bandBottom = clamp(g.y(TARGET_LOW),TOP,BOTTOM);
    const band = '<rect x="'+LEFT+'" y="'+f(bandTop)+'" width="'+(RIGHT-LEFT)+
      '" height="'+f(Math.max(0,bandBottom-bandTop))+'" fill="#83be8e" fill-opacity=".13"/>';
    const nowLine = '<line x1="'+RIGHT+'" x2="'+RIGHT+'" y1="'+TOP+'" y2="'+BOTTOM+
      '" stroke="#cfdfd2" stroke-opacity=".48" stroke-dasharray="5 5" stroke-width="1"/>';
    const traces = g.segments.map(seg => seg.length>1
      ? '<polyline points="'+seg.map(p=>f(p.x)+','+f(p.y)).join(' ')+
        '" fill="none" stroke="#a9f3c5" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
      : '').join('');
    const last = g.points[g.points.length-1];
    const dot = last ? '<circle cx="'+f(g.x(last.timestamp))+'" cy="'+f(g.y(last.mmol))+
      '" r="4.8" fill="#b2facf" stroke="#143425" stroke-width="1.6"/>' : '';
    // Times are real local-clock positions, not fabricated categories.
    const labels = Array.from({length:5},(_,i)=>{
      const t=g.start+(g.endTime-g.start)*i/4;
      return {time:t, label:dateClock.format(new Date(t))};
    });
    const xTicks = labels.map((entry,i)=>{
      const px = LEFT + (RIGHT-LEFT)*i/4;
      const align = i===0?'start':i===4?'end':'middle';
      return '<text x="'+f(px)+'" y="187" fill="#9db4a8" font-size="12" text-anchor="'+
        align+'">'+entry.label+'</text>';
    }).join('');
    const svg = '<rect x="0" y="0" width="'+WIDTH+'" height="196" fill="transparent"/>'+
      band+targetEdges+lineGrid.join('')+nowLine+traces+dot+xTicks;
    return {
      svg,
      points: g.points,
      segments: g.segments,
      bounds: g.bounds,
      yTicks:tickValues,
      ticks: labels,
      latest: last || null,
      rangeLow:TARGET_LOW,
      rangeHigh:TARGET_HIGH,
      noData:g.points.length===0
    };
  }
  return {render,seriesWindow,yBounds,yAxisTicks,geometry,RANGES,TARGET_LOW,TARGET_HIGH};
});

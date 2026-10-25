/* LibreView history CSV parser: browser-only, no network or storage.
 * Exports a pure parser so its date/order/unit handling can be tested offline.
 * This is historical data only; never treat the export as a live CGM feed.
 */
(function (root, create) {
  const api = create();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.DeskGlucoseHistory = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  function csvRows(text, delimiter) {
    const rows = [];
    let row = [], field = '', quoted = false;
    for (let i = 0; i < text.length; i++) {
      const ch = text[i];
      if (ch === '"') {
        if (quoted && text[i + 1] === '"') { field += '"'; i++; }
        else if (!quoted && field === '') quoted = true;
        else if (quoted) quoted = false;
        else field += ch;
      } else if (!quoted && ch === delimiter) {
        row.push(field); field = '';
      } else if (!quoted && (ch === '\r' || ch === '\n')) {
        if (ch === '\r' && text[i + 1] === '\n') i++;
        row.push(field);
        if (row.some(value => value.trim())) rows.push(row);
        if (rows.length > 150000) throw Error('CSV has too many rows.');
        row = []; field = '';
      } else {
        field += ch;
      }
    }
    if (quoted) throw Error('CSV contains an unfinished quoted field.');
    row.push(field);
    if (row.some(value => value.trim())) rows.push(row);
    return rows;
  }
  function parseLocalTime(raw, order) {
    const match = String(raw).trim().match(/^(\d{1,4})[-/.](\d{1,2})[-/.](\d{1,4})[ T](\d{1,2}):(\d{2})(?::(\d{2}))?\s*(AM|PM)?$/i);
    if (!match) return null;
    const a = Number(match[1]), b = Number(match[2]), c = Number(match[3]);
    let year, month, day;
    if (match[1].length === 4) {
      year = a; month = b; day = c;
    } else if (match[3].length === 4) {
      year = c;
      if (order === 'DMY') { day = a; month = b; }
      else if (order === 'MDY') { month = a; day = b; }
      else return null;
    } else return null;
    let hours = Number(match[4]);
    const minutes = Number(match[5]), seconds = Number(match[6] || 0);
    const ampm = match[7] && match[7].toUpperCase();
    if (ampm) {
      if (hours < 1 || hours > 12) return null;
      hours = hours % 12 + (ampm === 'PM' ? 12 : 0);
    }
    if (year < 2000 || year > 2100 || hours > 23 || minutes > 59 || seconds > 59) return null;
    const date = new Date(year, month - 1, day, hours, minutes, seconds);
    if (date.getFullYear() !== year || date.getMonth() !== month - 1 ||
        date.getDate() !== day || date.getHours() !== hours || date.getMinutes() !== minutes) return null;
    return date.getTime();
  }
  function normalHeader(s) {
    return String(s).replace(/^\uFEFF/, '').trim().toLowerCase().replace(/\s+/g, ' ');
  }
  function parseLibreViewCsv(text, options) {
    if (typeof text !== 'string' || !text.trim()) throw Error('This CSV is empty.');
    if (text.length > 15_000_000) throw Error('CSV is too large (15 MB limit).');
    const order = options && options.dateOrder === 'MDY' ? 'MDY' : 'DMY';
    const firstRows = text.slice(0, 5000);
    const delim = ((firstRows.match(/\t/g) || []).length > (firstRows.match(/,/g) || []).length) ? '\t' : ',';
    const rows = csvRows(text.replace(/^\uFEFF/, ''), delim);
    const headerIndex = rows.findIndex(row => {
      const headers = row.map(normalHeader);
      return headers.includes('device timestamp') && headers.includes('record type') &&
        headers.some(h => /^historic glucose\b/.test(h) && /(?:mmol\/l|mg\/dl)/.test(h));
    });
    if (headerIndex < 0) throw Error('LibreView historic glucose columns not found. Export Glucose History as CSV.');
    const headers = rows[headerIndex].map(normalHeader);
    const dateIdx = headers.indexOf('device timestamp');
    const typeIdx = headers.indexOf('record type');
    const mmolIdx = headers.findIndex(h => /^historic glucose\b/.test(h) && /mmol\/l/.test(h));
    const mgIdx = headers.findIndex(h => /^historic glucose\b/.test(h) && /mg\/dl/.test(h));
    const valueIdx = mmolIdx >= 0 ? mmolIdx : mgIdx;
    const mgdl = mmolIdx < 0;
    const values = [];
    let skipped = 0;
    for (let i = headerIndex + 1; i < rows.length; i++) {
      const row = rows[i];
      if (String(row[typeIdx] || '').trim() !== '0') continue;
      const ts = parseLocalTime(row[dateIdx] || '', order);
      const raw = String(row[valueIdx] || '').trim().replace(',', '.');
      if (!/^\d{1,3}(?:\.\d{1,2})?$/.test(raw) || ts === null) { skipped++; continue; }
      const number = Number(raw);
      const mmol = mgdl ? number / 18.0182 : number;
      if (!Number.isFinite(mmol) || mmol < 0.5 || mmol > 40) { skipped++; continue; }
      values.push({timestamp:ts, mmol});
    }
    if (!values.length) throw Error('No usable historic glucose rows. Check UK/US date order and CSV format.');
    values.sort((a,b) => a.timestamp - b.timestamp);
    const unique = [];
    for (const value of values) {
      if (unique.length && unique[unique.length - 1].timestamp === value.timestamp) unique[unique.length - 1] = value;
      else unique.push(value);
    }
    return {readings: unique, skipped, dateOrder:order, convertedFromMgdl:mgdl};
  }
  function historyWindow(readings, hours) {
    if (!Array.isArray(readings) || !readings.length || ![3,6,12].includes(hours)) return [];
    const until = readings[readings.length - 1].timestamp;
    const from = until - hours * 3600000;
    return readings.filter(p => p.timestamp >= from && p.timestamp <= until);
  }
  return {parseLibreViewCsv, parseLocalTime, historyWindow};
});

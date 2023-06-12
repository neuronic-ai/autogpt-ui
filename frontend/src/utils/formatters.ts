import { parseISO, formatISO } from 'date-fns';

export const formatLargeNumber = function (val: number | null | string): string {
  if (val == null) {
    return '';
  }
  if (typeof val === 'string') {
    return parseFloat(val).toLocaleString('en-US');
  }
  return val.toLocaleString('en-US');
};

export const formatDateTime = function (dt: string | Date, toDate?: boolean) {
  if (!(dt instanceof Date)) {
    dt = parseISO(dt);
  }
  if (toDate) {
    return dt.toLocaleDateString('en-US');
  } else {
    return dt.toLocaleString('en-US', { timeZoneName: 'short' });
  }
};

export const formatDateISO = function (dt: string | Date, toDate?: boolean) {
  if (!(dt instanceof Date)) {
    dt = parseISO(dt);
  }
  if (toDate) {
    return formatISO(dt, { representation: 'date' });
  } else {
    return formatISO(dt, { representation: 'complete' });
  }
};

export const formatDateRange = function (start: string, end: string) {
  return parseISO(start).toLocaleDateString('fr-FR') + ' - ' + parseISO(end).toLocaleDateString('fr-FR');
};

export const addUSD = function (v: string | number | null) {
  if (v == null || v === '') {
    return '';
  }
  return `$${v}`;
};

export const numberToMoney = function (num: number | null) {
  if (num == null) {
    return num;
  }
  return num.toLocaleString('en-US', { minimumFractionDigits: 2 });
};

export const formatPercent = function (v: string | number | null) {
  if (v == null || v === '') {
    return '';
  }
  return `${v}%`;
};

export const addPlus = function (v: number | null) {
  if (v == null) {
    return null;
  }
  let prefix = '';
  if (v > 0) {
    prefix = '+';
  }
  return `${prefix}${v}`;
};

export const removeMinus = function (v: number | null) {
  if (v == null) {
    return null;
  }
  return Math.abs(v);
};

export const formatSeconds = function (secs: number | null) {
  if (secs == null) {
    return '';
  }

  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  const s = Math.floor((secs % 3600) % 60);

  return ('0' + h).slice(-2) + ':' + ('0' + m).slice(-2) + ':' + ('0' + s).slice(-2);
};

export const formatMarket = function (v: string) {
  switch (v) {
    case 'gdax':
      return 'coinbase';
    case 'GDAX':
      return 'COINBASE';
    default:
      return v;
  }
};

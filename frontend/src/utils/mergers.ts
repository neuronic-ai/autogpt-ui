import { isObject, isArray } from 'lodash-es';

function _mergeKeepShapeArray(dest: Array<any>, source: Array<any>) {
  if (source.length !== dest.length) {
    return dest;
  }
  const ret: any[] = [];
  dest.forEach((v, i) => {
    ret[i] = _mergeKeepShape(v, source[i]);
  });
  return ret;
}

function _mergeKeepShapeObject(dest: { [key: string]: any }, source: { [key: string]: any }) {
  const ret: { [key: string]: any } = {};
  Object.keys(dest).forEach((key) => {
    const sourceValue = source[key];
    if (typeof sourceValue !== 'undefined') {
      ret[key] = _mergeKeepShape(dest[key], sourceValue);
    } else {
      ret[key] = dest[key];
    }
  });
  return ret;
}

function _mergeKeepShape(dest: any, source: any) {
  if (isArray(dest)) {
    if (!isArray(source)) {
      return dest;
    }
    return _mergeKeepShapeArray(dest, source);
  } else if (isObject(dest)) {
    if (!isObject(source)) {
      return dest;
    }
    return _mergeKeepShapeObject(dest, source);
  } else {
    return source;
  }
}

/**
 * Immutable merge that retains the shape of the `existingValue`
 */
export const mergeKeepShape = <T>(existingValue: T, extendingValue: T): T => {
  return _mergeKeepShape(existingValue, extendingValue);
};

// Sauvegarde locale fiable : écriture double (principal + secours) et validation à la lecture.
const PREFIX = 'streetride3d:';
export function load(key, fallback) {
  for (const k of [PREFIX + key, PREFIX + key + ':bak']) {
    try { const v = localStorage.getItem(k); if (v) return { ...fallback, ...JSON.parse(v) }; } catch { /* corrompu -> secours */ }
  }
  return structuredClone(fallback);
}
export function save(key, data) {
  try {
    const s = JSON.stringify(data);
    const prev = localStorage.getItem(PREFIX + key);
    if (prev) localStorage.setItem(PREFIX + key + ':bak', prev);
    localStorage.setItem(PREFIX + key, s);
    return true;
  } catch { return false; }
}

import { writable } from 'svelte/store';

export const objects = [
  { label: 'Furniture', emoji: '🪑', desc: 'Chairs, tables and large stationary objects.', pattern: ['dash','dash'] },
  { label: 'People',    emoji: '🧍', desc: 'Pedestrians and moving persons nearby.',       pattern: ['dot','dot','dot'] },
  { label: 'Stairs',    emoji: '🪜', desc: 'Stairways and steps — take extra care.',        pattern: ['dot','dash'] },
  { label: 'Walls',     emoji: '🧱', desc: 'Solid walls and vertical barriers ahead.',      pattern: ['dash','dot','dot'] },
  { label: 'Elevation', emoji: '📐', desc: 'Curbs, ledges and ground-level drops.',         pattern: ['dot','dot','dash'] },
];

function persisted(key, fallback) {
  const initial = typeof localStorage !== 'undefined'
    ? JSON.parse(localStorage.getItem(key) ?? 'null') ?? fallback
    : fallback;
  const store = writable(initial);
  store.subscribe(val => {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(key, JSON.stringify(val));
    }
  });
  return store;
}

export const patterns = persisted(
  'blindspot_patterns',
  objects.map(o => [...o.pattern])
);

export const detectionRange = persisted('blindspot_range', 2.0);

export const connectionStatus = writable('connecting');
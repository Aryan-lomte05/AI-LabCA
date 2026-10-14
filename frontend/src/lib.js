export async function api(path, body) {
  const res = await fetch(path, body
    ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }
    : undefined);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

export const ALERTS = {
  GREEN:  { hex: '#22c55e', glow: 'rgba(34,197,94,.35)',  label: 'No action',          tag: 'Normal day' },
  YELLOW: { hex: '#facc15', glow: 'rgba(250,204,21,.35)', label: 'Be updated',          tag: 'Heat alert' },
  ORANGE: { hex: '#fb923c', glow: 'rgba(251,146,60,.4)',  label: 'Be prepared',         tag: 'Severe heat alert' },
  RED:    { hex: '#ef4444', glow: 'rgba(239,68,68,.45)',  label: 'Take action',         tag: 'Extreme heat alert' }
};

export const ROLES = [
  { id: 'citizen',   title: 'Citizen',     sub: 'Household, family, workers', icon: '◉' },
  { id: 'farmer',    title: 'Farmer',      sub: 'Crops & livestock',          icon: '❋' },
  { id: 'health',    title: 'Health dept', sub: 'Hospitals & PHCs',           icon: '✚' },
  { id: 'authority', title: 'Authority',   sub: 'Municipal / SDMA',           icon: '◆' }
];

export const REGIONS = [
  { id: 'plains',  label: 'Plains',  threshold: 40 },
  { id: 'coastal', label: 'Coastal', threshold: 37 },
  { id: 'hilly',   label: 'Hilly',   threshold: 30 }
];

export const VULNERABLE = [
  ['elderly', 'Elderly'], ['infant_child', 'Infant / child'], ['pregnant', 'Pregnant'],
  ['chronic_illness', 'Chronic illness'], ['outdoor_worker', 'Outdoor worker']
];

export const SYMPTOMS = [
  ['high_body_temp', 'Body temp > 40 °C', 'stroke'], ['no_sweating', 'Hot, dry skin', 'stroke'],
  ['confusion', 'Confusion', 'stroke'], ['unconscious', 'Unconscious', 'stroke'],
  ['seizure', 'Seizure', 'stroke'], ['heavy_sweating', 'Heavy sweating', 'exh'],
  ['dizziness', 'Dizziness', 'exh'], ['nausea', 'Nausea', 'exh'], ['weakness', 'Weakness', 'exh'],
  ['headache', 'Headache', 'exh'], ['fainting', 'Fainting', 'exh'], ['muscle_cramps', 'Muscle cramps', 'cramp']
];

export const AUDIENCE = {
  EMERGENCY:  { color: '#ef4444', label: 'Emergency' },
  'FIRST AID':{ color: '#fb7185', label: 'First aid' },
  GOVERNANCE: { color: '#a78bfa', label: 'Governance' },
  CITIZEN:    { color: '#fb923c', label: 'Citizen' },
  VULNERABLE: { color: '#f472b6', label: 'Vulnerable' },
  WORKER:     { color: '#fbbf24', label: 'Worker' },
  FARMER:     { color: '#4ade80', label: 'Farmer' },
  HEALTH:     { color: '#38bdf8', label: 'Health' },
  AUTHORITY:  { color: '#818cf8', label: 'Authority' },
  NOTE:       { color: '#94a3b8', label: 'Note' }
};

export const GROUP_COLOR = {
  Triage: '#ef4444', Validation: '#f43f5e', Derivation: '#38bdf8', Classification: '#fb923c',
  'Warm night': '#c084fc', 'Heat stress': '#f59e0b', Alert: '#ff6a00', Escalation: '#e11d48',
  Governance: '#a78bfa', Citizen: '#fdba74', Farmer: '#4ade80', Health: '#7dd3fc',
  Authority: '#818cf8', Summary: '#e5e7eb'
};

export const DEFAULT_FACTS = {
  role: 'citizen', region: 'plains', tmax: 45.6, tmax_normal: 39.8, heat_days: 3, rh: 25,
  tmin: 31, tmin_normal: 26, vulnerable: ['elderly', 'outdoor_worker'], symptoms: [], farm: 'crops'
};

export const pretty = s => String(s ?? '').replaceAll('_', ' ');

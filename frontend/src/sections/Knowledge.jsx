import { useMemo, useState } from 'react';
import SpotlightCard from '../components/reactbits/SpotlightCard';
import { GROUP_COLOR } from '../lib';
import { Chip, Eyebrow, SectionHead } from '../ui';

export default function Knowledge({ kb, firedIds }) {
  const [q, setQ] = useState('');
  const [group, setGroup] = useState('All');
  const [open, setOpen] = useState(null);
  const groups = useMemo(() => ['All', ...new Set(kb?.rules.map(r => r.group) ?? [])], [kb]);
  const rules = (kb?.rules ?? []).filter(r =>
    (group === 'All' || r.group === group) &&
    `${r.id} ${r.name} ${r.if} ${r.then} ${r.because}`.toLowerCase().includes(q.toLowerCase()));

  return (
    <section id="knowledge" className="relative mx-auto max-w-7xl scroll-mt-24 px-4 py-28 md:px-8">
      <SectionHead index="03" eyebrow="Knowledge base" title={`${kb?.rules.length ?? 59} rules.`} accent="Zero invented.">
        Each production rule carries a salience (priority) and a citation to the guideline it encodes.
        Rules that fired in your current consultation glow.
      </SectionHead>

      <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center">
        <input value={q} onChange={e => setQ(e.target.value)} placeholder="Search rules - e.g. warm night, 47, farmer…"
          className="w-full rounded-full border border-line bg-white/[.03] px-5 py-3 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-heat md:max-w-sm" />
        <div className="flex flex-wrap gap-2">
          {groups.map(g => (
            <Chip key={g} active={group === g} color={GROUP_COLOR[g] ?? '#ff6a00'} onClick={() => setGroup(g)}>{g}</Chip>
          ))}
        </div>
      </div>

      <div className="overflow-hidden rounded-3xl border border-line">
        <div className="hidden grid-cols-12 gap-4 border-b border-line bg-white/[.02] px-5 py-3 font-mono text-[10px] uppercase tracking-[0.18em] text-zinc-500 md:grid">
          <div className="col-span-1">ID</div><div className="col-span-3">Rule</div>
          <div className="col-span-5">IF</div><div className="col-span-2">THEN</div><div className="col-span-1 text-right">Sal · Src</div>
        </div>
        {rules.map(r => {
          const c = GROUP_COLOR[r.group] ?? '#aaa';
          const fired = firedIds.has(r.id);
          return (
            <div key={r.id} onClick={() => setOpen(open === r.id ? null : r.id)}
              className={`cursor-pointer border-b border-line/70 px-5 py-3.5 transition-colors last:border-0 hover:bg-white/[.03] ${fired ? 'bg-heat/[.06]' : ''}`}>
              <div className="grid gap-2 md:grid-cols-12 md:gap-4">
                <div className="col-span-1 flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full" style={{ background: fired ? '#ff6a00' : c, boxShadow: fired ? '0 0 10px #ff6a00' : 'none' }} />
                  <span className="font-mono text-sm" style={{ color: c }}>{r.id}</span>
                </div>
                <div className="col-span-3 text-sm text-white">{r.name}</div>
                <div className="col-span-5 font-mono text-[11.5px] leading-relaxed text-zinc-400">{r.if}</div>
                <div className="col-span-2 font-mono text-[11.5px] text-emerald-300/80">{r.then}</div>
                <div className="col-span-1 font-mono text-[11px] text-zinc-500 md:text-right">{r.salience} · {r.source.toUpperCase()}</div>
              </div>
              {open === r.id && (
                <div className="mt-3 rounded-xl border border-line bg-black/30 p-3 text-[13px] text-zinc-300 md:ml-[8.33%]">
                  <span className="font-serif italic text-white">Why: </span>{r.because}
                  <div className="mt-1 text-xs text-mute">{kb.sources[r.source]}</div>
                </div>
              )}
            </div>
          );
        })}
        {!rules.length && <div className="p-10 text-center text-mute">No rules match “{q}”.</div>}
      </div>

      <div id="sources" className="mt-20 grid scroll-mt-24 gap-4 md:grid-cols-3">
        {Object.entries(kb?.sources ?? {}).map(([k, v]) => (
          <SpotlightCard key={k} className="rounded-2xl border border-line bg-panel p-5" spotlightColor="rgba(255,176,32,.14)">
            <div className="font-mono text-xs text-heat">{k.toUpperCase()}</div>
            <div className="mt-2 text-[15px] text-white">{v.split(' - ')[0].split(':')[0]}</div>
            <p className="mt-2 text-xs leading-relaxed text-mute">{v.includes(':') ? v.slice(v.indexOf(':') + 1).trim() : v}</p>
          </SpotlightCard>
        ))}
      </div>
    </section>
  );
}

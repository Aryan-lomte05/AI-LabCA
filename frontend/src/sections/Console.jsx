import { useState } from 'react';
import Stepper, { Step } from '../components/reactbits/Stepper';
import SpotlightCard from '../components/reactbits/SpotlightCard';
import DecryptedText from '../components/reactbits/DecryptedText';
import AnimatedList from '../components/reactbits/AnimatedList';
import Magnet from '../components/reactbits/Magnet';
import {
  ALERTS, AUDIENCE, REGIONS, ROLES, SYMPTOMS, VULNERABLE, pretty
} from '../lib';
import { Chip, Eyebrow, NumberSlider, SectionHead, Segmented, Stat } from '../ui';

const toggle = (list = [], v) => (list.includes(v) ? list.filter(x => x !== v) : [...list, v]);

function Wizard({ facts, set, onDone }) {
  const [run, setRun] = useState(0);
  const region = REGIONS.find(r => r.id === facts.region);
  return (
    <Stepper key={run} width="100%" radius={22} accentColor="#ff6a00" transition="slide"
      nextButtonText="Next" completeButtonText="See verdict"
      onFinalStepCompleted={onDone}
      completedContent={
        <div className="py-8 text-center">
          <div className="font-serif text-3xl italic text-white">Verdict ready.</div>
          <p className="mt-2 text-sm text-mute">Results update live as you change any answer.</p>
          <button type="button" onClick={() => setRun(r => r + 1)}
            className="mt-5 rounded-full border border-white/15 px-4 py-2 text-sm hover:border-heat">
            Edit answers
          </button>
        </div>
      }>
      <Step>
        <Eyebrow className="mb-1">Step 1</Eyebrow>
        <h3 className="mb-4 text-xl text-white">Who is this advice for?</h3>
        <div className="grid grid-cols-2 gap-2.5">
          {ROLES.map(r => (
            <button key={r.id} type="button" onClick={() => set({ role: r.id })}
              className={`rounded-2xl border p-4 text-left transition-all ${
                facts.role === r.id ? 'border-heat bg-heat/10 shadow-[0_0_30px_-8px_#ff6a00]'
                  : 'border-line hover:border-white/25'}`}>
              <div className="text-xl text-heat">{r.icon}</div>
              <div className="mt-2 text-sm font-medium text-white">{r.title}</div>
              <div className="text-xs text-mute">{r.sub}</div>
            </button>
          ))}
        </div>
      </Step>

      <Step>
        <Eyebrow className="mb-1">Step 2</Eyebrow>
        <h3 className="mb-4 text-xl text-white">Weather conditions</h3>
        <div className="space-y-3">
          <Segmented value={facts.region} onChange={v => set({ region: v })}
            options={REGIONS.map(r => ({ id: r.id, label: r.label, hint: `${r.threshold}°` }))} />
          <NumberSlider label="Max temperature (Tmax)" value={facts.tmax} min={20} max={52}
            onChange={v => set({ tmax: v })}
            hint={`IMD threshold for ${region?.label.toLowerCase()}: ${region?.threshold} °C`} />
          <NumberSlider label="Normal Tmax for the date" value={facts.tmax_normal} min={15} max={46}
            optional onChange={v => set({ tmax_normal: v })} hint="Climatological normal - used for departure" />
          <div className="grid grid-cols-2 gap-3">
            <NumberSlider label="Hot days in a row" value={facts.heat_days} min={1} max={10} step={1}
              unit="d" optional onChange={v => set({ heat_days: v })} />
            <NumberSlider label="Humidity" value={facts.rh} min={0} max={100} step={1} unit="%"
              optional onChange={v => set({ rh: v })} />
          </div>
        </div>
      </Step>

      <Step>
        <Eyebrow className="mb-1">Step 3</Eyebrow>
        <h3 className="mb-4 text-xl text-white">Night & context</h3>
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <NumberSlider label="Night min (Tmin)" value={facts.tmin} min={10} max={40} optional
              onChange={v => set({ tmin: v })} />
            <NumberSlider label="Normal Tmin" value={facts.tmin_normal} min={10} max={35} optional
              onChange={v => set({ tmin_normal: v })} />
          </div>
          {facts.role === 'citizen' && (
            <div>
              <div className="mb-2 text-[13px] text-zinc-300">Household includes</div>
              <div className="flex flex-wrap gap-2">
                {VULNERABLE.map(([id, label]) => (
                  <Chip key={id} active={facts.vulnerable?.includes(id)}
                    onClick={() => set({ vulnerable: toggle(facts.vulnerable, id) })}>{label}</Chip>
                ))}
              </div>
            </div>
          )}
          {facts.role === 'farmer' && (
            <Segmented value={facts.farm} onChange={v => set({ farm: v })}
              options={[{ id: 'crops', label: 'Crops' }, { id: 'livestock', label: 'Livestock' },
                        { id: 'both', label: 'Both' }]} />
          )}
          {(facts.role === 'health' || facts.role === 'authority') && (
            <p className="text-sm text-mute">No extra context needed for {facts.role === 'health' ? 'health departments' : 'authorities'}.</p>
          )}
        </div>
      </Step>

      <Step>
        <Eyebrow className="mb-1">Step 4</Eyebrow>
        <h3 className="mb-1 text-xl text-white">Anyone unwell right now?</h3>
        <p className="mb-4 text-xs text-mute">Triage runs first - before any weather reasoning.</p>
        {facts.role === 'citizen' || facts.role === 'health' ? (
          <div className="flex flex-wrap gap-2">
            {SYMPTOMS.map(([id, label, kind]) => (
              <Chip key={id} active={facts.symptoms?.includes(id)}
                color={kind === 'stroke' ? '#ef4444' : kind === 'exh' ? '#fb923c' : '#facc15'}
                onClick={() => set({ symptoms: toggle(facts.symptoms, id) })}>{label}</Chip>
            ))}
          </div>
        ) : <p className="text-sm text-mute">Symptom triage applies to citizens and health departments.</p>}
      </Step>
    </Stepper>
  );
}

function Thermometer({ facts }) {
  const lo = 20, hi = 52;
  const pct = v => `${Math.min(100, Math.max(0, ((v - lo) / (hi - lo)) * 100))}%`;
  const thr = REGIONS.find(r => r.id === facts.region)?.threshold ?? 40;
  const t = Number(facts.tmax);
  const marks = [[thr, `${thr}° threshold`, 'below'], [45, '45° heat wave', 'above'], [47, '47° severe', 'below']]
    .filter((m, i, arr) => arr.findIndex(x => x[0] === m[0]) === i);
  return (
    <div className="mt-10">
      <div className="relative h-2 rounded-full bg-gradient-to-r from-sky-500/60 via-amber-400/70 to-red-600">
        {marks.map(([v, l, pos]) => (
          <div key={l} className="absolute -top-1 h-4 w-px bg-white/70" style={{ left: pct(v) }}>
            <span className={`absolute left-1/2 -translate-x-1/2 whitespace-nowrap font-mono text-[10px] text-mute ${
              pos === 'above' ? 'bottom-5' : 'top-5'}`}>{l}</span>
          </div>
        ))}
        {Number.isFinite(t) && (
          <div className="absolute -top-[7px] h-[22px] w-[22px] -translate-x-1/2 rounded-full border-2 border-white bg-ink shadow-[0_0_20px_#fff] transition-all duration-500"
               style={{ left: pct(t) }} />
        )}
      </div>
    </div>
  );
}

function Verdict({ result, facts }) {
  if (!result) {
    return <div className="glass flex h-80 items-center justify-center rounded-3xl text-mute">Connecting to the inference engine…</div>;
  }
  const f = result.facts;
  if (result.halted_by) {
    return (
      <SpotlightCard className="rounded-3xl border border-rose-500/40 bg-rose-950/20 p-7" spotlightColor="rgba(244,63,94,.25)">
        <Eyebrow className="!text-rose-300">Input rejected · rule {result.halted_by}</Eyebrow>
        <div className="mt-3 font-serif text-4xl italic text-white">Check the readings.</div>
        <p className="mt-3 text-rose-200/80">{f.error}</p>
        <p className="mt-4 text-sm text-mute">Validation rules halt inference instead of producing a misleading alert.</p>
      </SpotlightCard>
    );
  }
  const a = ALERTS[result.alert] ?? { hex: '#71717a', glow: 'transparent', label: '—', tag: 'Insufficient data' };
  return (
    <SpotlightCard className="relative overflow-hidden rounded-3xl border border-line bg-panel p-7"
      spotlightColor={a.glow}>
      <div className="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full blur-3xl transition-colors duration-700"
           style={{ background: a.glow }} />
      <div className="relative">
        <div className="flex items-center justify-between">
          <Eyebrow>IMD colour-coded alert</Eyebrow>
          {f.status && (
            <span className="rounded-full border border-white/15 px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-wider text-zinc-300">
              {f.status === 'watch' ? 'Watch · not yet declared' : 'Declared'}
            </span>
          )}
        </div>
        <div className="mt-4 flex flex-wrap items-end gap-x-4 gap-y-1">
          <div className="text-[clamp(3.5rem,8vw,6.5rem)] font-semibold leading-none tracking-tight" style={{ color: a.hex }}>
            <DecryptedText key={result.alert} text={result.alert ?? '—'} animateOn="view" speed={45}
              maxIterations={14} sequential revealDirection="start" characters="▓▒░█#%&@ABCDEFGHIJKLMNOPQRSTUVWXYZ" />
          </div>
          <div className="pb-3">
            <div className="text-lg text-white">{a.tag}</div>
            <div className="font-serif text-xl italic text-zinc-400">{a.label}.</div>
          </div>
        </div>
        <div className="mt-2 text-sm text-zinc-300">
          IMD category: <span className="font-medium capitalize text-white">{pretty(f.hw_category ?? 'n/a')}</span>
          {f.escalated && <span className="text-mute"> · escalated for <span className="text-white">{f.escalated}</span></span>}
          {f.needs_review && <span className="ml-2 rounded bg-violet-500/20 px-1.5 py-0.5 text-[11px] text-violet-200">needs meteorologist sign-off</span>}
        </div>
        <Thermometer facts={facts} />
        <div className="mt-12 grid grid-cols-2 gap-3 md:grid-cols-4">
          <Stat label="Departure" value={f.departure != null ? `${f.departure > 0 ? '+' : ''}${f.departure.toFixed(1)}°` : '—'}
            sub={f.departure == null ? 'normal unknown' : f.departure >= 4.5 ? 'above 4.5° criterion' : 'below criterion'} />
          <Stat label="Feels like" value={f.heat_index != null ? `${f.heat_index.toFixed(1)}°` : '—'}
            sub={pretty(f.hi_level ?? (f.heat_index == null ? 'humidity unknown' : 'comfortable'))} />
          <Stat label="Night" value={f.night ? '☾' : '—'} sub={pretty(f.night ?? 'no warm night')} />
          <Stat label="Persistence" value={facts.heat_days ? `${facts.heat_days}d` : '—'} sub="consecutive days" />
        </div>
      </div>
    </SpotlightCard>
  );
}

function Advisory({ result }) {
  const items = result?.advice ?? [];
  if (!items.length) return null;
  return (
    <div className="glass rounded-3xl p-5">
      <div className="mb-3 flex items-center justify-between px-1">
        <Eyebrow>Advisory · {items.length} actions</Eyebrow>
        <Eyebrow className="hidden !text-[10px] sm:block">hover · ↑↓ to browse</Eyebrow>
      </div>
      <AnimatedList key={JSON.stringify(items.map(i => i.rule + i.text))} items={items} width="100%" maxHeight={420}
        accentColor="#ff6a00" frame={false} animation="pop" stagger={0.04}
        renderItem={item => {
          const au = AUDIENCE[item.audience] ?? AUDIENCE.NOTE;
          return (
            <div className="flex items-start gap-3 p-3.5">
              <span className="mt-0.5 shrink-0 rounded-md px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider"
                style={{ background: `${au.color}22`, color: au.color }}>{au.label}</span>
              <span className="flex-1 text-[14px] leading-snug text-zinc-200">{item.text}</span>
              <span className="shrink-0 font-mono text-[10px] text-zinc-500">{item.rule}</span>
            </div>
          );
        }} />
    </div>
  );
}

export default function Console({ facts, set, result, scenarios, loadScenario, error }) {
  const emergency = result?.facts?.emergency;
  return (
    <section id="console" className="relative mx-auto max-w-7xl scroll-mt-24 px-4 py-28 md:px-8">
      <SectionHead index="01" eyebrow="Consultation console" title="Ask the system." accent="Watch it think.">
        Answer four short steps. Every change is sent to the forward-chaining engine and the verdict,
        advice and reasoning trace update instantly. Or load one of the documented test scenarios.
      </SectionHead>

      <div className="mb-8 flex flex-wrap gap-2.5">
        <Eyebrow className="mr-2 self-center">Presets</Eyebrow>
        {scenarios?.map(s => (
          <Magnet key={s.id} padding={30} magnetStrength={4}>
            <button type="button" onClick={() => loadScenario(s)} title={s.title}
              className="rounded-full border border-line bg-white/[.03] px-3 py-1.5 text-xs text-zinc-300 transition hover:border-heat hover:text-white">
              <span className="font-mono text-heat">{s.id}</span>{' '}
              {(t => (t.length > 24 ? `${t.slice(0, 23)}…` : t))(s.title.split(/ - |\(|,|:/)[0].trim())}
            </button>
          </Magnet>
        ))}
      </div>

      {error && <div className="mb-6 rounded-xl border border-rose-500/40 bg-rose-950/30 p-4 text-sm text-rose-200">
        Engine unreachable ({error}). Start it with <code className="font-mono">python server.py</code>.</div>}

      <div className="grid gap-6 lg:grid-cols-12">
        <div className="lg:col-span-5">
          <div className="lg:sticky lg:top-24">
            <Wizard facts={facts} set={set}
              onDone={() => document.getElementById('verdict')?.scrollIntoView({ behavior: 'smooth', block: 'start' })} />
          </div>
        </div>
        <div id="verdict" className="scroll-mt-24 space-y-6 lg:col-span-7">
          {emergency && (
            <div className="animate-pulse rounded-2xl border border-red-500/60 bg-red-600/15 p-4 text-red-100 shadow-[0_0_40px_-10px_#ef4444]">
              <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-red-300">Life-safety rule T5 fired</div>
              <div className="mt-1 text-lg font-medium">Suspected heat stroke - call 108 / 112 now.</div>
            </div>
          )}
          <Verdict result={result} facts={facts} />
          <Advisory result={result} />
        </div>
      </div>
    </section>
  );
}

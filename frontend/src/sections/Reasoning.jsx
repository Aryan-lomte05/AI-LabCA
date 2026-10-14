import { useState } from 'react';
import AnimatedList from '../components/reactbits/AnimatedList';
import SpotlightCard from '../components/reactbits/SpotlightCard';
import { GROUP_COLOR, pretty } from '../lib';
import { Eyebrow, SectionHead } from '../ui';

const STRATEGY = [
  ['Match', 'Every rule whose conditions all hold against working memory joins the agenda (conflict set).'],
  ['Resolve', 'Refraction → highest salience → most specific → earliest rule. One winner per cycle.'],
  ['Act', 'Assert or modify facts, emit advice, or HALT on invalid input. Logged to the trace.'],
  ['Repeat', 'Until the agenda is empty. Each rule fires at most once, so inference always terminates.']
];

function HowTree({ lines }) {
  return (
    <div className="space-y-1 font-mono text-[12.5px] leading-relaxed">
      {lines.map((l, i) => {
        const depth = (l.match(/^ */)[0].length) / 2;
        const [fact, rest] = l.trim().split(/  (?=<-|\()/);
        const user = rest?.includes('given by user');
        return (
          <div key={i} className="flex items-start gap-2" style={{ paddingLeft: depth * 20 }}>
            <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${user ? 'bg-zinc-500' : 'bg-heat'}`} />
            <span>
              <span className="whitespace-nowrap text-white">{fact}</span>{' '}
              <span className={user ? 'text-zinc-500' : 'text-amber-300/80'}>{rest}</span>
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default function Reasoning({ result }) {
  const [tab, setTab] = useState('alert');
  const trace = result?.trace ?? [];
  const how = result?.how ?? {};
  const active = how[tab] ? tab : Object.keys(how)[0];
  return (
    <section id="reasoning" className="relative mx-auto max-w-7xl scroll-mt-24 px-4 py-28 md:px-8">
      <SectionHead index="02" eyebrow="Explanation facility" title="No black box." accent="Every rule, on the record.">
        The engine runs the classic recognise-act cycle. Below is the live trace of the current
        consultation - which rules fired, in what order, what they matched, and which rules they beat.
      </SectionHead>

      <div className="mb-10 grid gap-px overflow-hidden rounded-2xl border border-line bg-line md:grid-cols-4">
        {STRATEGY.map(([t, d], i) => (
          <div key={t} className="bg-ink p-6">
            <div className="font-mono text-xs text-heat">0{i + 1}</div>
            <div className="mt-3 font-serif text-3xl italic text-white">{t}</div>
            <p className="mt-2 text-sm leading-relaxed text-mute">{d}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <div className="glass rounded-3xl p-5 lg:col-span-7">
          <div className="mb-3 flex items-center justify-between px-1">
            <Eyebrow>Rule-firing trace · {trace.length} cycles</Eyebrow>
            {result?.halted_by && <Eyebrow className="!text-rose-400">halted by {result.halted_by}</Eyebrow>}
          </div>
          {trace.length > 0 && (
            <AnimatedList key={trace.map(t => t.id).join()} items={trace} width="100%" maxHeight={620}
              frame={false} accentColor="#ff6a00" animation="slide" stagger={0.03}
              renderItem={t => {
                const c = GROUP_COLOR[t.group] ?? '#aaa';
                return (
                  <div className="p-4">
                    <div className="flex items-center gap-3">
                      <span className="w-6 font-mono text-[11px] text-zinc-500">{String(t.cycle).padStart(2, '0')}</span>
                      <span className="rounded-md px-2 py-0.5 font-mono text-xs font-medium" style={{ background: `${c}22`, color: c }}>{t.id}</span>
                      <span className="flex-1 text-[14px] text-white">{t.name}</span>
                      <span className="hidden font-mono text-[10px] text-zinc-500 sm:block">sal {t.salience} · {t.source.toUpperCase()}</span>
                    </div>
                    <div className="mt-2 space-y-0.5 pl-9 font-mono text-[11.5px]">
                      {t.matched.map((m, i) => <div key={i} className="text-zinc-400"><span className="text-zinc-600">IF </span>{m}</div>)}
                      {Object.entries(t.asserted).map(([k, v]) => (
                        <div key={k} className="text-emerald-300/90"><span className="text-zinc-600">THEN </span>{k} = {String(v)}</div>
                      ))}
                      <div className="pt-1 font-sans text-[12px] italic text-zinc-500">{t.because}</div>
                      {t.beaten.length > 0 && (
                        <div className="text-[10.5px] text-zinc-600">beat: {t.beaten.join(', ')}</div>
                      )}
                    </div>
                  </div>
                );
              }} />
          )}
        </div>

        <div className="space-y-6 lg:col-span-5">
          <SpotlightCard className="rounded-3xl border border-line bg-panel p-6" spotlightColor="rgba(255,106,0,.18)">
            <Eyebrow className="mb-4">HOW was this concluded?</Eyebrow>
            <div className="mb-5 flex flex-wrap gap-2">
              {Object.keys(how).map(k => (
                <button key={k} type="button" onClick={() => setTab(k)}
                  className={`rounded-full px-3 py-1 font-mono text-xs transition ${
                    active === k ? 'bg-white text-black' : 'border border-line text-zinc-400 hover:text-white'}`}>
                  {pretty(k)}
                </button>
              ))}
            </div>
            {active ? <HowTree lines={how[active]} /> : <p className="text-sm text-mute">Nothing concluded yet.</p>}
          </SpotlightCard>

          <SpotlightCard className="rounded-3xl border border-line bg-panel p-6" spotlightColor="rgba(181,23,158,.2)">
            <Eyebrow className="mb-4">Guidelines used in this run</Eyebrow>
            <div className="space-y-3">
              {Object.entries(result?.sources ?? {}).map(([k, v]) => (
                <div key={k} className="flex gap-3 text-[13px] leading-snug">
                  <span className="font-mono text-heat">{k.toUpperCase()}</span>
                  <span className="text-zinc-300">{v.split(':')[0]}</span>
                </div>
              ))}
            </div>
          </SpotlightCard>
        </div>
      </div>
    </section>
  );
}

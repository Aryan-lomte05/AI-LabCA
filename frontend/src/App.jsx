import { useEffect, useMemo, useRef, useState } from 'react';
import ClickSpark from './components/reactbits/ClickSpark';
import ShinyText from './components/reactbits/ShinyText';
import Hero from './sections/Hero';
import Console from './sections/Console';
import Reasoning from './sections/Reasoning';
import Knowledge from './sections/Knowledge';
import { ALERTS, DEFAULT_FACTS, api } from './lib';

function Nav({ result, kb, online }) {
  const a = ALERTS[result?.alert];
  return (
    <nav className="fixed inset-x-0 top-4 z-50 px-4">
      <div className="glass mx-auto flex max-w-5xl !bg-black/55 items-center justify-between rounded-full px-3 py-2 pl-5 shadow-[0_10px_40px_-15px_rgba(0,0,0,.8)]">
        <a href="#top" className="flex items-center gap-2.5">
          <span className="relative h-5 w-5 rounded-full bg-gradient-to-br from-sun via-heat to-ember shadow-[0_0_18px_#ff6a00]" />
          <span className="text-[15px] font-medium tracking-tight text-white">HeatGuard</span>
          <span className="font-serif text-[17px] italic text-zinc-400">Atlas</span>
        </a>
        <div className="hidden items-center gap-7 text-[13px] text-zinc-400 md:flex">
          {[['Console', '#console'], ['Reasoning', '#reasoning'], ['Knowledge', '#knowledge'], ['Sources', '#sources']].map(([l, h]) => (
            <a key={h} href={h} className="transition hover:text-white">{l}</a>
          ))}
        </div>
        <div className="flex items-center gap-2 rounded-full border border-line bg-black/40 px-3 py-1.5">
          <span className={`h-1.5 w-1.5 rounded-full ${online ? 'pulse-dot' : ''}`}
            style={{ background: online ? a?.hex ?? '#22c55e' : '#ef4444', color: a?.hex ?? '#22c55e' }} />
          <span className="font-mono text-[11px] text-zinc-300">
            {online ? `${result?.alert ?? 'ENGINE'} · ${kb?.rules.length ?? '–'} rules` : 'engine offline'}
          </span>
        </div>
      </div>
    </nav>
  );
}

function Footer() {
  return (
    <footer className="relative mt-10 border-t border-line">
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-16 md:grid-cols-12 md:px-8">
        <div className="md:col-span-7">
          <div className="font-serif text-5xl italic leading-none text-white md:text-7xl">Stay cool.</div>
          <ShinyText text="Stay hydrated. Check on your neighbours." speed={4} color="#71717a" shineColor="#ffb020"
            className="mt-3 text-lg" />
        </div>
        <div className="space-y-2 text-sm text-mute md:col-span-5">
          <div className="text-white">Somaiya Vidyavihar University · K. J. Somaiya School of Engineering</div>
          <div>216U50E514 Artificial Intelligence · LAB CA Component 2</div>
          <div>Use case KJS-CES-01 - Climate Intelligence for Heatwave Monitoring (IMD Mumbai-Pune)</div>
          <div className="pt-3 font-mono text-[11px] text-zinc-600">
            Advisory tool for education - in an emergency call 108 / 112 and follow official IMD / NDMA warnings.
          </div>
        </div>
      </div>
    </footer>
  );
}

export default function App() {
  const [facts, setFacts] = useState(DEFAULT_FACTS);
  const [result, setResult] = useState(null);
  const [kb, setKb] = useState(null);
  const [scenarios, setScenarios] = useState([]);
  const [error, setError] = useState(null);
  const seq = useRef(0);

  useEffect(() => {
    api('/api/kb').then(setKb).catch(e => setError(e.message));
    api('/api/scenarios').then(setScenarios).catch(() => {});
  }, []);

  // live inference: debounce, and ignore out-of-order responses
  useEffect(() => {
    const id = ++seq.current;
    const t = setTimeout(() => {
      api('/api/consult', facts)
        .then(r => { if (id === seq.current) { setResult(r); setError(null); } })
        .catch(e => setError(e.message));
    }, 120);
    return () => clearTimeout(t);
  }, [facts]);

  const set = patch => setFacts(f => ({ ...f, ...patch }));
  const loadScenario = s => {
    setFacts({ vulnerable: [], symptoms: [], farm: 'crops', tmax_normal: null, heat_days: null,
               rh: null, tmin: null, tmin_normal: null, ...s.inputs });
    document.getElementById('verdict')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };
  const firedIds = useMemo(() => new Set(result?.trace?.map(t => t.id) ?? []), [result]);

  return (
    <ClickSpark sparkColor={['#ff6a00', '#ffb020', '#ff3d3d']} sparkSize={11} sparkRadius={26} sparkCount={9} duration={480}>
      <div className="grain min-h-screen overflow-x-clip">
        <Nav result={result} kb={kb} online={!error} />
        <Hero kb={kb} scenarios={scenarios} />
        <div className="hairline mx-auto max-w-7xl" />
        <Console facts={facts} set={set} result={result} scenarios={scenarios} loadScenario={loadScenario} error={error} />
        <div className="hairline mx-auto max-w-7xl" />
        <Reasoning result={result} />
        <div className="hairline mx-auto max-w-7xl" />
        <Knowledge kb={kb} firedIds={firedIds} />
        <Footer />
      </div>
    </ClickSpark>
  );
}

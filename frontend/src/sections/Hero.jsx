import Aurora from '../components/reactbits/Aurora';
import SplitText from '../components/reactbits/SplitText';
import ShinyText from '../components/reactbits/ShinyText';
import GradientText from '../components/reactbits/GradientText';
import BlurText from '../components/reactbits/BlurText';
import CountUp from '../components/reactbits/CountUp';
import StarBorder from '../components/reactbits/StarBorder';
import { Eyebrow } from '../ui';

export default function Hero({ kb, scenarios }) {
  const stats = [
    { n: kb?.rules.length ?? 59, label: 'Production rules', sub: 'IF-THEN, salience-ranked' },
    { n: kb ? Object.keys(kb.sources).length : 9, label: 'Expert sources', sub: 'IMD · NDMA · MoHFW · NWS' },
    { n: scenarios?.length ?? 15, label: 'Test scenarios', sub: 'incl. edge & invalid cases' },
    { n: 4, label: 'Alert levels', sub: 'IMD colour code' }
  ];

  return (
    <header id="top" className="relative isolate overflow-hidden">
      <div className="absolute inset-0 -z-10 opacity-90">
        <Aurora colorStops={['#ff3d00', '#ffb020', '#b5179e']} amplitude={1.1} blend={0.55} speed={0.6} />
      </div>
      <div className="absolute inset-0 -z-10 bg-black/35 md:bg-transparent" />
      <div className="grid-bg absolute inset-0 -z-10" />
      <div className="absolute inset-x-0 bottom-0 -z-10 h-64 bg-gradient-to-b from-transparent to-ink" />

      <div className="mx-auto flex min-h-[100svh] max-w-7xl flex-col justify-center px-4 pb-16 pt-36 md:px-8">
        <div className="mb-8 inline-flex w-fit items-center gap-3 rounded-full border border-white/10 bg-black/30 px-4 py-1.5 backdrop-blur">
          <span className="pulse-dot h-1.5 w-1.5 rounded-full bg-heat text-heat" />
          <ShinyText text="SVU use case KJS-CES-01 · Phase V · Early warning" speed={3}
            color="#a1a1aa" shineColor="#ffffff" className="font-mono text-[11px] uppercase tracking-[0.2em]" />
        </div>

        <SplitText text="Read the heat" tag="h1" splitType="chars" delay={35} duration={1.1}
          textAlign="left" rootMargin="0px"
          className="text-[clamp(3.2rem,10vw,9.5rem)] font-medium leading-[0.9] tracking-[-0.045em] text-white" />
        <div className="-mt-1 font-serif text-[clamp(3.2rem,10vw,9.5rem)] italic leading-[0.95] tracking-[-0.02em]">
          <GradientText colors={['#ffb020', '#ff3d00', '#ff7ac6', '#ffb020']} animationSpeed={6}
            className="!mx-0 !justify-start">
            before it hits.
          </GradientText>
        </div>

        <div className="mt-10 grid gap-10 md:grid-cols-12 md:items-end">
          <div className="md:col-span-6">
            <BlurText delay={60} animateBy="words" direction="top"
              text="A rule-based expert system that turns a temperature reading into an IMD heat-wave verdict, a colour-coded alert, and advice tuned to who is asking - with every step of its reasoning on display."
              className="text-lg leading-relaxed text-zinc-300 md:text-xl" />
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <StarBorder as="a" href="#console" color="#ff6a00" duration={5} radius={999}
                className="!text-[15px]">
                Open the console →
              </StarBorder>
              <a href="#knowledge" className="rounded-full border border-white/15 px-5 py-3 text-[15px] text-zinc-200 transition hover:border-white/40 hover:bg-white/5">
                Explore the rules
              </a>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-white/10 bg-white/10 md:col-span-6">
            {stats.map(s => (
              <div key={s.label} className="bg-ink/80 p-5 backdrop-blur">
                <div className="font-mono text-4xl text-white md:text-5xl">
                  <CountUp to={s.n} duration={1.6} />
                </div>
                <div className="mt-2 text-sm text-zinc-200">{s.label}</div>
                <Eyebrow className="mt-1 !text-[10px]">{s.sub}</Eyebrow>
              </div>
            ))}
          </div>
        </div>
      </div>
    </header>
  );
}

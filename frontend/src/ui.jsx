// Small hand-made primitives used alongside the React Bits components.

export function Eyebrow({ children, className = '' }) {
  return (
    <div className={`font-mono text-[11px] uppercase tracking-[0.22em] text-mute ${className}`}>
      {children}
    </div>
  );
}

export function SectionHead({ index, eyebrow, title, accent, children }) {
  return (
    <div className="mb-10 grid gap-6 md:grid-cols-12 md:items-end">
      <div className="md:col-span-7">
        <Eyebrow className="mb-4">
          <span className="text-heat">{index}</span> &nbsp;/&nbsp; {eyebrow}
        </Eyebrow>
        <h2 className="text-4xl leading-[1.05] tracking-tight text-white md:text-6xl">
          {title} <span className="font-serif italic text-white/70">{accent}</span>
        </h2>
      </div>
      {children && <p className="text-sm leading-relaxed text-mute md:col-span-5">{children}</p>}
    </div>
  );
}

export function Chip({ active, onClick, children, color = '#ff6a00' }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-full border px-3.5 py-1.5 text-[13px] transition-all duration-200 hover:border-white/30"
      style={active
        ? { borderColor: color, background: `${color}22`, color: '#fff', boxShadow: `0 0 18px ${color}33` }
        : { borderColor: 'rgba(255,255,255,.1)', color: '#a1a1aa' }}
    >
      {children}
    </button>
  );
}

export function Segmented({ value, onChange, options }) {
  return (
    <div className="relative grid rounded-xl border border-line bg-white/[.03] p-1"
         style={{ gridTemplateColumns: `repeat(${options.length}, 1fr)` }}>
      {options.map(o => (
        <button key={o.id} type="button" onClick={() => onChange(o.id)}
          className={`relative z-10 rounded-lg px-3 py-2 text-sm transition-colors ${
            value === o.id ? 'bg-white text-black' : 'text-zinc-400 hover:text-white'}`}>
          {o.label}
          {o.hint && <span className={`ml-1.5 font-mono text-[10px] ${value === o.id ? 'text-black/50' : 'text-zinc-600'}`}>{o.hint}</span>}
        </button>
      ))}
    </div>
  );
}

export function NumberSlider({ label, value, onChange, min, max, step = 0.1, unit = '°C', optional, hint }) {
  const on = value !== null && value !== undefined && value !== '';
  return (
    <div className={`rounded-xl border border-line p-3.5 transition-opacity ${on ? '' : 'opacity-60'}`}>
      <div className="mb-2.5 flex items-center justify-between gap-2">
        <label className="truncate text-[13px] text-zinc-300">{label}</label>
        {optional && (
          <button type="button" onClick={() => onChange(on ? null : Math.round((min + max) / 2))}
            className="shrink-0 font-mono text-[10px] uppercase tracking-wider text-zinc-500 hover:text-heat">
            {on ? 'unknown?' : 'set value'}
          </button>
        )}
      </div>
      <div className="flex items-center gap-3">
        <input type="range" min={min} max={max} step={step} value={on ? value : min} disabled={!on}
          onChange={e => onChange(Number(e.target.value))} className="min-w-0 flex-1" />
        <div className="flex shrink-0 items-center gap-1">
          <input type="number" value={on ? value : ''} placeholder="—" step={step}
            onChange={e => onChange(e.target.value === '' ? (optional ? null : min) : Number(e.target.value))}
            className="w-16 rounded-md border border-line bg-black/40 px-2 py-1 text-right font-mono text-sm text-white outline-none focus:border-heat" />
          <span className="w-5 font-mono text-[11px] text-zinc-500">{unit}</span>
        </div>
      </div>
      {hint && <div className="mt-1.5 text-[11px] text-zinc-500">{hint}</div>}
    </div>
  );
}

export function Stat({ label, value, sub, color }) {
  return (
    <div className="rounded-xl border border-line bg-white/[.02] p-4">
      <Eyebrow className="mb-2 !text-[10px]">{label}</Eyebrow>
      <div className="font-mono text-2xl text-white" style={color ? { color } : undefined}>{value}</div>
      {sub && <div className="mt-1 text-xs capitalize text-mute">{sub}</div>}
    </div>
  );
}

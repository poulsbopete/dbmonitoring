import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { LayoutGrid, Server, Cpu, MemoryStick, Activity } from 'lucide-react';
import { HBar } from '@/components/charts/HBar';
import { Sparkline } from '@/components/charts/Sparkline';

const heatmapLegend = [
  { label: 'Critical (3)', value: 4, color: '#ef4444' },
  { label: 'Warning (2)', value: 3, color: '#eab308' },
  { label: 'Healthy (1)', value: 2, color: '#22c55e' },
  { label: 'Info (0)', value: 1, color: '#3b82f6' },
];

const severityTrend = [1, 1, 2, 1, 1, 2, 2, 1, 1, 3, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1];

const dashboards = [
  {
    icon: LayoutGrid,
    title: 'Severity grid (Spotlight-style treemap)',
    color: '#f59e0b',
    bullets: [
      'Time × grid row: each SQL instance, Windows host row, MongoDB node',
      'Lens treemap via Dashboard API: same ES|QL as a heat map (max severity 0–3 per bucket); inline heat map type not on Serverless API',
      'Companion line + bar panels for trends and peak breakdown (bars avoid legacy Lens tables on some Serverless builds)',
      'Flow & topology dashboard: connection load by host + host→DB treemap (optional OTel flow edges in generator; true Sankey = Vega)',
      'On-prem, Azure VM, Azure SQL MI, MongoDB Atlas (synthetic labels)',
    ],
  },
  {
    icon: Server,
    title: 'SQL Server overview',
    color: '#8b5cf6',
    bullets: [
      'Sessions, response time, utilisation %, performance rating',
      'CPU gauge, memory (PLE, buffer & procedure cache), processes',
      'Virtualisation overhead, error-log rate, services — OTel-friendly gauges',
    ],
  },
];

export function Slide09Spotlight() {
  return (
    <SlideLayout shadowColor="rgba(245, 158, 11, 0.45)" shadowSpeed={44} shadowScale={70}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <p className="text-[#f59e0b] text-xs font-semibold tracking-widest uppercase">Quest Spotlight · Parity story</p>
            <span className="text-white/55 text-[10px] border border-white/15 rounded-full px-2 py-0.5">
              OpenTelemetry + Kibana Lens
            </span>
          </div>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Severity grid &amp; <span className="text-white/55">SQL Overview</span>
          </h2>
          <p className="text-white/65 text-sm mt-2 max-w-3xl leading-relaxed">
            Two dashboards mirror familiar DBA tooling: a cross-platform health grid (SQL Server, Windows, MongoDB)
            and a Spotlight-style instance overview — all on OTLP metrics, no Quest agent.
          </p>
        </motion.div>

        <div className="flex gap-5 flex-1 min-h-0">
          <div className="flex flex-col gap-3 flex-1 min-h-0">
            {dashboards.map((d, i) => (
              <motion.div
                key={d.title}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.15 + i * 0.1 }}
                className="flex gap-4 p-4 rounded-xl border border-white/12 bg-white/6 flex-1 min-h-0"
              >
                <div
                  className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ background: `${d.color}18`, border: `1px solid ${d.color}40` }}
                >
                  <d.icon size={20} style={{ color: d.color }} />
                </div>
                <div className="min-w-0 flex flex-col gap-2">
                  <h3 className="text-white font-semibold text-sm">{d.title}</h3>
                  <ul className="space-y-1.5">
                    {d.bullets.map((b) => (
                      <li key={b} className="flex items-start gap-2 text-white/70 text-xs leading-snug">
                        <span style={{ color: d.color }} className="flex-shrink-0 mt-0.5">
                          →
                        </span>
                        {b}
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            ))}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.45 }}
              className="flex items-center gap-4 text-[10px] text-white/45 flex-wrap"
            >
              <span className="flex items-center gap-1.5">
                <Cpu size={12} className="text-white/40" /> sqlserver.spotlight.*
              </span>
              <span className="flex items-center gap-1.5">
                <MemoryStick size={12} className="text-white/40" /> PLE · buffer · procedure cache
              </span>
              <span className="flex items-center gap-1.5">
                <Activity size={12} className="text-white/40" /> assets/spotlight-otel-gaps.md
              </span>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, x: 14 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="flex flex-col gap-3 w-52 flex-shrink-0"
          >
            <div className="p-3 rounded-2xl border border-white/12 bg-white/6">
              <p className="text-white/55 text-[9px] uppercase tracking-widest font-semibold mb-2">
                Severity scale (0–3)
              </p>
              <HBar items={heatmapLegend} delay={0.4} />
            </div>
            <div className="p-3 rounded-2xl border border-white/12 bg-white/6 flex-1 flex flex-col gap-2">
              <p className="text-white/55 text-[9px] uppercase tracking-widest font-semibold">Example trend</p>
              <Sparkline data={severityTrend} color="#f59e0b" height={56} delay={0.55} />
              <p className="text-white/40 text-[9px] leading-snug">
                Tune Lens palette so higher severity reads hotter (red).
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </SlideLayout>
  );
}

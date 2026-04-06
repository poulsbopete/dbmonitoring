import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Layers, ShieldCheck, Globe, Users, ExternalLink, ArrowRight } from 'lucide-react';
import { Donut } from '@/components/charts/Donut';
import { CountUp } from '@/components/charts/CountUp';

/** Optional capability areas — same product surface as the demo, not a project plan. */
const demoExtensions = [
  {
    tag: 'Observe', icon: Layers, color: '#1ba9f5',
    title: 'OTLP metrics & logs',
    items: ['Receivers you saw map to real MySQL, Postgres, SQL Server, MongoDB, Oracle', 'Lens + ES|QL dashboards, including Spotlight-style views'],
  },
  {
    tag: 'Respond', icon: ShieldCheck, color: '#a855f7',
    title: 'Alerts & investigation',
    items: ['Threshold rules on the same streams', 'Workflows, cases, and AI-assisted RCA in Kibana'],
  },
  {
    tag: 'Broaden', icon: Globe, color: '#00bfa5',
    title: 'More signal',
    items: ['Additional instances, replicas, and audit or slow logs', 'SLOs on the metrics you already have'],
  },
  {
    tag: 'Operate', icon: Users, color: '#f59e0b',
    title: 'How teams use it',
    items: ['Spaces and RBAC', 'Usage and cost visibility on Serverless'],
  },
];

const outcomes = [
  { label: 'Data ingested', value: 5, suffix: '+ streams', color: '#1ba9f5' },
  { label: 'Dashboards', value: 8, suffix: '', color: '#a855f7' },
  { label: 'Alert rules', value: 6, suffix: '', color: '#00bfa5' },
  { label: 'Time to value', value: 30, suffix: ' min', color: '#f59e0b' },
];

export function Slide12NextSteps() {
  return (
    <SlideLayout shadowColor="rgba(0, 191, 165, 0.4)" shadowSpeed={42} shadowScale={72}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[#00bfa5] text-xs font-semibold tracking-widest uppercase mb-1">Same product, your data</p>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Everything you saw is a <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#1ba9f5] to-[#00bfa5]">live pattern</span> — not a one-off
          </h2>
        </motion.div>

        <div className="flex gap-5 flex-1 min-h-0">
          {/* Capability themes (illustrative — not a staged project) */}
          <div className="flex flex-col gap-2 flex-1 min-h-0">
            {demoExtensions.map((m, i) => (
              <motion.div key={m.tag} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.15 + i * 0.1 }}
                className="flex gap-3 p-4 rounded-xl border border-white/12 bg-white/6 flex-1">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{ background: `${m.color}18`, border: `1px solid ${m.color}35` }}>
                    <m.icon size={16} style={{ color: m.color }} />
                  </div>
                  {i < demoExtensions.length - 1 && (
                    <div className="w-px flex-1 bg-white/8" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded border border-white/15 text-white/55">{m.tag}</span>
                    <span className="text-white font-semibold text-sm">{m.title}</span>
                    <ArrowRight size={12} style={{ color: m.color }} className="ml-auto flex-shrink-0" />
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {m.items.map(item => (
                      <span key={item} className="text-[10px] text-white/65">{item}</span>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Right: demo snapshot */}
          <motion.div initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}
            className="flex flex-col gap-3 w-52 flex-shrink-0">
            <div className="p-4 rounded-2xl border border-white/12 bg-white/6">
              <p className="text-white/55 text-[10px] uppercase tracking-widest font-semibold mb-3">In this demo</p>
              <div className="grid grid-cols-2 gap-2">
                {outcomes.map((o, i) => (
                  <div key={o.label} className="flex flex-col gap-0.5 p-2.5 rounded-lg border border-white/10 bg-white/5">
                    <span className="text-xl font-bold" style={{ color: o.color }}>
                      <CountUp end={o.value} suffix={o.suffix} delay={0.5 + i * 0.1} duration={1.0} />
                    </span>
                    <span className="text-white/55 text-[9px]">{o.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 rounded-2xl border border-[#1ba9f5]/25 bg-[#1ba9f5]/8 flex flex-col gap-3 flex-1">
              <p className="text-[#1ba9f5] text-[10px] font-semibold uppercase tracking-widest">Surface covered</p>
              <div className="flex justify-center">
                <Donut value={100} color="#1ba9f5" size={88} label="100%" sublabel="shown" delay={0.6} thickness={10} />
              </div>
              <div className="flex flex-col gap-1">
                {['Data flowing ✓', '8 dashboards live ✓', 'Spotlight views ✓', '6 alerts + AI RCA ✓'].map(t => (
                  <div key={t} className="text-white/70 text-[10px] flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#1ba9f5]" />{t}
                  </div>
                ))}
              </div>
            </div>

            <a
              href="https://play.instruqt.com/elastic/invite/m33cztpvt73h"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-3 rounded-xl border border-[#00bfa5]/30 bg-[#00bfa5]/8 no-underline hover:bg-[#00bfa5]/14 transition-colors"
            >
              <ExternalLink size={14} className="text-[#00bfa5] flex-shrink-0" />
              <div>
                <div className="text-white text-xs font-semibold">Try it on Instruqt</div>
                <div className="text-white/55 text-[9px]">Hands-on sandbox — same stack as this demo</div>
              </div>
            </a>
          </motion.div>
        </div>
      </div>
    </SlideLayout>
  );
}

import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { AlertTriangle, DollarSign, Puzzle, Eye } from 'lucide-react';

const pains = [
  {
    icon: DollarSign,
    color: '#f04e98',
    title: 'Escalating Costs',
    body: 'Datadog DBM charges per host/month on top of APM. SQL Server and MongoDB are premium add-ons. Bills grow faster than your fleet.',
    stat: '3–5×', statLabel: 'cost vs Elastic',
  },
  {
    icon: Puzzle,
    color: '#f59e0b',
    title: 'Agent Sprawl',
    body: 'Proprietary agents per vendor, per engine. Every upgrade is a migration. Custom integrations break on new engine versions.',
    stat: '4+', statLabel: 'agents to maintain',
  },
  {
    icon: Eye,
    color: '#a855f7',
    title: 'Fragmented Visibility',
    body: 'MySQL slow queries and PostgreSQL spikes live in separate tools. Cross-DB correlation requires manual effort and war rooms.',
    stat: '0', statLabel: 'unified view',
  },
  {
    icon: AlertTriangle,
    color: '#ef4444',
    title: 'Reactive Alerting',
    body: 'Alerts fire after impact. Root cause analysis is still a manual war-room exercise. AI-powered RCA locked behind enterprise tiers.',
    stat: 'MTTR', statLabel: 'measured in hours',
  },
];

const item = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } };
const container = { hidden: {}, show: { transition: { staggerChildren: 0.1, delayChildren: 0.15 } } };

export function Slide02Problem() {
  return (
    <SlideLayout shadowColor="rgba(239, 68, 68, 0.4)" shadowSpeed={40} shadowScale={70}>
      <div className="flex flex-col h-full px-10 py-8 gap-5 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[#f04e98] text-xs font-semibold tracking-widest uppercase mb-1">The Challenge</p>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Why Your Current Stack <span className="text-white/70">Isn't Cutting It</span>
          </h2>
        </motion.div>

        <motion.div variants={container} initial="hidden" animate="show"
          className="grid grid-cols-2 gap-4 flex-1 min-h-0">
          {pains.map((p) => (
            <motion.div key={p.title} variants={item} transition={{ duration: 0.35, ease: 'easeOut' }}
              className="flex gap-4 p-5 rounded-2xl border border-white/15 bg-white/3 backdrop-blur-sm min-h-0">
              <div className="flex flex-col gap-3 flex-shrink-0">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ background: `${p.color}18`, border: `1px solid ${p.color}30` }}>
                  <p.icon size={18} style={{ color: p.color }} />
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold" style={{ color: p.color }}>{p.stat}</div>
                  <div className="text-white/85 text-[10px] leading-tight">{p.statLabel}</div>
                </div>
              </div>
              <div className="flex flex-col gap-1 min-w-0">
                <h3 className="text-base font-semibold text-white">{p.title}</h3>
                <p className="text-white/80 text-sm leading-relaxed">{p.body}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 }}
          className="flex items-center justify-center gap-6 py-2">
          {['Datadog DBM', 'Dynatrace', 'New Relic'].map(v => (
            <span key={v} className="text-white/20 text-xs line-through">{v}</span>
          ))}
          <span className="text-white/20 text-xs mx-2">→</span>
          <span className="text-[#1ba9f5] text-xs font-medium">One platform. All four databases.</span>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

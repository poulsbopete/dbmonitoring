import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { AlertTriangle, DollarSign, Puzzle, Eye } from 'lucide-react';

const pains = [
  {
    icon: DollarSign,
    color: '#f04e98',
    title: 'Escalating Costs',
    body: 'Datadog DBM charges per host per month on top of APM. SQL Server + MongoDB are premium add-ons. Bills grow faster than your database fleet.',
  },
  {
    icon: Puzzle,
    color: '#f59e0b',
    title: 'Agent Sprawl',
    body: 'Proprietary agents per vendor, per DB engine. Every upgrade is a migration project. Custom integrations break on new engine versions.',
  },
  {
    icon: Eye,
    color: '#a855f7',
    title: 'Fragmented Visibility',
    body: 'Siloed dashboards mean slow queries in MySQL and connection spikes in PostgreSQL live in different tools — correlation is manual.',
  },
  {
    icon: AlertTriangle,
    color: '#ef4444',
    title: 'Reactive, Not Intelligent',
    body: 'Alerts fire after the incident. Root cause analysis is still a manual war-room exercise. AI-powered RCA is locked behind enterprise tiers.',
  },
];

const item = { hidden: { opacity: 0, x: -20 }, show: { opacity: 1, x: 0 } };
const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12, delayChildren: 0.2 } },
};

export function Slide02Problem() {
  return (
    <SlideLayout shadowColor="rgba(239, 68, 68, 0.4)" shadowSpeed={40} shadowScale={70}>
      <div className="flex flex-col h-full px-16 py-14 gap-8">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <p className="text-[#f04e98] text-sm font-medium tracking-widest uppercase mb-2">The Challenge</p>
          <h2 className="text-5xl font-bold text-white">Why Your Current Stack
            <br />
            <span className="text-white/50">Isn't Cutting It</span>
          </h2>
        </motion.div>

        <motion.div
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-2 gap-5 flex-1"
        >
          {pains.map((p) => (
            <motion.div
              key={p.title}
              variants={item}
              transition={{ duration: 0.4, ease: 'easeOut' }}
              className="flex gap-5 p-6 rounded-2xl border border-white/8 bg-white/3 backdrop-blur-sm"
            >
              <div
                className="flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center"
                style={{ background: `${p.color}18`, border: `1px solid ${p.color}30` }}
              >
                <p.icon size={22} style={{ color: p.color }} />
              </div>
              <div className="flex flex-col gap-1">
                <h3 className="text-lg font-semibold text-white">{p.title}</h3>
                <p className="text-white/55 text-sm leading-relaxed">{p.body}</p>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </SlideLayout>
  );
}

import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Database, Zap, Shield, TrendingUp } from 'lucide-react';

const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };
const container = { hidden: {}, show: { transition: { staggerChildren: 0.13, delayChildren: 0.2 } } };

const badges = [
  { icon: Database, label: 'MySQL · PostgreSQL · SQL Server · MongoDB' },
  { icon: Zap, label: 'OpenTelemetry — no proprietary agents' },
  { icon: Shield, label: 'Serverless · Pay for what you use' },
  { icon: TrendingUp, label: 'AI-powered Root Cause Analysis' },
];

export function Slide01Title() {
  return (
    <SlideLayout shadowColor="rgba(27, 169, 245, 0.55)" shadowSpeed={55} shadowScale={85}>
      <div className="flex flex-col items-center justify-center h-full px-10 text-center gap-5 overflow-hidden">
        <motion.div variants={container} initial="hidden" animate="show" className="flex flex-col items-center gap-5">

          <motion.div variants={item}
            className="flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#1ba9f5]/40 bg-[#1ba9f5]/10 text-[#1ba9f5] text-xs font-semibold tracking-widest uppercase">
            <Database size={12} />
            Elastic Observability · Database Monitoring POC
          </motion.div>

          <motion.h1 variants={item}
            className="text-6xl md:text-7xl font-bold tracking-tight text-white leading-[1.05]">
            Database Monitoring
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#1ba9f5] via-[#a855f7] to-[#f04e98]">
              Without Compromise
            </span>
          </motion.h1>

          <motion.p variants={item} className="text-lg text-white/80 max-w-2xl leading-relaxed">
            One platform for <strong className="text-white/80">MySQL</strong>, <strong className="text-white/80">PostgreSQL</strong>,{' '}
            <strong className="text-white/80">SQL Server</strong> and <strong className="text-white/80">MongoDB</strong> —
            unified dashboards, AI root-cause analysis, and OpenTelemetry end to end.
            No proprietary agents. No per-host surprises.
          </motion.p>

          <motion.div variants={item} className="grid grid-cols-2 gap-3 mt-2 w-full max-w-2xl">
            {badges.map(b => (
              <div key={b.label}
                className="flex items-center gap-3 px-4 py-3 rounded-xl border border-white/15 bg-white/3 text-white/85 text-sm text-left">
                <b.icon size={15} className="text-[#1ba9f5] flex-shrink-0" />
                {b.label}
              </div>
            ))}
          </motion.div>

          <motion.div variants={item} className="flex items-center gap-6 text-white/80 text-xs mt-1">
            <span>vs Datadog DBM</span>
            <span className="w-1 h-1 rounded-full bg-white/20" />
            <span>vs Dynatrace</span>
            <span className="w-1 h-1 rounded-full bg-white/20" />
            <span>Proof of Concept · 2026</span>
          </motion.div>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

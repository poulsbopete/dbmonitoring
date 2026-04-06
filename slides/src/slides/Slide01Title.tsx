import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Database, Zap, Shield, TrendingUp, LayoutGrid } from 'lucide-react';
import { CountUp } from '@/components/charts/CountUp';

const stats = [
  { value: 6, suffix: ' DBs', label: 'Monitored', color: '#1ba9f5' },
  { value: 10, suffix: '', label: 'Kibana Dashboards', color: '#f59e0b' },
  { value: 100, suffix: '%', label: 'OpenTelemetry', color: '#a855f7' },
  { value: 7, suffix: ' rules', label: 'Alerts + AI RCA', color: '#00bfa5' },
];

const badges = [
  { icon: Database, label: 'MySQL · PostgreSQL · SQL Server · MongoDB · Db2 · Oracle' },
  { icon: LayoutGrid, label: 'Spotlight-style heat map + SQL Server overview' },
  { icon: Zap, label: 'OpenTelemetry OTLP — no proprietary agents' },
  { icon: Shield, label: 'Serverless · Pay only for what you use' },
  { icon: TrendingUp, label: 'AI-powered Root Cause Analysis built in' },
];

export function Slide01Title() {
  return (
    <SlideLayout shadowColor="rgba(27, 169, 245, 0.55)" shadowSpeed={55} shadowScale={85}>
      <div className="flex h-full gap-8 px-10 py-8 overflow-hidden">
        {/* Left: headline */}
        <div className="flex flex-col justify-center gap-5 flex-1 min-w-0">
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-2 px-4 py-1.5 rounded-full border border-[#1ba9f5]/40 bg-[#1ba9f5]/10 text-[#1ba9f5] text-xs font-semibold tracking-widest uppercase w-fit">
            <Database size={12} /> Elastic Observability · Live database monitoring demo
          </motion.div>

          <motion.h1 initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="text-5xl font-bold tracking-tight text-white leading-[1.05]">
            Database Monitoring
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#1ba9f5] via-[#a855f7] to-[#f04e98]">
              Without Compromise
            </span>
          </motion.h1>

          <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
            className="text-base text-white/75 max-w-lg leading-relaxed">
            One platform for <strong className="text-white">MySQL</strong>, <strong className="text-white">PostgreSQL</strong>,{' '}
            <strong className="text-white">SQL Server</strong>, <strong className="text-white">MongoDB</strong>, <strong className="text-white">IBM Db2</strong>, and <strong className="text-white">Oracle</strong> —
            unified dashboards, AI root-cause analysis, and OpenTelemetry end to end.
          </motion.p>

          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
            className="grid grid-cols-2 xl:grid-cols-3 gap-2.5">
            {badges.map(b => (
              <div key={b.label} className="flex items-center gap-2.5 px-3 py-2.5 rounded-xl border border-white/12 bg-white/6 text-white/80 text-xs">
                <b.icon size={14} className="text-[#1ba9f5] flex-shrink-0" />{b.label}
              </div>
            ))}
          </motion.div>

          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
            className="flex items-center gap-5 text-white/40 text-xs">
            <span>vs Datadog DBM</span><span className="w-1 h-1 rounded-full bg-white/20" />
            <span>vs Dynatrace</span><span className="w-1 h-1 rounded-full bg-white/20" />
            <span>Elastic · 2026</span>
          </motion.div>
        </div>

        {/* Right: animated stat tiles */}
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
          className="flex flex-col justify-center gap-3 w-52 flex-shrink-0">
          {stats.map((s, i) => (
            <motion.div key={s.label} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + i * 0.1 }}
              className="flex flex-col gap-1 p-4 rounded-2xl border border-white/12 bg-white/6">
              <div className="text-3xl font-bold" style={{ color: s.color }}>
                <CountUp end={s.value} suffix={s.suffix} delay={0.5 + i * 0.1} duration={1.2} />
              </div>
              <div className="text-white/60 text-xs">{s.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </SlideLayout>
  );
}

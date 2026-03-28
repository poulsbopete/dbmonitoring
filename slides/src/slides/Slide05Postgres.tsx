import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Users, Zap, RotateCcw, ShieldAlert } from 'lucide-react';

const metrics = [
  { icon: Users, label: 'Active Connections', value: '84', sub: 'avg across databases', color: '#3b82f6' },
  { icon: ShieldAlert, label: 'Deadlocks', value: '27', sub: 'detected in 4 days', color: '#ef4444' },
  { icon: Zap, label: 'Cache Hit Ratio', value: '98.2%', sub: 'buffer cache', color: '#00bfa5' },
  { icon: RotateCcw, label: 'Tuple Inserts', value: '1.2M', sub: 'cumulative (TO_DOUBLE cast)', color: '#3b82f6' },
];

const capabilities = [
  { text: 'Backend connection count per database — alert before max_connections is breached', em: 'postgresql.backends' },
  { text: 'Deadlock rate monitoring with trend over time using TSDB counter_long → TO_DOUBLE()', em: 'postgresql.deadlocks' },
  { text: 'Buffer cache hit ratio — know when shared_buffers need tuning', em: 'postgresql.db_size' },
  { text: 'Row activity: inserts, updates, deletes per database over time', em: 'postgresql.tup_*' },
  { text: 'Pre-wired alert: High Connection Count → AI RCA Workflow', em: 'threshold: 80 conns' },
];

export function Slide05Postgres() {
  return (
    <SlideLayout shadowColor="rgba(59, 130, 246, 0.5)" shadowSpeed={50} shadowScale={78}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <p className="text-[#3b82f6] text-xs font-semibold tracking-widest uppercase">PostgreSQL</p>
            <span className="text-white/25 text-[10px] border border-white/10 rounded-full px-2 py-0.5">TSDB · high-cardinality metrics · live data</span>
          </div>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Connection & Health <span className="text-white/40">At a Glance</span>
          </h2>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15 }}
          className="grid grid-cols-4 gap-3">
          {metrics.map((m, i) => (
            <motion.div key={m.label} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.07 }}
              className="flex flex-col gap-1 p-4 rounded-xl border border-white/8 bg-white/3">
              <m.icon size={16} style={{ color: m.color }} />
              <div className="text-2xl font-bold text-white mt-1">{m.value}</div>
              <div className="text-white/60 text-xs">{m.label}</div>
              <div className="text-white/30 text-[10px]">{m.sub}</div>
            </motion.div>
          ))}
        </motion.div>

        <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.45 }}
          className="flex flex-col gap-2.5 p-5 rounded-2xl border border-[#3b82f6]/20 bg-[#3b82f6]/5 flex-1 min-h-0">
          <h3 className="text-white/60 text-xs font-semibold uppercase tracking-widest">Dashboard panels</h3>
          {capabilities.map((c, i) => (
            <motion.div key={c.text} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + i * 0.06 }}
              className="flex items-start gap-3">
              <span className="text-[#3b82f6] text-sm mt-px flex-shrink-0">→</span>
              <span className="text-white/65 text-sm leading-snug">{c.text}
                <span className="ml-2 font-mono text-[10px] text-[#3b82f6]/60">{c.em}</span>
              </span>
            </motion.div>
          ))}
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}
          className="text-[10px] text-white/25">
          Stream: <code className="text-white/40">metrics-postgresqlreceiver.otel.otel-default</code>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

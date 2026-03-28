import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Users, Zap, RotateCcw, ShieldAlert } from 'lucide-react';

const metrics = [
  { icon: Users, label: 'Active Connections', value: '84', sub: 'avg across databases', color: '#3b82f6' },
  { icon: ShieldAlert, label: 'Deadlocks', value: '27', sub: 'detected in 4 days', color: '#ef4444' },
  { icon: Zap, label: 'Cache Hit Ratio', value: '98.2%', sub: 'buffer cache', color: '#00bfa5' },
  { icon: RotateCcw, label: 'Tuple Inserts', value: '1.2M', sub: 'cumulative', color: '#3b82f6' },
];

const capabilities = [
  'Backend connection count per database — alert before max_connections is breached',
  'Deadlock rate monitoring with trend analysis over time',
  'Buffer cache hit ratio — identify when shared_buffers need tuning',
  'Row-level activity: inserts, updates, deletes per database',
  'Replication lag (where applicable) for HA cluster health',
];

export function Slide05Postgres() {
  return (
    <SlideLayout shadowColor="rgba(59, 130, 246, 0.5)" shadowSpeed={50} shadowScale={78}>
      <div className="flex flex-col h-full px-16 py-14 gap-7">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-2">
            <p className="text-[#3b82f6] text-sm font-medium tracking-widest uppercase">PostgreSQL</p>
            <span className="text-white/20 text-xs border border-white/10 rounded-full px-2 py-0.5">TSDB — high-cardinality metrics</span>
          </div>
          <h2 className="text-5xl font-bold text-white">
            Connection & Health
            <br />
            <span className="text-white/50">At a Glance</span>
          </h2>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-4 gap-4"
        >
          {metrics.map((m, i) => (
            <motion.div
              key={m.label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.08 }}
              className="flex flex-col gap-1 p-4 rounded-xl border border-white/8 bg-white/3"
            >
              <m.icon size={18} style={{ color: m.color }} />
              <div className="text-3xl font-bold text-white mt-1">{m.value}</div>
              <div className="text-white/60 text-sm">{m.label}</div>
              <div className="text-white/30 text-xs">{m.sub}</div>
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="flex flex-col gap-3 p-6 rounded-2xl border border-[#3b82f6]/20 bg-[#3b82f6]/5 flex-1"
        >
          <h3 className="text-white/70 text-sm font-medium uppercase tracking-wide mb-1">What the Dashboard Shows</h3>
          {capabilities.map((c, i) => (
            <motion.div
              key={c}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 + i * 0.07 }}
              className="flex items-start gap-3 text-white/70 text-sm"
            >
              <span className="text-[#3b82f6] mt-0.5 flex-shrink-0">→</span>
              {c}
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-white/25 text-xs text-center"
        >
          Data source: <code className="text-white/40">metrics-postgresqlreceiver.otel.otel-default</code>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

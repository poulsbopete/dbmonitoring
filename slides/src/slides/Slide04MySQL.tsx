import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Clock, AlertCircle, TrendingUp, Table2 } from 'lucide-react';

const metrics = [
  { icon: Clock, label: 'Slow Queries', value: '4,820', sub: 'last 4 days', color: '#f59e0b' },
  { icon: AlertCircle, label: 'Error Events', value: '312', sub: 'parsed from error log', color: '#ef4444' },
  { icon: TrendingUp, label: 'Avg Query Time', value: '2.4s', sub: 'p95 = 8.1s', color: '#f59e0b' },
  { icon: Table2, label: 'Tables Monitored', value: '18', sub: 'across 6 databases', color: '#f59e0b' },
];

const capabilities = [
  'Slow query log parsing — query time, lock time, rows examined',
  'Top offending tables ranked by cumulative wait time',
  'Error log severity breakdown (Warning / Error / Fatal)',
  'Per-database query rate trend over time',
  'Full query text searchable via ES|QL in Discover',
];

export function Slide04MySQL() {
  return (
    <SlideLayout shadowColor="rgba(245, 158, 11, 0.45)" shadowSpeed={45} shadowScale={72}>
      <div className="flex flex-col h-full px-16 py-14 gap-7">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-2">
            <p className="text-[#f59e0b] text-sm font-medium tracking-widest uppercase">MySQL</p>
            <span className="text-white/20 text-xs border border-white/10 rounded-full px-2 py-0.5">LogsDB — flexible timestamps</span>
          </div>
          <h2 className="text-5xl font-bold text-white">
            Slow Query Intelligence
            <br />
            <span className="text-white/50">From the Error Log Up</span>
          </h2>
        </motion.div>

        {/* KPI row */}
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

        {/* Capabilities */}
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="flex flex-col gap-3 p-6 rounded-2xl border border-[#f59e0b]/20 bg-[#f59e0b]/5 flex-1"
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
              <span className="text-[#f59e0b] mt-0.5 flex-shrink-0">→</span>
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
          Data source: <code className="text-white/40">logs-mysql.slowlog.otel.otel-default</code> · <code className="text-white/40">logs-mysql.error.otel.otel-default</code>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

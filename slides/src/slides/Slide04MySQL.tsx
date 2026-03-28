import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Clock, AlertCircle, TrendingUp, Table2 } from 'lucide-react';

const metrics = [
  { icon: Clock, label: 'Slow Queries', value: '4,820', sub: 'last 4 days', color: '#f59e0b' },
  { icon: AlertCircle, label: 'Error Events', value: '312', sub: 'error log parsed', color: '#ef4444' },
  { icon: TrendingUp, label: 'Avg Query Time', value: '2.4s', sub: 'p95 = 8.1s', color: '#f59e0b' },
  { icon: Table2, label: 'Tables Tracked', value: '18', sub: 'across 6 databases', color: '#f59e0b' },
];

const capabilities = [
  { text: 'Slow query log parsing — query time, lock time, rows examined', em: 'mysql.slowlog.*' },
  { text: 'Top offending tables ranked by cumulative wait time', em: 'db.sql.table' },
  { text: 'Error log severity breakdown — Warning / Error / Fatal', em: 'log.level' },
  { text: 'Per-database query rate trend over time using ES|QL BUCKET()', em: 'BUCKET(@timestamp)' },
  { text: 'Full query text searchable in Discover via ES|QL', em: 'db.statement' },
];

export function Slide04MySQL() {
  return (
    <SlideLayout shadowColor="rgba(245, 158, 11, 0.45)" shadowSpeed={45} shadowScale={72}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <p className="text-[#f59e0b] text-xs font-semibold tracking-widest uppercase">MySQL</p>
            <span className="text-white/25 text-[10px] border border-white/10 rounded-full px-2 py-0.5">LogsDB · flexible timestamps · 4 days historical</span>
          </div>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Slow Query Intelligence <span className="text-white/40">From the Error Log Up</span>
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
          className="flex flex-col gap-2.5 p-5 rounded-2xl border border-[#f59e0b]/20 bg-[#f59e0b]/5 flex-1 min-h-0">
          <h3 className="text-white/60 text-xs font-semibold uppercase tracking-widest">Dashboard panels</h3>
          {capabilities.map((c, i) => (
            <motion.div key={c.text} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + i * 0.06 }}
              className="flex items-start gap-3">
              <span className="text-[#f59e0b] text-sm mt-px flex-shrink-0">→</span>
              <span className="text-white/65 text-sm leading-snug">{c.text}
                <span className="ml-2 font-mono text-[10px] text-[#f59e0b]/60">{c.em}</span>
              </span>
            </motion.div>
          ))}
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}
          className="flex gap-3 text-[10px]">
          <span className="text-white/25">Streams:</span>
          <code className="text-white/40">logs-mysql.slowlog.otel.otel-default</code>
          <span className="text-white/20">·</span>
          <code className="text-white/40">logs-mysql.error.otel.otel-default</code>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

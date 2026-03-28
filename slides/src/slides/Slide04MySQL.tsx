import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Clock, AlertCircle, TrendingUp, Table2 } from 'lucide-react';
import { Sparkline } from '@/components/charts/Sparkline';
import { HBar } from '@/components/charts/HBar';
import { CountUp } from '@/components/charts/CountUp';

const metrics = [
  { icon: Clock, label: 'Slow Queries', value: 4820, display: '4,820', color: '#f59e0b' },
  { icon: AlertCircle, label: 'Error Events', value: 312, display: '312', color: '#ef4444' },
  { icon: TrendingUp, label: 'Avg Query (s)', value: 2.4, display: '2.4s', color: '#f59e0b' },
  { icon: Table2, label: 'Tables', value: 18, display: '18', color: '#f59e0b' },
];

const slowQueryTrend = [12, 18, 14, 32, 28, 45, 22, 38, 50, 42, 60, 55, 48, 72, 65, 80, 58, 76, 90, 70];
const topTables = [
  { label: 'scheduled_jobs', value: 89, color: '#f59e0b' },
  { label: 'attribution', value: 74, color: '#f59e0b' },
  { label: 'report_cache', value: 61, color: '#f59e0b' },
  { label: 'audit_log', value: 48, color: '#f59e0b' },
  { label: 'customers', value: 35, color: '#f59e0b' },
];

const capabilities = [
  'Slow query log parsing — query time, lock time, rows examined',
  'Top offending tables by cumulative wait time',
  'Error log severity: Warning / Error / Fatal trend',
  'Per-database query rate over time with ES|QL BUCKET()',
  'Full query text searchable in Discover',
];

export function Slide04MySQL() {
  return (
    <SlideLayout shadowColor="rgba(245, 158, 11, 0.45)" shadowSpeed={45} shadowScale={72}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <p className="text-[#f59e0b] text-xs font-semibold tracking-widest uppercase">MySQL</p>
            <span className="text-white/55 text-[10px] border border-white/15 rounded-full px-2 py-0.5">LogsDB · 4 days historical</span>
          </div>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Slow Query Intelligence <span className="text-white/55">From the Error Log Up</span>
          </h2>
        </motion.div>

        <div className="flex gap-5 flex-1 min-h-0">
          {/* Left column */}
          <div className="flex flex-col gap-3 flex-1 min-h-0">
            <div className="grid grid-cols-4 gap-2">
              {metrics.map((m, i) => (
                <motion.div key={m.label} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.15 + i * 0.07 }}
                  className="flex flex-col gap-1 p-3 rounded-xl border border-white/12 bg-white/6">
                  <m.icon size={14} style={{ color: m.color }} />
                  <div className="text-xl font-bold text-white">
                    <CountUp end={m.value} suffix={m.label === 'Avg Query (s)' ? 's' : ''} decimals={m.label === 'Avg Query (s)' ? 1 : 0} delay={0.3 + i * 0.07} />
                  </div>
                  <div className="text-white/60 text-[10px]">{m.label}</div>
                </motion.div>
              ))}
            </div>

            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.45 }}
              className="flex flex-col gap-2 p-4 rounded-xl border border-[#f59e0b]/20 bg-[#f59e0b]/5 flex-1 min-h-0">
              <h3 className="text-white/60 text-[10px] font-semibold uppercase tracking-widest">Dashboard panels</h3>
              {capabilities.map((c, i) => (
                <motion.div key={c} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + i * 0.06 }}
                  className="flex items-start gap-2 text-white/75 text-xs leading-snug">
                  <span className="text-[#f59e0b] flex-shrink-0">→</span>{c}
                </motion.div>
              ))}
            </motion.div>
          </div>

          {/* Right: infographics */}
          <motion.div initial={{ opacity: 0, x: 14 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35 }}
            className="flex flex-col gap-3 w-48 flex-shrink-0">
            <div className="p-3 rounded-2xl border border-white/12 bg-white/6 flex flex-col gap-2">
              <p className="text-white/55 text-[9px] uppercase tracking-widest font-semibold">Slow Query Rate</p>
              <Sparkline data={slowQueryTrend} color="#f59e0b" height={56} delay={0.5} />
              <p className="text-white/40 text-[9px] text-center">Last 4 days →</p>
            </div>
            <div className="p-3 rounded-2xl border border-white/12 bg-white/6 flex flex-col gap-2 flex-1">
              <p className="text-white/55 text-[9px] uppercase tracking-widest font-semibold">Top Tables by Slow Queries</p>
              <HBar items={topTables} delay={0.6} />
            </div>
          </motion.div>
        </div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}
          className="flex gap-3 text-[9px]">
          <span className="text-white/40">Streams:</span>
          <code className="text-white/55">logs-mysql.slowlog.otel.otel-default</code>
          <span className="text-white/30">·</span>
          <code className="text-white/55">logs-mysql.error.otel.otel-default</code>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

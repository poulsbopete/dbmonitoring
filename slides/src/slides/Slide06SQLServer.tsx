import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Activity, Lock, BarChart2, Timer } from 'lucide-react';
import { Sparkline } from '@/components/charts/Sparkline';
import { HBar } from '@/components/charts/HBar';
import { CountUp } from '@/components/charts/CountUp';

const metrics = [
  { icon: Activity, label: 'Batch Req/s', value: 2840, color: '#8b5cf6' },
  { icon: Lock, label: 'Lock Waits', value: 143, color: '#ef4444' },
  { icon: BarChart2, label: 'Transactions/s', value: 1420, color: '#8b5cf6' },
  { icon: Timer, label: 'Avg Compile (ms)', value: 12.4, color: '#a855f7' },
];

const batchTrend = [1200, 1500, 1800, 2100, 2400, 2800, 2600, 2900, 2700, 3100, 2840, 2950, 2750, 3000, 2840, 2900, 2800, 3100, 2950, 2840];
const lockBreakdown = [
  { label: 'Table lock', value: 55, color: '#8b5cf6' },
  { label: 'Row lock', value: 42, color: '#a855f7' },
  { label: 'Page lock', value: 28, color: '#6d28d9' },
  { label: 'Key lock', value: 18, color: '#7c3aed' },
];

const capabilities = [
  'Batch requests over time — spot spikes before they escalate',
  'SQL compilations vs re-compilations (plan cache efficiency)',
  'Lock waits: table, row, page and key broken out by type',
  'Transactions per second with commit/rollback breakdown',
  'Spotlight-style dashboards: health heat map + SQL overview (sessions, CPU, PLE, processes)',
  'Pre-wired alert: High Transaction Rate → AI RCA Workflow',
];

export function Slide06SQLServer() {
  return (
    <SlideLayout shadowColor="rgba(139, 92, 246, 0.5)" shadowSpeed={48} shadowScale={74}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <p className="text-[#8b5cf6] text-xs font-semibold tracking-widest uppercase">Microsoft SQL Server</p>
            <span className="text-white/55 text-[10px] border border-white/15 rounded-full px-2 py-0.5">TSDB · counter_long fields via TO_DOUBLE()</span>
          </div>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Batch Throughput & <span className="text-white/55">Lock Intelligence</span>
          </h2>
        </motion.div>

        <div className="flex gap-5 flex-1 min-h-0">
          <div className="flex flex-col gap-3 flex-1 min-h-0">
            <div className="grid grid-cols-4 gap-2">
              {metrics.map((m, i) => (
                <motion.div key={m.label} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.15 + i * 0.07 }}
                  className="flex flex-col gap-1 p-3 rounded-xl border border-white/12 bg-white/6">
                  <m.icon size={14} style={{ color: m.color }} />
                  <div className="text-xl font-bold text-white">
                    <CountUp end={m.value} decimals={m.value % 1 !== 0 ? 1 : 0} delay={0.3 + i * 0.07} />
                  </div>
                  <div className="text-white/60 text-[10px]">{m.label}</div>
                </motion.div>
              ))}
            </div>

            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.45 }}
              className="flex flex-col gap-2 p-4 rounded-xl border border-[#8b5cf6]/20 bg-[#8b5cf6]/5 flex-1 min-h-0">
              <h3 className="text-white/60 text-[10px] font-semibold uppercase tracking-widest">Dashboard panels</h3>
              {capabilities.map((c, i) => (
                <motion.div key={c} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + i * 0.06 }}
                  className="flex items-start gap-2 text-white/75 text-xs leading-snug">
                  <span className="text-[#8b5cf6] flex-shrink-0">→</span>{c}
                </motion.div>
              ))}
            </motion.div>
          </div>

          <motion.div initial={{ opacity: 0, x: 14 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35 }}
            className="flex flex-col gap-3 w-48 flex-shrink-0">
            <div className="p-3 rounded-2xl border border-white/12 bg-white/6 flex flex-col gap-2">
              <p className="text-white/55 text-[9px] uppercase tracking-widest font-semibold">Batch Requests/s</p>
              <Sparkline data={batchTrend} color="#8b5cf6" height={56} delay={0.5} />
            </div>
            <div className="p-3 rounded-2xl border border-white/12 bg-white/6 flex flex-col gap-2 flex-1">
              <p className="text-white/55 text-[9px] uppercase tracking-widest font-semibold">Lock Wait Breakdown</p>
              <HBar items={lockBreakdown} delay={0.6} />
            </div>
          </motion.div>
        </div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}
          className="text-[9px] text-white/40">
          Stream: <code className="text-white/55">metrics-sqlserverreceiver.otel.otel-default</code>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

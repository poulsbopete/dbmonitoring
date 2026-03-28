import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Layers, Lock, Activity, ArrowLeftRight } from 'lucide-react';

const metrics = [
  { icon: Activity, label: 'Batch Requests/s', value: '1,840', sub: 'peak observed', color: '#8b5cf6' },
  { icon: Layers, label: 'Active Transactions', value: '142', sub: 'avg concurrent', color: '#8b5cf6' },
  { icon: Lock, label: 'Lock Waits', value: '89', sub: 'over 4 days', color: '#ef4444' },
  { icon: ArrowLeftRight, label: 'I/O Stall (ms)', value: '18.4', sub: 'avg data file', color: '#f59e0b' },
];

const capabilities = [
  { text: 'Batch SQL request rate — the primary throughput signal for SQL Server', em: 'sqlserver.batch_sql_request.count' },
  { text: 'Active transaction count with alert at 100 concurrent (pre-wired)', em: 'sqlserver.transaction.active.count' },
  { text: 'Lock wait frequency and avg wait time — catch blocking before users do', em: 'sqlserver.lock.wait_time.avg' },
  { text: 'I/O read vs write latency by database — identify storage bottlenecks', em: 'sqlserver.database.io.*' },
  { text: 'Buffer cache hit % — SQL Server memory pressure at a glance', em: 'sqlserver.page.buffer_cache.hit_ratio' },
];

export function Slide06SQLServer() {
  return (
    <SlideLayout shadowColor="rgba(139, 92, 246, 0.5)" shadowSpeed={48} shadowScale={75}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <p className="text-[#8b5cf6] text-xs font-semibold tracking-widest uppercase">Microsoft SQL Server</p>
            <span className="text-white/25 text-[10px] border border-[#8b5cf6]/30 rounded-full px-2 py-0.5 text-[#8b5cf6]/60">No premium add-on required · included in Elastic</span>
          </div>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Throughput, Locks & <span className="text-white/40">I/O at Full Fidelity</span>
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
          className="flex flex-col gap-2.5 p-5 rounded-2xl border border-[#8b5cf6]/20 bg-[#8b5cf6]/5 flex-1 min-h-0">
          <h3 className="text-white/60 text-xs font-semibold uppercase tracking-widest">Dashboard panels</h3>
          {capabilities.map((c, i) => (
            <motion.div key={c.text} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + i * 0.06 }}
              className="flex items-start gap-3">
              <span className="text-[#8b5cf6] text-sm mt-px flex-shrink-0">→</span>
              <span className="text-white/65 text-sm leading-snug">{c.text}
                <span className="ml-2 font-mono text-[10px] text-[#8b5cf6]/60">{c.em}</span>
              </span>
            </motion.div>
          ))}
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}
          className="text-[10px] text-white/25">
          Stream: <code className="text-white/40">metrics-sqlserverreceiver.otel.otel-default</code>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

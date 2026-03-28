import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Layers, Lock, Activity, ArrowLeftRight } from 'lucide-react';

const metrics = [
  { icon: Activity, label: 'Batch Requests/s', value: '1,840', sub: 'peak observed', color: '#8b5cf6' },
  { icon: Layers, label: 'Active Transactions', value: '142', sub: 'avg concurrent', color: '#8b5cf6' },
  { icon: Lock, label: 'Lock Waits', value: '89', sub: 'over 4 days', color: '#ef4444' },
  { icon: ArrowLeftRight, label: 'I/O Stalls (ms)', value: '18.4', sub: 'avg data file', color: '#f59e0b' },
];

const capabilities = [
  'Batch SQL request rate — the primary throughput signal for SQL Server',
  'Active transaction count with alert rule pre-wired at 100 concurrent',
  'Lock wait frequency — detect blocking queries before users complain',
  'Database page I/O stall — identify storage bottlenecks per database',
  'No SQL Server agent required — standard OpenTelemetry OTLP receiver',
];

export function Slide06SQLServer() {
  return (
    <SlideLayout shadowColor="rgba(139, 92, 246, 0.5)" shadowSpeed={48} shadowScale={75}>
      <div className="flex flex-col h-full px-16 py-14 gap-7">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-2">
            <p className="text-[#8b5cf6] text-sm font-medium tracking-widest uppercase">Microsoft SQL Server</p>
            <span className="text-white/20 text-xs border border-white/10 rounded-full px-2 py-0.5">No premium add-on required</span>
          </div>
          <h2 className="text-5xl font-bold text-white">
            Throughput, Locks &
            <br />
            <span className="text-white/50">I/O at Full Fidelity</span>
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
          className="flex flex-col gap-3 p-6 rounded-2xl border border-[#8b5cf6]/20 bg-[#8b5cf6]/5 flex-1"
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
              <span className="text-[#8b5cf6] mt-0.5 flex-shrink-0">→</span>
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
          Data source: <code className="text-white/40">metrics-sqlserverreceiver.otel.otel-default</code>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

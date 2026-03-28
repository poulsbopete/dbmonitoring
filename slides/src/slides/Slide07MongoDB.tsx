import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Cpu, HardDrive, GitBranch, Zap } from 'lucide-react';

const metrics = [
  { icon: Zap, label: 'Operations/s', value: '3,240', sub: 'reads + writes + cmds', color: '#00bfa5' },
  { icon: HardDrive, label: 'Memory Usage', value: '4.2 GB', sub: 'resident (virtual: 11 GB)', color: '#00bfa5' },
  { icon: GitBranch, label: 'Connections', value: '156', sub: 'current client conns', color: '#3b82f6' },
  { icon: Cpu, label: 'Document Ops', value: '890K', sub: 'inserts + updates + deletes', color: '#00bfa5' },
];

const capabilities = [
  'Operation rate by type (query, insert, update, delete, command) over time',
  'Memory usage in GB — resident and virtual, human-readable',
  'Active connection count with trend — catch connection pool exhaustion early',
  'Document-level operation counts with cumulative rate analysis',
  'Replication lag tracking for replica set health',
];

export function Slide07MongoDB() {
  return (
    <SlideLayout shadowColor="rgba(0, 191, 165, 0.45)" shadowSpeed={52} shadowScale={73}>
      <div className="flex flex-col h-full px-16 py-14 gap-7">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-2">
            <p className="text-[#00bfa5] text-sm font-medium tracking-widest uppercase">MongoDB</p>
            <span className="text-white/20 text-xs border border-white/10 rounded-full px-2 py-0.5">First-class support — no premium tier</span>
          </div>
          <h2 className="text-5xl font-bold text-white">
            Operations, Memory &
            <br />
            <span className="text-white/50">Connection Health</span>
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
          className="flex flex-col gap-3 p-6 rounded-2xl border border-[#00bfa5]/20 bg-[#00bfa5]/5 flex-1"
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
              <span className="text-[#00bfa5] mt-0.5 flex-shrink-0">→</span>
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
          Data source: <code className="text-white/40">metrics-mongodbatlas.otel.otel-default</code>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

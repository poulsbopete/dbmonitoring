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
  { text: 'Operation rate by type (query, insert, update, delete, command) over time', em: 'mongodb.operation.count' },
  { text: 'Memory in GB — resident and virtual, human-readable (bytes ÷ 1073741824)', em: 'mongodb.memory.usage' },
  { text: 'Active connection count with trend — catch pool exhaustion early', em: 'mongodb.connection.count' },
  { text: 'Document-level operation counts with cumulative rate using TO_DOUBLE()', em: 'mongodb.document.operation.count' },
  { text: 'Replication lag tracking for replica set health monitoring', em: 'mongodb.replication.lag' },
];

export function Slide07MongoDB() {
  return (
    <SlideLayout shadowColor="rgba(0, 191, 165, 0.45)" shadowSpeed={52} shadowScale={73}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <p className="text-[#00bfa5] text-xs font-semibold tracking-widest uppercase">MongoDB</p>
            <span className="text-white/25 text-[10px] border border-[#00bfa5]/30 rounded-full px-2 py-0.5 text-[#00bfa5]/60">First-class support · no premium tier · included</span>
          </div>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Operations, Memory & <span className="text-white/40">Connection Health</span>
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
          className="flex flex-col gap-2.5 p-5 rounded-2xl border border-[#00bfa5]/20 bg-[#00bfa5]/5 flex-1 min-h-0">
          <h3 className="text-white/60 text-xs font-semibold uppercase tracking-widest">Dashboard panels</h3>
          {capabilities.map((c, i) => (
            <motion.div key={c.text} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + i * 0.06 }}
              className="flex items-start gap-3">
              <span className="text-[#00bfa5] text-sm mt-px flex-shrink-0">→</span>
              <span className="text-white/65 text-sm leading-snug">{c.text}
                <span className="ml-2 font-mono text-[10px] text-[#00bfa5]/60">{c.em}</span>
              </span>
            </motion.div>
          ))}
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}
          className="text-[10px] text-white/25">
          Stream: <code className="text-white/40">metrics-mongodbatlas.otel.otel-default</code>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

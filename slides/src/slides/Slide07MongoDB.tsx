import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Layers, HardDrive, Zap, Network } from 'lucide-react';
import { Sparkline } from '@/components/charts/Sparkline';
import { Donut } from '@/components/charts/Donut';
import { CountUp } from '@/components/charts/CountUp';

const metrics = [
  { icon: Zap, label: 'Ops/s', value: 3420, color: '#00bfa5' },
  { icon: HardDrive, label: 'Memory (GB)', value: 1.24, color: '#00bfa5' },
  { icon: Network, label: 'Connections', value: 62, color: '#00bfa5' },
  { icon: Layers, label: 'Collections', value: 14, color: '#00bfa5' },
];

const opsTrend = [1800, 2200, 2600, 2900, 3100, 2700, 3200, 3400, 3100, 3500, 3420, 3300, 3600, 3200, 3420, 3500, 3300, 3600, 3420, 3500];
const capabilities = [
  'Operation rate by type: insert, query, update, delete, command',
  'Memory usage in GB (resident + virtual)',
  'Network bytes in/out — egress cost awareness',
  'Connection count vs max configured pool size',
  'Pre-wired alert: High Op Rate → AI RCA Workflow',
];

export function Slide07MongoDB() {
  return (
    <SlideLayout shadowColor="rgba(0, 191, 165, 0.45)" shadowSpeed={52} shadowScale={76}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <p className="text-[#00bfa5] text-xs font-semibold tracking-widest uppercase">MongoDB</p>
            <span className="text-white/55 text-[10px] border border-white/15 rounded-full px-2 py-0.5">TSDB · memory in GB · live ops</span>
          </div>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Operations, Memory <span className="text-white/55">& Connections</span>
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
                    <CountUp end={m.value} decimals={m.value % 1 !== 0 ? 2 : 0} delay={0.3 + i * 0.07} />
                  </div>
                  <div className="text-white/60 text-[10px]">{m.label}</div>
                </motion.div>
              ))}
            </div>

            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.45 }}
              className="flex flex-col gap-2 p-4 rounded-xl border border-[#00bfa5]/20 bg-[#00bfa5]/5 flex-1 min-h-0">
              <h3 className="text-white/60 text-[10px] font-semibold uppercase tracking-widest">Dashboard panels</h3>
              {capabilities.map((c, i) => (
                <motion.div key={c} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + i * 0.06 }}
                  className="flex items-start gap-2 text-white/75 text-xs leading-snug">
                  <span className="text-[#00bfa5] flex-shrink-0">→</span>{c}
                </motion.div>
              ))}
            </motion.div>
          </div>

          <motion.div initial={{ opacity: 0, x: 14 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35 }}
            className="flex flex-col gap-3 w-48 flex-shrink-0">
            <div className="p-3 rounded-2xl border border-white/12 bg-white/6 flex flex-col gap-2">
              <p className="text-white/55 text-[9px] uppercase tracking-widest font-semibold">Operations/s</p>
              <Sparkline data={opsTrend} color="#00bfa5" height={52} delay={0.5} />
            </div>
            <div className="p-3 rounded-2xl border border-white/12 bg-white/6 flex flex-col gap-3 flex-1 items-center justify-around">
              <p className="text-white/55 text-[9px] uppercase tracking-widest font-semibold self-start">Connection Pool</p>
              <Donut value={62} color="#00bfa5" size={80} label="62%" sublabel="of max" delay={0.6} thickness={10} />
              <div className="flex gap-3 text-[9px] text-white/50">
                <span>62 active</span><span>/</span><span>100 max</span>
              </div>
            </div>
          </motion.div>
        </div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}
          className="text-[9px] text-white/40">
          Stream: <code className="text-white/55">metrics-mongodbatlas.otel.otel-default</code>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

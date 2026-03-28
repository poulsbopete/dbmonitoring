import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Check, X, Minus } from 'lucide-react';

const rows = [
  { feature: 'MySQL slow query analysis', elastic: true, datadog: true, dynatrace: false },
  { feature: 'PostgreSQL deep metrics', elastic: true, datadog: true, dynatrace: 'partial' },
  { feature: 'SQL Server (no premium add-on)', elastic: true, datadog: false, dynatrace: 'partial' },
  { feature: 'MongoDB first-class support', elastic: true, datadog: false, dynatrace: false },
  { feature: 'OpenTelemetry native ingestion', elastic: true, datadog: 'partial', dynatrace: 'partial' },
  { feature: 'Custom ES|QL dashboards', elastic: true, datadog: false, dynatrace: false },
  { feature: 'AI-powered root cause analysis', elastic: true, datadog: 'partial', dynatrace: 'partial' },
  { feature: 'Unified logs + metrics + APM', elastic: true, datadog: true, dynatrace: true },
  { feature: 'Predictable serverless pricing', elastic: true, datadog: false, dynatrace: false },
  { feature: 'No proprietary agents required', elastic: true, datadog: false, dynatrace: false },
];

type CellValue = boolean | 'partial' | string;

function Cell({ value, color }: { value: CellValue; color: string }) {
  if (value === true) return <Check size={18} style={{ color }} className="mx-auto" />;
  if (value === 'partial') return <Minus size={18} className="mx-auto text-yellow-400/70" />;
  return <X size={18} className="mx-auto text-red-400/60" />;
}

export function Slide08Comparison() {
  return (
    <SlideLayout shadowColor="rgba(168, 85, 247, 0.4)" shadowSpeed={40} shadowScale={68}>
      <div className="flex flex-col h-full px-16 py-14 gap-7">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[#a855f7] text-sm font-medium tracking-widest uppercase mb-2">Competitive Analysis</p>
          <h2 className="text-5xl font-bold text-white">
            Elastic vs Datadog vs Dynatrace
          </h2>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.25 }}
          className="flex-1 rounded-2xl overflow-hidden border border-white/8 bg-white/2"
        >
          {/* Header */}
          <div className="grid grid-cols-[1fr_140px_140px_140px] border-b border-white/8 bg-white/4">
            <div className="px-5 py-3 text-white/50 text-xs uppercase tracking-wide">Feature</div>
            <div className="px-5 py-3 text-center text-[#1ba9f5] font-semibold text-sm">Elastic</div>
            <div className="px-5 py-3 text-center text-white/50 text-sm">Datadog DBM</div>
            <div className="px-5 py-3 text-center text-white/50 text-sm">Dynatrace</div>
          </div>

          {/* Rows */}
          {rows.map((row, i) => (
            <motion.div
              key={row.feature}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.35 + i * 0.05 }}
              className="grid grid-cols-[1fr_140px_140px_140px] border-b border-white/5 last:border-0 hover:bg-white/3 transition-colors"
            >
              <div className="px-5 py-3 text-white/75 text-sm">{row.feature}</div>
              <div className="px-5 py-3 flex items-center justify-center">
                <Cell value={row.elastic} color="#1ba9f5" />
              </div>
              <div className="px-5 py-3 flex items-center justify-center">
                <Cell value={row.datadog} color="#1ba9f5" />
              </div>
              <div className="px-5 py-3 flex items-center justify-center">
                <Cell value={row.dynatrace} color="#1ba9f5" />
              </div>
            </motion.div>
          ))}
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-center text-white/25 text-xs"
        >
          <Minus size={12} className="inline mr-1 text-yellow-400/70" />Partial = available but limited or requires premium tier ·
          Data as of Q1 2026
        </motion.p>
      </div>
    </SlideLayout>
  );
}

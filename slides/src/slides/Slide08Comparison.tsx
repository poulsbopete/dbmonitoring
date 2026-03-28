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
  if (value === true) return <Check size={15} style={{ color }} className="mx-auto" />;
  if (value === 'partial') return <Minus size={15} className="mx-auto text-yellow-400/70" />;
  return <X size={15} className="mx-auto text-red-400/50" />;
}

export function Slide08Comparison() {
  return (
    <SlideLayout shadowColor="rgba(168, 85, 247, 0.4)" shadowSpeed={40} shadowScale={68}>
      <div className="flex flex-col h-full px-10 py-8 gap-5 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[#a855f7] text-xs font-semibold tracking-widest uppercase mb-1">Competitive Analysis</p>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Elastic vs Datadog vs Dynatrace
          </h2>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
          className="flex-1 min-h-0 rounded-2xl overflow-hidden border border-white/15 bg-white/2 flex flex-col">
          {/* Header */}
          <div className="grid grid-cols-[1fr_120px_120px_120px] border-b border-white/15 bg-white/4 flex-shrink-0">
            <div className="px-4 py-2.5 text-white/70 text-[10px] uppercase tracking-widest">Feature</div>
            <div className="px-4 py-2.5 text-center text-[#1ba9f5] font-semibold text-sm">Elastic</div>
            <div className="px-4 py-2.5 text-center text-white/70 text-sm">Datadog</div>
            <div className="px-4 py-2.5 text-center text-white/70 text-sm">Dynatrace</div>
          </div>
          {/* Rows */}
          <div className="flex-1 overflow-hidden flex flex-col">
            {rows.map((row, i) => (
              <motion.div key={row.feature}
                initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.28 + i * 0.04 }}
                className="grid grid-cols-[1fr_120px_120px_120px] border-b border-white/12 last:border-0 hover:bg-white/3 transition-colors flex-1">
                <div className="px-4 flex items-center text-white/70 text-sm">{row.feature}</div>
                <div className="px-4 flex items-center justify-center"><Cell value={row.elastic} color="#1ba9f5" /></div>
                <div className="px-4 flex items-center justify-center"><Cell value={row.datadog} color="#1ba9f5" /></div>
                <div className="px-4 flex items-center justify-center"><Cell value={row.dynatrace} color="#1ba9f5" /></div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}
          className="text-center text-white/20 text-[10px]">
          <Minus size={10} className="inline mr-1 text-yellow-400/60" />Partial = limited or requires premium tier · Q1 2026
        </motion.p>
      </div>
    </SlideLayout>
  );
}

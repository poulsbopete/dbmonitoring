import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Check, X, Minus } from 'lucide-react';

const features = [
  { label: 'MySQL Slow Query Log', elastic: 'full', dd: 'full', dt: 'full' },
  { label: 'PostgreSQL Metrics', elastic: 'full', dd: 'full', dt: 'full' },
  { label: 'SQL Server Metrics', elastic: 'full', dd: 'addon', dt: 'full' },
  { label: 'MongoDB Metrics', elastic: 'full', dd: 'addon', dt: 'addon' },
  { label: 'IBM Db2 Metrics', elastic: 'full', dd: 'addon', dt: 'addon' },
  { label: 'Oracle Database', elastic: 'full', dd: 'addon', dt: 'addon' },
  { label: 'Spotlight-style heat map & SQL overview', elastic: 'full', dd: 'partial', dt: 'partial' },
  { label: 'OpenTelemetry Native', elastic: 'full', dd: 'partial', dt: 'none' },
  { label: 'No Proprietary Agents', elastic: 'full', dd: 'none', dt: 'none' },
  { label: 'AI Root Cause Analysis', elastic: 'full', dd: 'partial', dt: 'partial' },
  { label: 'Serverless / Per-Use Pricing', elastic: 'full', dd: 'none', dt: 'none' },
  { label: 'ES|QL Query Engine', elastic: 'full', dd: 'none', dt: 'none' },
  { label: 'TSDB Compression', elastic: 'full', dd: 'none', dt: 'none' },
];

type Level = 'full' | 'partial' | 'addon' | 'none';

function Cell({ level }: { level: Level }) {
  if (level === 'full') return <Check size={14} className="text-emerald-400 mx-auto" />;
  if (level === 'partial') return <Minus size={14} className="text-yellow-400 mx-auto" />;
  if (level === 'addon') return <span className="text-yellow-400/80 text-[10px] block text-center">Add-on $</span>;
  return <X size={13} className="text-red-400/70 mx-auto" />;
}

// Score bars
const vendors = [
  { name: 'Elastic', score: 10, color: '#1ba9f5' },
  { name: 'Datadog', score: 6.5, color: '#632CA6' },
  { name: 'Dynatrace', score: 6, color: '#1496ff' },
];

export function Slide10Comparison() {
  return (
    <SlideLayout shadowColor="rgba(27, 169, 245, 0.4)" shadowSpeed={40} shadowScale={68}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[#1ba9f5] text-xs font-semibold tracking-widest uppercase mb-1">Feature Matrix</p>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Elastic vs Datadog vs Dynatrace
          </h2>
        </motion.div>

        <div className="flex gap-5 flex-1 min-h-0">
          {/* Table */}
          <motion.div initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
            className="flex-1 min-h-0 overflow-hidden">
            <div className="h-full overflow-auto rounded-xl border border-white/12 bg-white/5">
              <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="border-b border-white/12 bg-white/5">
                    <th className="text-left px-4 py-2.5 text-white/60 font-semibold w-1/2">Capability</th>
                    {['Elastic', 'Datadog', 'Dynatrace'].map(h => (
                      <th key={h} className="px-3 py-2.5 text-center font-semibold text-white/80">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {features.map((f, i) => (
                    <motion.tr key={f.label} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.25 + i * 0.05 }}
                      className="border-b border-white/7 hover:bg-white/4 transition-colors">
                      <td className="px-4 py-2 text-white/75">{f.label}</td>
                      <td className="px-3 py-2"><Cell level={f.elastic as Level} /></td>
                      <td className="px-3 py-2"><Cell level={f.dd as Level} /></td>
                      <td className="px-3 py-2"><Cell level={f.dt as Level} /></td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>

          {/* Score visualization */}
          <motion.div initial={{ opacity: 0, x: 14 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35 }}
            className="flex flex-col gap-4 w-48 flex-shrink-0 justify-between py-1">
            <div>
              <p className="text-white/55 text-[10px] uppercase tracking-widest font-semibold mb-3">Coverage Score</p>
              {vendors.map((v, i) => (
                <div key={v.name} className="mb-3">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-white/75 text-xs">{v.name}</span>
                    <span className="text-xs font-bold" style={{ color: v.color }}>{v.score}/10</span>
                  </div>
                  <div className="h-2.5 bg-white/6 rounded-full overflow-hidden">
                    <motion.div className="h-full rounded-full" style={{ background: v.color }}
                      initial={{ width: 0 }} animate={{ width: `${v.score * 10}%` }}
                      transition={{ delay: 0.5 + i * 0.1, duration: 0.8, ease: 'easeOut' }} />
                  </div>
                </div>
              ))}
            </div>

            <div className="p-3 rounded-xl border border-white/12 bg-white/6">
              <p className="text-white/55 text-[10px] uppercase tracking-widest font-semibold mb-2">Legend</p>
              {[
                { icon: <Check size={12} className="text-emerald-400" />, label: 'Included' },
                { icon: <Minus size={12} className="text-yellow-400" />, label: 'Partial' },
                { icon: <span className="text-yellow-400/80 text-[9px]">$</span>, label: 'Paid add-on' },
                { icon: <X size={11} className="text-red-400/70" />, label: 'Not available' },
              ].map(l => (
                <div key={l.label} className="flex items-center gap-2 mb-1">
                  <div className="w-5 flex-shrink-0 flex justify-center">{l.icon}</div>
                  <span className="text-white/60 text-[10px]">{l.label}</span>
                </div>
              ))}
            </div>

            <div className="p-3 rounded-xl border border-[#1ba9f5]/25 bg-[#1ba9f5]/8">
              <p className="text-[#1ba9f5] text-xs font-semibold">Elastic wins on:</p>
              <p className="text-white/65 text-[10px] leading-relaxed mt-1">OTel-native · Db2 + Oracle included · Spotlight-style views · AI RCA · serverless · ES|QL</p>
            </div>
          </motion.div>
        </div>
      </div>
    </SlideLayout>
  );
}

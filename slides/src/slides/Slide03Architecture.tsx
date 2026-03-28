import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { ArrowRight, Database, Activity, BarChart3, Bot } from 'lucide-react';

const sources = [
  { label: 'MySQL', color: '#f59e0b', sub: 'Slow queries · Error logs', stream: 'LogsDB' },
  { label: 'PostgreSQL', color: '#3b82f6', sub: 'Connections · Deadlocks · Cache hit', stream: 'TSDB' },
  { label: 'SQL Server', color: '#8b5cf6', sub: 'Batch requests · Transactions · Locks', stream: 'TSDB' },
  { label: 'MongoDB', color: '#00bfa5', sub: 'Operations · Memory · Replication', stream: 'TSDB' },
];

export function Slide03Architecture() {
  return (
    <SlideLayout shadowColor="rgba(59, 130, 246, 0.5)" shadowSpeed={50} shadowScale={75}>
      <div className="flex flex-col h-full px-10 py-8 gap-5 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[#1ba9f5] text-xs font-semibold tracking-widest uppercase mb-1">How It Works</p>
          <h2 className="text-4xl font-bold text-white leading-tight">
            One Pipeline, <span className="text-white/40">Four Databases</span>
          </h2>
        </motion.div>

        <div className="flex-1 min-h-0 flex items-center">
          <div className="flex items-stretch gap-3 w-full">

            {/* Sources */}
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
              className="flex flex-col gap-2 flex-1">
              <p className="text-white/30 text-xs uppercase tracking-widest mb-1">Data Sources</p>
              {sources.map((s, i) => (
                <motion.div key={s.label} initial={{ opacity: 0, x: -15 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + i * 0.08 }}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl border border-white/8 bg-white/3">
                  <Database size={16} style={{ color: s.color }} />
                  <div className="flex-1 min-w-0">
                    <div className="text-white font-semibold text-sm">{s.label}</div>
                    <div className="text-white/40 text-xs truncate">{s.sub}</div>
                  </div>
                  <span className="text-[10px] border rounded-full px-2 py-0.5 flex-shrink-0"
                    style={{ color: s.color, borderColor: `${s.color}40` }}>{s.stream}</span>
                </motion.div>
              ))}
            </motion.div>

            {/* Arrow + OTLP */}
            <motion.div initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.55 }}
              className="flex flex-col items-center justify-center gap-2 px-2">
              <ArrowRight className="text-white/20" size={18} />
              <div className="flex flex-col items-center gap-1 px-4 py-5 rounded-2xl border border-[#1ba9f5]/30 bg-[#1ba9f5]/8 text-center">
                <Activity size={20} className="text-[#1ba9f5]" />
                <span className="text-[#1ba9f5] font-bold text-sm mt-1">OpenTelemetry</span>
                <span className="text-white/40 text-xs">OTLP/HTTP</span>
                <span className="text-white/30 text-[10px] mt-1">No agents</span>
                <span className="text-white/30 text-[10px]">Open standard</span>
              </div>
              <ArrowRight className="text-white/20" size={18} />
            </motion.div>

            {/* Elastic */}
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.65 }}
              className="flex flex-col gap-2 flex-1">
              <p className="text-white/30 text-xs uppercase tracking-widest mb-1">Elastic Observability Serverless</p>
              <div className="flex-1 p-4 rounded-xl border border-[#1ba9f5]/20 bg-[#1ba9f5]/5 flex flex-col gap-2">
                <div className="flex items-center gap-2 pb-2 border-b border-white/8">
                  <BarChart3 size={16} className="text-[#1ba9f5]" />
                  <span className="text-white font-semibold text-sm">4 Kibana Dashboards</span>
                </div>
                {[
                  ['logs-mysql.*', '#f59e0b', 'Slow queries + errors (historical)'],
                  ['metrics-postgresql.*', '#3b82f6', 'DB health metrics (live)'],
                  ['metrics-sqlserver.*', '#8b5cf6', 'Batch & transaction metrics (live)'],
                  ['metrics-mongodb.*', '#00bfa5', 'Ops, memory, connections (live)'],
                ].map(([idx, color, label]) => (
                  <div key={idx} className="flex items-start gap-2">
                    <div className="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0" style={{ background: color as string }} />
                    <div>
                      <div className="text-white/60 font-mono text-[10px]">{idx}</div>
                      <div className="text-white/35 text-[10px]">{label}</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="p-3 rounded-xl border border-[#a855f7]/20 bg-[#a855f7]/5 flex items-center gap-2">
                <Bot size={15} className="text-[#a855f7]" />
                <div>
                  <div className="text-white text-xs font-semibold">AI RCA Workflow</div>
                  <div className="text-white/40 text-[10px]">Alert → investigate → create case</div>
                </div>
              </div>
              <div className="flex gap-2">
                {['Alert Rules', 'Cases', 'SLOs'].map(t => (
                  <div key={t} className="flex-1 text-center text-[10px] text-white/40 border border-white/8 rounded-lg py-1.5">{t}</div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>

        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1 }}
          className="text-center text-white/25 text-xs">
          Python OTLP generator seeds 4 days of MySQL logs + live metrics for all 4 engines before the demo begins
        </motion.p>
      </div>
    </SlideLayout>
  );
}

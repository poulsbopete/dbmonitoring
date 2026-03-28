import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { ArrowRight, Database, Activity, BarChart3 } from 'lucide-react';

const sources = [
  { label: 'MySQL', color: '#f59e0b', sub: 'Slow queries · Error logs' },
  { label: 'PostgreSQL', color: '#3b82f6', sub: 'Connections · Deadlocks · Cache' },
  { label: 'SQL Server', color: '#8b5cf6', sub: 'Batch requests · Transactions' },
  { label: 'MongoDB', color: '#00bfa5', sub: 'Operations · Memory · Replication' },
];

export function Slide03Architecture() {
  return (
    <SlideLayout shadowColor="rgba(59, 130, 246, 0.5)" shadowSpeed={50} shadowScale={75}>
      <div className="flex flex-col h-full px-16 py-14 gap-8">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[#1ba9f5] text-sm font-medium tracking-widest uppercase mb-2">How It Works</p>
          <h2 className="text-5xl font-bold text-white">
            One Pipeline,
            <br />
            <span className="text-white/50">Four Databases</span>
          </h2>
        </motion.div>

        {/* Architecture flow */}
        <div className="flex-1 flex items-center justify-center">
          <div className="flex items-center gap-4 w-full max-w-5xl">
            {/* Source DBs */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="flex flex-col gap-3 flex-1"
            >
              {sources.map((s, i) => (
                <motion.div
                  key={s.label}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + i * 0.1 }}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl border border-white/10 bg-white/4"
                >
                  <Database size={18} style={{ color: s.color }} />
                  <div>
                    <div className="text-white font-semibold text-sm">{s.label}</div>
                    <div className="text-white/40 text-xs">{s.sub}</div>
                  </div>
                </motion.div>
              ))}
            </motion.div>

            {/* Arrow + OTLP */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.6 }}
              className="flex flex-col items-center gap-2"
            >
              <ArrowRight className="text-white/30" size={24} />
              <div className="flex flex-col items-center gap-1 px-5 py-4 rounded-2xl border border-[#1ba9f5]/30 bg-[#1ba9f5]/8 text-center">
                <Activity size={22} className="text-[#1ba9f5]" />
                <span className="text-[#1ba9f5] font-bold text-sm">OpenTelemetry</span>
                <span className="text-white/40 text-xs">OTLP HTTP</span>
                <span className="text-white/40 text-xs">No agents</span>
              </div>
              <ArrowRight className="text-white/30" size={24} />
            </motion.div>

            {/* Elastic */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 }}
              className="flex flex-col gap-3 flex-1"
            >
              <div className="px-5 py-5 rounded-2xl border border-[#1ba9f5]/25 bg-[#1ba9f5]/6">
                <div className="flex items-center gap-2 mb-3">
                  <BarChart3 size={18} className="text-[#1ba9f5]" />
                  <span className="text-white font-bold">Elastic Observability</span>
                  <span className="ml-auto text-xs text-[#1ba9f5] border border-[#1ba9f5]/30 rounded-full px-2 py-0.5">Serverless</span>
                </div>
                <div className="flex flex-col gap-2 text-sm">
                  {[
                    ['logs-mysql.*', 'Slow queries + errors'],
                    ['metrics-postgresql.*', 'DB health metrics (TSDB)'],
                    ['metrics-sqlserver.*', 'Batch & transaction metrics'],
                    ['metrics-mongodb.*', 'Ops, memory, connections'],
                  ].map(([idx, label]) => (
                    <div key={idx} className="flex items-center gap-2">
                      <span className="text-white/40 font-mono text-xs">{idx}</span>
                      <span className="text-white/30 text-xs">→ {label}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex gap-2">
                {['Kibana Dashboards', 'Alert Rules', 'AI RCA Workflow'].map((t) => (
                  <div key={t} className="flex-1 text-center text-xs text-white/50 border border-white/10 rounded-lg py-2 px-1">
                    {t}
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="text-center text-white/30 text-sm"
        >
          Python OTLP generator produces 4 days of synthetic telemetry in minutes, seeding all streams before the demo begins
        </motion.p>
      </div>
    </SlideLayout>
  );
}

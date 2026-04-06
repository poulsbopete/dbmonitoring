import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Database, Activity, BarChart3, Bot, ArrowRight } from 'lucide-react';

const sources = [
  { label: 'MySQL', color: '#f59e0b', sub: 'Slow queries · Error logs', stream: 'LogsDB' },
  { label: 'PostgreSQL', color: '#3b82f6', sub: 'Connections · Deadlocks', stream: 'TSDB' },
  { label: 'SQL Server', color: '#8b5cf6', sub: 'Batch requests · Locks', stream: 'TSDB' },
  { label: 'MongoDB', color: '#00bfa5', sub: 'Operations · Memory', stream: 'TSDB' },
  { label: 'Oracle', color: '#f97316', sub: 'Sessions · Tablespaces · Parses', stream: 'TSDB' },
];

// Animated pulsing dot moving along a path
function FlowDot({ color, delay }: { color: string; delay: number }) {
  return (
    <motion.div
      className="w-2 h-2 rounded-full absolute"
      style={{ background: color, top: '50%', translateY: '-50%' }}
      initial={{ left: '0%', opacity: 0 }}
      animate={{ left: ['0%', '100%'], opacity: [0, 1, 1, 0] }}
      transition={{ delay, duration: 1.8, repeat: Infinity, repeatDelay: 1.5, ease: 'easeInOut' }}
    />
  );
}

export function Slide03Architecture() {
  return (
    <SlideLayout shadowColor="rgba(59, 130, 246, 0.5)" shadowSpeed={50} shadowScale={75}>
      <div className="flex flex-col h-full px-10 py-8 gap-5 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[#1ba9f5] text-xs font-semibold tracking-widest uppercase mb-1">How It Works</p>
          <h2 className="text-4xl font-bold text-white leading-tight">
            One Pipeline, <span className="text-white/55">Five Databases</span>
          </h2>
        </motion.div>

        <div className="flex-1 min-h-0 flex items-center">
          <div className="flex items-stretch gap-3 w-full">

            {/* Sources */}
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15 }}
              className="flex flex-col gap-2 flex-1">
              <p className="text-white/55 text-[10px] uppercase tracking-widest mb-1">Data Sources</p>
              {sources.map((s, i) => (
                <motion.div key={s.label} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + i * 0.08 }}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl border border-white/12 bg-white/6">
                  <Database size={15} style={{ color: s.color }} />
                  <div className="flex-1 min-w-0">
                    <div className="text-white font-semibold text-sm">{s.label}</div>
                    <div className="text-white/60 text-xs">{s.sub}</div>
                  </div>
                  <span className="text-[10px] border rounded-full px-2 py-0.5 flex-shrink-0"
                    style={{ color: s.color, borderColor: `${s.color}40` }}>{s.stream}</span>
                </motion.div>
              ))}
            </motion.div>

            {/* Animated flow arrows */}
            <div className="flex flex-col justify-center items-center gap-3 w-24 flex-shrink-0">
              {sources.map((s, i) => (
                <div key={s.label} className="relative w-full h-5 flex items-center">
                  <div className="w-full h-px bg-white/10 relative overflow-hidden">
                    <FlowDot color={s.color} delay={0.6 + i * 0.4} />
                  </div>
                  <ArrowRight size={12} className="text-white/30 flex-shrink-0 ml-1" />
                </div>
              ))}
              <div className="text-center mt-1">
                <div className="flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl border border-[#1ba9f5]/35 bg-[#1ba9f5]/10">
                  <Activity size={14} className="text-[#1ba9f5]" />
                  <span className="text-[#1ba9f5] font-semibold text-xs">OTel</span>
                </div>
                <div className="text-white/40 text-[9px] mt-1">OTLP/HTTP</div>
              </div>
            </div>

            {/* Elastic */}
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 }}
              className="flex flex-col gap-2 flex-1">
              <p className="text-white/55 text-[10px] uppercase tracking-widest mb-1">Elastic Observability Serverless</p>
              <div className="flex-1 p-4 rounded-xl border border-[#1ba9f5]/25 bg-[#1ba9f5]/6 flex flex-col gap-2">
                <div className="flex items-center gap-2 pb-2 border-b border-white/10">
                  <BarChart3 size={15} className="text-[#1ba9f5]" />
                  <span className="text-white font-semibold text-sm">8 Kibana dashboards</span>
                </div>
                {[
                  { stream: 'logs-mysql.*', color: '#f59e0b', label: 'Slow queries + errors' },
                  { stream: 'metrics-postgresql.*', color: '#3b82f6', label: 'DB health metrics' },
                  { stream: 'metrics-sqlserver.*', color: '#8b5cf6', label: 'Batch & transactions' },
                  { stream: 'metrics-mongodb.*', color: '#00bfa5', label: 'Ops, memory, conns' },
                  { stream: 'metrics-oracledb.*', color: '#f97316', label: 'Sessions, tablespaces' },
                ].map(({ stream, color, label }) => (
                  <div key={stream} className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: color }} />
                    <div className="min-w-0">
                      <div className="text-white/70 font-mono text-[10px] truncate">{stream}</div>
                      <div className="text-white/45 text-[9px]">{label}</div>
                    </div>
                  </div>
                ))}
                <div className="flex items-center gap-2 pt-1 border-t border-white/8">
                  <div className="w-2 h-2 rounded-full flex-shrink-0 bg-[#f59e0b]" />
                  <div className="min-w-0">
                    <div className="text-white/70 font-mono text-[10px] truncate">Spotlight — heat map + SQL overview</div>
                    <div className="text-white/45 text-[9px]">SQL · Windows · Mongo · Azure / Atlas</div>
                  </div>
                </div>
              </div>
              <div className="p-3 rounded-xl border border-[#a855f7]/25 bg-[#a855f7]/6 flex items-center gap-2">
                <Bot size={14} className="text-[#a855f7]" />
                <div>
                  <div className="text-white text-xs font-semibold">AI RCA Workflow</div>
                  <div className="text-white/55 text-[10px]">Alert → investigate → case</div>
                </div>
              </div>
              <div className="flex gap-1.5">
                {['6 Alert Rules', 'Cases', 'SLOs'].map(t => (
                  <div key={t} className="flex-1 text-center text-[9px] text-white/55 border border-white/12 rounded-lg py-1.5">{t}</div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </SlideLayout>
  );
}

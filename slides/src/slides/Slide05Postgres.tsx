import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { DashboardScreenshot } from '@/components/DashboardScreenshot';
import { Users, Zap, RotateCcw, ShieldAlert } from 'lucide-react';
import { CountUp } from '@/components/charts/CountUp';

const metrics = [
  { icon: Users, label: 'Connections', value: 84, color: '#3b82f6' },
  { icon: ShieldAlert, label: 'Deadlocks', value: 27, color: '#ef4444' },
  { icon: Zap, label: 'Cache Hit %', value: 98.2, color: '#00bfa5' },
  { icon: RotateCcw, label: 'Tuple Inserts (M)', value: 1.2, color: '#3b82f6' },
];

const capabilities = [
  'Backend connections per DB — alert before max_connections breach',
  'Deadlock rate trend over time (counter_long → TO_DOUBLE cast)',
  'Buffer cache hit ratio — when shared_buffers need tuning',
  'Row-level activity: inserts, updates, deletes over time',
  'Pre-wired alert: High Connection Count → AI RCA Workflow',
];

export function Slide05Postgres() {
  return (
    <SlideLayout shadowColor="rgba(59, 130, 246, 0.5)" shadowSpeed={50} shadowScale={78}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <p className="text-[#3b82f6] text-xs font-semibold tracking-widest uppercase">PostgreSQL</p>
            <span className="text-white/55 text-[10px] border border-white/15 rounded-full px-2 py-0.5">TSDB · live metrics · alert threshold: 80 conns</span>
          </div>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Connection & Health <span className="text-white/55">At a Glance</span>
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
                    <CountUp end={m.value} decimals={m.value % 1 !== 0 ? 1 : 0} suffix={m.label === 'Tuple Inserts (M)' ? 'M' : ''} delay={0.3 + i * 0.07} />
                  </div>
                  <div className="text-white/60 text-[10px]">{m.label}</div>
                </motion.div>
              ))}
            </div>

            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.45 }}
              className="flex flex-col gap-2 p-4 rounded-xl border border-[#3b82f6]/20 bg-[#3b82f6]/5 flex-1 min-h-0">
              <h3 className="text-white/60 text-[10px] font-semibold uppercase tracking-widest">Dashboard panels</h3>
              {capabilities.map((c, i) => (
                <motion.div key={c} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + i * 0.06 }}
                  className="flex items-start gap-2 text-white/75 text-xs leading-snug">
                  <span className="text-[#3b82f6] flex-shrink-0">→</span>{c}
                </motion.div>
              ))}
            </motion.div>
          </div>

          <DashboardScreenshot
            src="dashboards/postgresql.png"
            alt="Kibana dashboard: PostgreSQL performance and health with AI recommendations"
            caption="Live dashboard · Elastic Observability Serverless"
          />
        </div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}
          className="text-[9px] text-white/40">
          Stream: <code className="text-white/55">metrics-postgresqlreceiver.otel.otel-default</code>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

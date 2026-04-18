import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { DashboardScreenshot } from '@/components/DashboardScreenshot';
import { Activity, Database, HardDrive, Timer } from 'lucide-react';
import { CountUp } from '@/components/charts/CountUp';

const metrics = [
  { icon: Activity, label: 'Active connections', value: 285, color: '#4589ff', decimals: 0 },
  { icon: Database, label: 'Buffer pool hit', value: 0.94, color: '#4589ff', decimals: 2 },
  { icon: Timer, label: 'Log util %', value: 68, color: '#4589ff', decimals: 0 },
  { icon: HardDrive, label: 'Tablespaces', value: 4, color: '#4589ff', decimals: 0 },
];

const capabilities = [
  'Connections + buffer pool hit ratio — same signals as LUW health monitors',
  'Transaction log utilization % — capacity and recovery headroom',
  'Lock wait averages — correlates with connection spikes under batch load',
  'Tablespace used vs total GB — USERSPACE1, WAREHOUSE_TS, SYSCATSPACE, TEMPSPACE1',
  'Deadlocks & sort overflows — cumulative counters for tuning stories',
  'Pre-wired alert: High Connection Count → AI RCA Workflow',
];

export function Slide08Db2() {
  return (
    <SlideLayout shadowColor="rgba(69, 137, 255, 0.45)" shadowSpeed={47} shadowScale={73}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <p className="text-[#4589ff] text-xs font-semibold tracking-widest uppercase">IBM Db2 LUW</p>
            <span className="text-white/55 text-[10px] border border-white/15 rounded-full px-2 py-0.5">TSDB · db2receiver · connections + buffer pool + logs</span>
          </div>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Buffer Pool, Logs <span className="text-white/55">& Tablespaces</span>
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
                    <CountUp end={m.value} decimals={m.decimals} delay={0.3 + i * 0.07} />
                  </div>
                  <div className="text-white/60 text-[10px]">{m.label}</div>
                </motion.div>
              ))}
            </div>

            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.45 }}
              className="flex flex-col gap-2 p-4 rounded-xl border border-[#4589ff]/20 bg-[#4589ff]/5 flex-1 min-h-0">
              <h3 className="text-white/60 text-[10px] font-semibold uppercase tracking-widest">Dashboard panels</h3>
              {capabilities.map((c, i) => (
                <motion.div key={c} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + i * 0.06 }}
                  className="flex items-start gap-2 text-white/75 text-xs leading-snug">
                  <span className="text-[#4589ff] flex-shrink-0">→</span>{c}
                </motion.div>
              ))}
            </motion.div>
          </div>

          <DashboardScreenshot
            src="dashboards/db2.png"
            alt="Kibana dashboard: IBM Db2 LUW performance and health with AI recommendations"
            caption="Live dashboard · Elastic Observability Serverless"
          />
        </div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}
          className="text-[9px] text-white/40">
          Stream: <code className="text-white/55">metrics-db2receiver.otel.otel-default</code>
          <span className="ml-3 text-white/30">·</span>
          <span className="ml-3">Synthetic LUW-style <span className="text-[#4589ff]/70">db2.*</span> metrics via OpenTelemetry OTLP</span>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

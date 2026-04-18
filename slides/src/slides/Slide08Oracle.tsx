import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { DashboardScreenshot } from '@/components/DashboardScreenshot';
import { Users, Layers, BookOpen, Cpu } from 'lucide-react';
import { CountUp } from '@/components/charts/CountUp';

const metrics = [
  { icon: Users,   label: 'Active Sessions', value: 142, color: '#f97316' },
  { icon: Layers,  label: 'Tablespaces',     value: 7,   color: '#f97316' },
  { icon: BookOpen,label: 'Hard Parses/min', value: 38,  color: '#ef4444' },
  { icon: Cpu,     label: 'PGA Memory (GB)', value: 1.8, color: '#f97316' },
];

const capabilities = [
  'Active vs inactive sessions over time — alert threshold at 250',
  'Tablespace utilisation (used vs total GB) — all 7 spaces',
  'Hard parse rate — indicates poor SQL plan cache efficiency',
  'Physical vs logical reads — storage I/O health at a glance',
  'PGA memory trend — per-instance by service.name',
  'Pre-wired alert: High Active Sessions → AI RCA Workflow',
];

export function Slide08Oracle() {
  return (
    <SlideLayout shadowColor="rgba(249, 115, 22, 0.45)" shadowSpeed={47} shadowScale={73}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <p className="text-[#f97316] text-xs font-semibold tracking-widest uppercase">Oracle Database</p>
            <span className="text-white/55 text-[10px] border border-white/15 rounded-full px-2 py-0.5">TSDB · oracledbreceiver · sessions + tablespaces + parses</span>
          </div>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Sessions, Tablespaces <span className="text-white/55">& Parse Efficiency</span>
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
                    <CountUp end={m.value} decimals={m.value % 1 !== 0 ? 1 : 0} delay={0.3 + i * 0.07} />
                  </div>
                  <div className="text-white/60 text-[10px]">{m.label}</div>
                </motion.div>
              ))}
            </div>

            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.45 }}
              className="flex flex-col gap-2 p-4 rounded-xl border border-[#f97316]/20 bg-[#f97316]/5 flex-1 min-h-0">
              <h3 className="text-white/60 text-[10px] font-semibold uppercase tracking-widest">Dashboard panels</h3>
              {capabilities.map((c, i) => (
                <motion.div key={c} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + i * 0.06 }}
                  className="flex items-start gap-2 text-white/75 text-xs leading-snug">
                  <span className="text-[#f97316] flex-shrink-0">→</span>{c}
                </motion.div>
              ))}
            </motion.div>
          </div>

          <DashboardScreenshot
            src="dashboards/oracle.png"
            alt="Kibana dashboard: Oracle performance and health with AI recommendations"
            caption="Live dashboard · Elastic Observability Serverless"
          />
        </div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9 }}
          className="text-[9px] text-white/40">
          Stream: <code className="text-white/55">metrics-oracledbreceiver.otel.otel-default</code>
          <span className="ml-3 text-white/30">·</span>
          <span className="ml-3">Elastic Oracle integration: <span className="text-[#f97316]/70">elastic.co/docs/reference/integrations/oracle</span></span>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

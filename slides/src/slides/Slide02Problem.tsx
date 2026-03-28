import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { AlertTriangle, DollarSign, Puzzle, Eye } from 'lucide-react';
import { HBar } from '@/components/charts/HBar';
import { Donut } from '@/components/charts/Donut';

const pains = [
  { icon: DollarSign, color: '#f04e98', title: 'Escalating Costs', body: 'Datadog DBM charges per host/month on top of APM. SQL Server and MongoDB are premium add-ons.' },
  { icon: Puzzle, color: '#f59e0b', title: 'Agent Sprawl', body: 'Proprietary agents per vendor, per engine. Every major upgrade is a migration project.' },
  { icon: Eye, color: '#a855f7', title: 'Fragmented Visibility', body: 'MySQL slow queries and PostgreSQL spikes live in separate tools — correlation is manual.' },
  { icon: AlertTriangle, color: '#ef4444', title: 'Reactive Alerting', body: 'Root cause analysis is still a war-room exercise. AI-powered RCA is an enterprise add-on.' },
];

const costData = [
  { label: 'Datadog DBM', value: 100, color: '#f04e98' },
  { label: 'Dynatrace', value: 85, color: '#f59e0b' },
  { label: 'New Relic', value: 75, color: '#a855f7' },
  { label: 'Elastic', value: 32, color: '#1ba9f5' },
];

export function Slide02Problem() {
  return (
    <SlideLayout shadowColor="rgba(239, 68, 68, 0.4)" shadowSpeed={40} shadowScale={70}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[#f04e98] text-xs font-semibold tracking-widest uppercase mb-1">The Challenge</p>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Why Your Current Stack <span className="text-white/55">Isn't Cutting It</span>
          </h2>
        </motion.div>

        <div className="flex gap-5 flex-1 min-h-0">
          {/* Left: pain points */}
          <div className="flex flex-col gap-3 flex-1 min-h-0">
            {pains.map((p, i) => (
              <motion.div key={p.title} initial={{ opacity: 0, x: -14 }} animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.15 + i * 0.1, duration: 0.4 }}
                className="flex gap-3 p-4 rounded-xl border border-white/12 bg-white/6 flex-1">
                <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ background: `${p.color}18`, border: `1px solid ${p.color}35` }}>
                  <p.icon size={16} style={{ color: p.color }} />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">{p.title}</h3>
                  <p className="text-white/70 text-xs leading-relaxed mt-0.5">{p.body}</p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Right: infographics */}
          <motion.div initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
            className="flex flex-col gap-4 w-52 flex-shrink-0">

            {/* Cost comparison bar chart */}
            <div className="p-4 rounded-2xl border border-white/12 bg-white/6 flex flex-col gap-3">
              <p className="text-white/55 text-[10px] uppercase tracking-widest font-semibold">Relative Cost Index</p>
              <HBar items={costData} delay={0.4} unit="" />
              <p className="text-[#1ba9f5] text-[10px] text-center mt-1">Elastic = lowest TCO</p>
            </div>

            {/* Tool count donuts */}
            <div className="p-4 rounded-2xl border border-white/12 bg-white/6 flex flex-col gap-3">
              <p className="text-white/55 text-[10px] uppercase tracking-widest font-semibold">Agents Required</p>
              <div className="flex justify-around items-center">
                <div className="flex flex-col items-center gap-1">
                  <Donut value={75} color="#f04e98" size={64} label="4+" sublabel="Datadog" delay={0.5} thickness={8} />
                </div>
                <div className="flex flex-col items-center gap-1">
                  <Donut value={10} color="#1ba9f5" size={64} label="0" sublabel="Elastic" delay={0.6} thickness={8} />
                </div>
              </div>
              <p className="text-white/55 text-[10px] text-center">OTel replaces proprietary agents</p>
            </div>
          </motion.div>
        </div>
      </div>
    </SlideLayout>
  );
}

import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Bell, Search, FileText, CheckCircle, ArrowDown } from 'lucide-react';

const steps = [
  {
    icon: Bell, num: '01', color: '#ef4444',
    title: 'Alert Fires',
    items: ['5 pre-wired rules', 'MySQL · PG · SQL · Mongo', 'ES|QL threshold check', 'Debounced, noise-free'],
    badge: 'Kibana Alerting',
  },
  {
    icon: Search, num: '02', color: '#f59e0b',
    title: 'AI Investigates',
    items: ['Observability AI agent', 'Queries Logs + Metrics', 'Correlates across DBs', 'Identifies root cause'],
    badge: 'observability.agent',
  },
  {
    icon: FileText, num: '03', color: '#3b82f6',
    title: 'Case Created',
    items: ['Full markdown writeup', 'Kibana Cases API', 'Deep-links to Discover', 'Workflow trace ID'],
    badge: 'Kibana Cases',
  },
  {
    icon: CheckCircle, num: '04', color: '#00bfa5',
    title: 'Acknowledge & Learn',
    items: ['Human reviews case', 'Add resolution notes', 'Closed-loop feedback', 'Feeds ML baselines'],
    badge: 'Human in loop',
  },
];

// Animated SVG line connecting steps
function Connector({ color, delay }: { color: string; delay: number }) {
  return (
    <div className="flex flex-col items-center py-0.5 flex-shrink-0">
      <div className="flex-1 w-px bg-white/10 relative overflow-hidden">
        <motion.div className="absolute inset-0 w-full"
          style={{ background: `linear-gradient(to bottom, ${color}, transparent)` }}
          initial={{ scaleY: 0, transformOrigin: 'top' }}
          animate={{ scaleY: 1 }}
          transition={{ delay, duration: 0.6, ease: 'easeOut' }} />
      </div>
      <motion.div initial={{ scale: 0, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: delay + 0.3, duration: 0.3 }}>
        <ArrowDown size={10} className="text-white/30" />
      </motion.div>
    </div>
  );
}

export function Slide10AIWorkflow() {
  return (
    <SlideLayout shadowColor="rgba(168, 85, 247, 0.5)" shadowSpeed={55} shadowScale={80}>
      <div className="flex flex-col h-full px-10 py-8 gap-4 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[#a855f7] text-xs font-semibold tracking-widest uppercase mb-1">AI Workflows</p>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Alert → Investigate → <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#a855f7] to-[#1ba9f5]">Case Closed</span>
          </h2>
        </motion.div>

        <div className="flex gap-5 flex-1 min-h-0">
          {/* Flow — left column */}
          <div className="flex flex-1 gap-2 min-h-0">
            <div className="flex flex-col">
              {steps.map((step, i) => (
                <div key={step.num} className="flex gap-2 flex-1">
                  {/* Step block */}
                  <motion.div
                    initial={{ opacity: 0, x: -14 }} animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.15 + i * 0.12 }}
                    className="flex gap-3 p-4 rounded-xl border border-white/12 bg-white/6 flex-1">
                    <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
                      style={{ background: `${step.color}18`, border: `1px solid ${step.color}35` }}>
                      <step.icon size={17} style={{ color: step.color }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-mono text-white/40">{step.num}</span>
                        <span className="text-white font-semibold text-sm">{step.title}</span>
                        <span className="ml-auto text-[9px] px-2 py-0.5 rounded-full border border-white/15 text-white/50">{step.badge}</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {step.items.map(item => (
                          <span key={item} className="text-[10px] text-white/65 border border-white/10 rounded px-1.5 py-0.5 bg-white/4">{item}</span>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                </div>
              ))}
            </div>

            {/* Vertical connectors */}
            <div className="flex flex-col gap-0 w-6 mt-8">
              {steps.slice(0, -1).map((step, i) => (
                <Connector key={step.num} color={step.color} delay={0.5 + i * 0.12} />
              ))}
            </div>
          </div>

          {/* Right: key benefits */}
          <motion.div initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}
            className="flex flex-col gap-3 w-48 flex-shrink-0">
            <div className="p-4 rounded-2xl border border-[#a855f7]/25 bg-[#a855f7]/6 flex flex-col gap-3">
              <p className="text-[#a855f7] text-[10px] font-semibold uppercase tracking-widest">Key Benefits</p>
              {[
                { label: 'MTTR', value: '−60%', desc: 'vs manual triage' },
                { label: 'Alert noise', value: '−80%', desc: 'via debounce + AI' },
                { label: 'On-call load', value: '−45%', desc: 'automated RCA' },
              ].map(b => (
                <div key={b.label} className="border-t border-white/8 pt-2">
                  <div className="text-2xl font-bold text-white">{b.value}</div>
                  <div className="text-[#a855f7] text-[10px] font-semibold">{b.label}</div>
                  <div className="text-white/50 text-[9px]">{b.desc}</div>
                </div>
              ))}
            </div>
            <div className="p-3 rounded-2xl border border-white/12 bg-white/6 flex flex-col gap-1">
              <p className="text-white/55 text-[10px] uppercase tracking-widest font-semibold">Workflow Tech</p>
              {['Kibana Workflows API (preview)', 'observability.agent LLM', 'Liquid template engine', 'YAML-as-code definition'].map(t => (
                <div key={t} className="text-white/65 text-[10px] flex items-start gap-1.5">
                  <span className="text-[#a855f7]">·</span>{t}
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </SlideLayout>
  );
}

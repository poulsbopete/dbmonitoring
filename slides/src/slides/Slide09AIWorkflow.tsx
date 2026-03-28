import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Bell, Bot, FileText, GitBranch, Zap } from 'lucide-react';

const steps = [
  {
    icon: Bell,
    color: '#ef4444',
    label: 'Alert Fires',
    desc: '5 pre-wired rules across all 4 DB types trigger on anomalies',
  },
  {
    icon: Bot,
    color: '#1ba9f5',
    label: 'AI Investigates',
    desc: 'Observability AI Agent runs ES|QL queries, checks metrics & logs, identifies root cause',
  },
  {
    icon: FileText,
    color: '#a855f7',
    label: 'Case Created',
    desc: 'Kibana case auto-created with AI-written title, description, and investigation trail',
  },
  {
    icon: GitBranch,
    color: '#00bfa5',
    label: 'Evidence Attached',
    desc: 'Triggering alert, full conversation reasoning, and Discover deep-links attached',
  },
];

export function Slide09AIWorkflow() {
  return (
    <SlideLayout shadowColor="rgba(27, 169, 245, 0.5)" shadowSpeed={55} shadowScale={80}>
      <div className="flex flex-col h-full px-16 py-14 gap-8">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-2">
            <p className="text-[#1ba9f5] text-sm font-medium tracking-widest uppercase">AI-Powered RCA</p>
            <span className="text-white/20 text-xs border border-white/10 rounded-full px-2 py-0.5">Elastic Workflows · Preview</span>
          </div>
          <h2 className="text-5xl font-bold text-white">
            From Alert to Root Cause
            <br />
            <span className="text-white/50">Without Human Intervention</span>
          </h2>
        </motion.div>

        {/* Flow steps */}
        <div className="flex items-center gap-3 flex-1">
          {steps.map((step, i) => (
            <React.Fragment key={step.label}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + i * 0.15 }}
                className="flex-1 flex flex-col gap-4 p-6 rounded-2xl border bg-white/3"
                style={{ borderColor: `${step.color}25` }}
              >
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center"
                  style={{ background: `${step.color}18`, border: `1px solid ${step.color}30` }}
                >
                  <step.icon size={22} style={{ color: step.color }} />
                </div>
                <div>
                  <div className="text-white font-semibold mb-1">{step.label}</div>
                  <div className="text-white/55 text-sm leading-relaxed">{step.desc}</div>
                </div>
                <div
                  className="text-xs font-mono rounded-lg px-3 py-2"
                  style={{ background: `${step.color}10`, color: step.color }}
                >
                  Step {i + 1} of 4
                </div>
              </motion.div>
              {i < steps.length - 1 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 + i * 0.15 }}
                >
                  <Zap size={20} className="text-white/20" />
                </motion.div>
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Code snippet */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="rounded-xl border border-white/8 bg-black/30 px-6 py-4 font-mono text-xs text-white/50 flex gap-8"
        >
          <div>
            <span className="text-white/25">trigger: </span>
            <span className="text-[#1ba9f5]">alert</span>
          </div>
          <div>
            <span className="text-white/25">agent: </span>
            <span className="text-[#00bfa5]">observability.agent</span>
          </div>
          <div>
            <span className="text-white/25">rules: </span>
            <span className="text-[#a855f7]">5 db monitoring rules</span>
          </div>
          <div>
            <span className="text-white/25">output: </span>
            <span className="text-[#f59e0b]">kibana.case + comments</span>
          </div>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

// Need React for Fragment
import React from 'react';

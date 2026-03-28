import React from 'react';
import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Bell, Bot, FileText, GitBranch, ArrowRight } from 'lucide-react';

const steps = [
  {
    icon: Bell,
    color: '#ef4444',
    label: 'Alert Fires',
    desc: '5 pre-wired rules cover all 4 DB types. Triggers on slow queries, connection spikes, deadlocks, transaction surges, and op rate anomalies.',
    detail: 'MySQL · PostgreSQL · SQL Server · MongoDB',
  },
  {
    icon: Bot,
    color: '#1ba9f5',
    label: 'AI Investigates',
    desc: 'Observability AI Agent runs ES|QL queries across logs and metrics, correlates signals across all 4 engines, and identifies root cause.',
    detail: 'observability.agent via Kibana Workflows',
  },
  {
    icon: FileText,
    color: '#a855f7',
    label: 'Case Created',
    desc: 'Kibana case auto-created with AI-written title and description. Investigation trail and reasoning steps attached as comments.',
    detail: 'owner: observability · severity: medium',
  },
  {
    icon: GitBranch,
    color: '#00bfa5',
    label: 'Evidence Linked',
    desc: 'Triggering alert, full AI conversation, and Discover deep-links for every ES|QL query run during the investigation are attached.',
    detail: 'context.kibana_url deep-links included',
  },
];

export function Slide09AIWorkflow() {
  return (
    <SlideLayout shadowColor="rgba(27, 169, 245, 0.5)" shadowSpeed={55} shadowScale={80}>
      <div className="flex flex-col h-full px-10 py-8 gap-5 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-1">
            <p className="text-[#1ba9f5] text-xs font-semibold tracking-widest uppercase">AI-Powered RCA</p>
            <span className="text-white/25 text-[10px] border border-white/10 rounded-full px-2 py-0.5">Elastic Workflows · Technical Preview</span>
          </div>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Alert → Root Cause → Case <span className="text-white/40">Without Human Intervention</span>
          </h2>
        </motion.div>

        <div className="flex items-stretch gap-2 flex-1 min-h-0">
          {steps.map((step, i) => (
            <React.Fragment key={step.label}>
              <motion.div
                initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + i * 0.13 }}
                className="flex-1 flex flex-col gap-3 p-5 rounded-2xl border bg-white/3"
                style={{ borderColor: `${step.color}22` }}>
                <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ background: `${step.color}18`, border: `1px solid ${step.color}30` }}>
                  <step.icon size={18} style={{ color: step.color }} />
                </div>
                <div className="flex flex-col gap-1 flex-1">
                  <div className="text-white font-semibold">{step.label}</div>
                  <p className="text-white/55 text-sm leading-snug flex-1">{step.desc}</p>
                </div>
                <div className="text-[10px] font-mono rounded-lg px-3 py-1.5 leading-snug"
                  style={{ background: `${step.color}10`, color: `${step.color}cc` }}>
                  {step.detail}
                </div>
                <div className="text-xs text-white/20 font-mono">Step {i + 1} / {steps.length}</div>
              </motion.div>
              {i < steps.length - 1 && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.35 + i * 0.13 }}
                  className="flex items-center flex-shrink-0">
                  <ArrowRight size={16} className="text-white/15" />
                </motion.div>
              )}
            </React.Fragment>
          ))}
        </div>

        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.85 }}
          className="rounded-xl border border-white/8 bg-black/25 px-5 py-3 font-mono text-[10px] text-white/40 flex flex-wrap gap-x-8 gap-y-1">
          <span><span className="text-white/20">trigger: </span><span className="text-[#1ba9f5]">alert</span></span>
          <span><span className="text-white/20">agent: </span><span className="text-[#00bfa5]">observability.agent</span></span>
          <span><span className="text-white/20">rules: </span><span className="text-[#a855f7]">5 database monitoring rules</span></span>
          <span><span className="text-white/20">output: </span><span className="text-[#f59e0b]">kibana.case + comments + alert link</span></span>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

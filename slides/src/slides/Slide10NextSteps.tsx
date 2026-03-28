import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { PlayCircle, Calendar, FileCheck, MessageSquare } from 'lucide-react';

const steps = [
  {
    icon: PlayCircle, color: '#1ba9f5', number: '01', title: 'Live Demo Now',
    body: 'Walk through 4 Kibana dashboards with live data flowing from MySQL, PostgreSQL, SQL Server, and MongoDB — all seeded before the session began.',
    cta: 'Dashboards already open in Kibana →',
  },
  {
    icon: MessageSquare, color: '#a855f7', number: '02', title: 'AI RCA Demo',
    body: 'Trigger an alert live and watch the Observability AI Agent investigate, generate a root cause, and create a Kibana case — end to end in under 2 minutes.',
    cta: 'Alerts → Rules → trigger manually →',
  },
  {
    icon: FileCheck, color: '#00bfa5', number: '03', title: 'Your Data, Your Queries',
    body: 'Connect your actual databases. Use ES|QL to answer questions your current tool can\'t. Build a custom dashboard live using Cursor + Elastic Agent Skills.',
    cta: 'Cursor + observability-esql skill ready →',
  },
  {
    icon: Calendar, color: '#f59e0b', number: '04', title: '30-Day POC',
    body: 'Define success criteria together. Deploy Elastic against your production-like environment with dedicated team support. Cancel Datadog DBM by month 2.',
    cta: 'book.elastic.co/poc →',
  },
];

export function Slide10NextSteps() {
  return (
    <SlideLayout shadowColor="rgba(27, 169, 245, 0.55)" shadowSpeed={50} shadowScale={82}>
      <div className="flex flex-col h-full px-10 py-8 gap-5 overflow-hidden">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[#1ba9f5] text-xs font-semibold tracking-widest uppercase mb-1">What's Next</p>
          <h2 className="text-4xl font-bold text-white leading-tight">
            Ready to Replace <span className="text-white/70">Your DB Monitoring Stack?</span>
          </h2>
        </motion.div>

        <div className="grid grid-cols-2 gap-4 flex-1 min-h-0">
          {steps.map((s, i) => (
            <motion.div key={s.number}
              initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 + i * 0.1 }}
              className="flex gap-4 p-5 rounded-2xl border border-white/15 bg-white/3 min-h-0">
              <div className="flex flex-col items-center gap-2 flex-shrink-0">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                  style={{ background: `${s.color}18`, border: `1px solid ${s.color}30` }}>
                  <s.icon size={18} style={{ color: s.color }} />
                </div>
                <span className="text-white/20 text-[10px] font-mono">{s.number}</span>
              </div>
              <div className="flex flex-col gap-1.5 min-w-0">
                <h3 className="text-white font-semibold">{s.title}</h3>
                <p className="text-white/80 text-sm leading-snug flex-1">{s.body}</p>
                <div className="text-[10px] mt-1 font-mono" style={{ color: `${s.color}99` }}>{s.cta}</div>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}
          className="flex items-center justify-between p-4 rounded-2xl border border-[#1ba9f5]/20 bg-[#1ba9f5]/6">
          <div>
            <p className="text-white font-semibold text-sm">Try the hands-on Instruqt lab right now</p>
            <p className="text-white/45 text-xs mt-0.5">4-hour sandbox · 4 databases · AI RCA · your browser · no install required</p>
          </div>
          <div className="text-[#1ba9f5] font-mono text-xs border border-[#1ba9f5]/30 rounded-xl px-4 py-2 flex-shrink-0">
            play.instruqt.com/elastic
          </div>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

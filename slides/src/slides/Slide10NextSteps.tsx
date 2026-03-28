import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { PlayCircle, Calendar, FileCheck, MessageSquare } from 'lucide-react';

const steps = [
  {
    icon: PlayCircle,
    color: '#1ba9f5',
    number: '01',
    title: 'Live Demo',
    body: 'Walk through the Elastic Observability environment with live data flowing from all 4 database engines. All 4 Kibana dashboards ready.',
  },
  {
    icon: MessageSquare,
    color: '#a855f7',
    number: '02',
    title: 'AI RCA Demo',
    body: 'Trigger an alert live and watch the Observability AI Agent investigate, write a case, and attach evidence — end to end in under 2 minutes.',
  },
  {
    icon: FileCheck,
    color: '#00bfa5',
    number: '03',
    title: 'Your Data, Your Queries',
    body: 'Connect your actual database agents. Use ES|QL to answer the questions your current tool can\'t. Build a custom dashboard in real-time with Cursor.',
  },
  {
    icon: Calendar,
    color: '#f59e0b',
    number: '04',
    title: 'POC Agreement',
    body: 'Define success criteria and deploy against your production-like environment. 30-day guided POC with dedicated Elastic team support.',
  },
];

export function Slide10NextSteps() {
  return (
    <SlideLayout shadowColor="rgba(27, 169, 245, 0.55)" shadowSpeed={50} shadowScale={82}>
      <div className="flex flex-col h-full px-16 py-14 gap-8">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[#1ba9f5] text-sm font-medium tracking-widest uppercase mb-2">What's Next</p>
          <h2 className="text-5xl font-bold text-white">
            Ready to Replace
            <br />
            <span className="text-white/50">Your DB Monitoring Stack?</span>
          </h2>
        </motion.div>

        <div className="grid grid-cols-2 gap-5 flex-1">
          {steps.map((s, i) => (
            <motion.div
              key={s.number}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.12 }}
              className="flex gap-5 p-6 rounded-2xl border border-white/8 bg-white/3"
            >
              <div className="flex flex-col items-center gap-2">
                <div
                  className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ background: `${s.color}18`, border: `1px solid ${s.color}30` }}
                >
                  <s.icon size={22} style={{ color: s.color }} />
                </div>
                <span className="text-white/20 text-xs font-mono">{s.number}</span>
              </div>
              <div>
                <h3 className="text-white font-semibold text-lg mb-1">{s.title}</h3>
                <p className="text-white/55 text-sm leading-relaxed">{s.body}</p>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="flex items-center justify-between p-5 rounded-2xl border border-[#1ba9f5]/25 bg-[#1ba9f5]/6"
        >
          <div>
            <p className="text-white font-semibold">Try the hands-on lab right now</p>
            <p className="text-white/50 text-sm mt-0.5">Instruqt sandbox — 4 hours, your browser, no install</p>
          </div>
          <div className="text-[#1ba9f5] font-mono text-sm border border-[#1ba9f5]/30 rounded-xl px-4 py-2">
            play.instruqt.com/elastic
          </div>
        </motion.div>
      </div>
    </SlideLayout>
  );
}

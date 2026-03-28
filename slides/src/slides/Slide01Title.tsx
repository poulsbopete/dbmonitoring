import { motion } from 'framer-motion';
import { SlideLayout } from '@/components/SlideLayout';
import { Database } from 'lucide-react';

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};
const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.15, delayChildren: 0.3 } },
};

export function Slide01Title() {
  return (
    <SlideLayout shadowColor="rgba(27, 169, 245, 0.55)" shadowSpeed={55} shadowScale={85}>
      <div className="flex flex-col items-center justify-center h-full px-12 text-center gap-6">
        <motion.div variants={container} initial="hidden" animate="show" className="flex flex-col items-center gap-6">
          {/* Logo badge */}
          <motion.div variants={item} className="flex items-center gap-3 px-5 py-2 rounded-full border border-[#1ba9f5]/40 bg-[#1ba9f5]/10 text-[#1ba9f5] text-sm font-medium tracking-wide">
            <Database size={16} />
            Elastic Observability · Database Monitoring POC
          </motion.div>

          <motion.h1
            variants={item}
            className="text-6xl md:text-8xl font-bold tracking-tight text-white leading-[1.05]"
          >
            Database Monitoring
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#1ba9f5] via-[#a855f7] to-[#f04e98]">
              Without Compromise
            </span>
          </motion.h1>

          <motion.p
            variants={item}
            className="text-xl md:text-2xl text-white/60 max-w-3xl leading-relaxed"
          >
            MySQL · PostgreSQL · SQL Server · MongoDB — one platform,
            no proprietary agents, powered by OpenTelemetry
          </motion.p>

          <motion.div variants={item} className="flex items-center gap-8 mt-4 text-white/40 text-sm">
            <span>vs Datadog DBM</span>
            <span className="w-1 h-1 rounded-full bg-white/20" />
            <span>vs Dynatrace</span>
            <span className="w-1 h-1 rounded-full bg-white/20" />
            <span>Proof of Concept · 2026</span>
          </motion.div>
        </motion.div>

        {/* Bottom elastic wordmark */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2, duration: 0.8 }}
          className="absolute bottom-16 text-white/20 text-xs tracking-[0.3em] uppercase"
        >
          Elastic
        </motion.div>
      </div>
    </SlideLayout>
  );
}

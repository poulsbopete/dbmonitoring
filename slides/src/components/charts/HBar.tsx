import { motion } from 'framer-motion';

interface HBarItem { label: string; value: number; color?: string; }

interface HBarProps {
  items: HBarItem[];
  color?: string;
  delay?: number;
  unit?: string;
}

export function HBar({ items, color = '#1ba9f5', delay = 0.4, unit = '' }: HBarProps) {
  const max = Math.max(...items.map(i => i.value));
  return (
    <div className="flex flex-col gap-1.5 w-full">
      {items.map((item, i) => (
        <div key={item.label} className="flex items-center gap-2">
          <div className="text-white/60 text-[10px] w-20 text-right flex-shrink-0 truncate">{item.label}</div>
          <div className="flex-1 bg-white/5 rounded-full h-2 overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ background: item.color || color }}
              initial={{ width: 0 }}
              animate={{ width: `${(item.value / max) * 100}%` }}
              transition={{ delay: delay + i * 0.08, duration: 0.7, ease: 'easeOut' }}
            />
          </div>
          <div className="text-[10px] w-10 flex-shrink-0" style={{ color: item.color || color }}>
            {item.value}{unit}
          </div>
        </div>
      ))}
    </div>
  );
}

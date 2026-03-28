import { motion } from 'framer-motion';

interface SparklineProps {
  data: number[];
  color?: string;
  height?: number;
  filled?: boolean;
  delay?: number;
}

export function Sparkline({ data, color = '#1ba9f5', height = 48, filled = true, delay = 0.3 }: SparklineProps) {
  const w = 200;
  const h = height;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const xs = data.map((_, i) => (i / (data.length - 1)) * w);
  const ys = data.map(v => h - ((v - min) / range) * (h * 0.85) - h * 0.05);
  const points = xs.map((x, i) => `${x},${ys[i]}`).join(' ');
  const linePath = `M ${points.split(' ').join(' L ')}`;
  const areaPath = `${linePath} L ${w},${h} L 0,${h} Z`;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full" style={{ height }}>
      <defs>
        <linearGradient id={`sg-${color.replace('#','')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      {filled && (
        <motion.path
          d={areaPath}
          fill={`url(#sg-${color.replace('#','')})`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay, duration: 0.6 }}
        />
      )}
      <motion.path
        d={linePath}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ delay, duration: 1.2, ease: 'easeOut' }}
      />
      {/* Last point dot */}
      <motion.circle
        cx={xs[xs.length - 1]}
        cy={ys[ys.length - 1]}
        r="3"
        fill={color}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: delay + 1, duration: 0.3 }}
      />
    </svg>
  );
}

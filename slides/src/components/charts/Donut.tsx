import { motion } from 'framer-motion';

interface DonutProps {
  value: number;       // 0–100
  color?: string;
  size?: number;
  label?: string;
  sublabel?: string;
  delay?: number;
  thickness?: number;
}

export function Donut({ value, color = '#1ba9f5', size = 80, label, sublabel, delay = 0.3, thickness = 10 }: DonutProps) {
  const r = (size - thickness) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (value / 100) * circ;

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={thickness} />
        <motion.circle
          cx={size/2} cy={size/2} r={r}
          fill="none" stroke={color} strokeWidth={thickness}
          strokeLinecap="round"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: circ - dash }}
          transition={{ delay, duration: 1.2, ease: 'easeOut' }}
        />
      </svg>
      {label && (
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="font-bold text-white leading-none" style={{ fontSize: size * 0.18 }}>{label}</span>
          {sublabel && <span className="text-white/50 leading-none mt-0.5" style={{ fontSize: size * 0.1 }}>{sublabel}</span>}
        </div>
      )}
    </div>
  );
}

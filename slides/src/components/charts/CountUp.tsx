import { useEffect, useRef, useState } from 'react';

interface CountUpProps {
  end: number;
  suffix?: string;
  prefix?: string;
  decimals?: number;
  duration?: number;
  delay?: number;
  className?: string;
}

export function CountUp({ end, suffix = '', prefix = '', decimals = 0, duration = 1.5, delay = 0.3, className = '' }: CountUpProps) {
  const [val, setVal] = useState(0);
  const started = useRef(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      started.current = true;
      const start = performance.now();
      const tick = (now: number) => {
        const t = Math.min((now - start) / (duration * 1000), 1);
        const eased = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
        setVal(eased * end);
        if (t < 1) requestAnimationFrame(tick);
        else setVal(end);
      };
      requestAnimationFrame(tick);
    }, delay * 1000);
    return () => clearTimeout(timer);
  }, [end, duration, delay]);

  return (
    <span className={className}>
      {prefix}{val.toFixed(decimals)}{suffix}
    </span>
  );
}

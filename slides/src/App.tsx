import { useState, useEffect, useCallback } from 'react';
import { AnimatePresence } from 'framer-motion';
import { SlideNav } from './components/SlideNav';
import { Slide01Title } from './slides/Slide01Title';
import { Slide02Problem } from './slides/Slide02Problem';
import { Slide03Architecture } from './slides/Slide03Architecture';
import { Slide04MySQL } from './slides/Slide04MySQL';
import { Slide05Postgres } from './slides/Slide05Postgres';
import { Slide06SQLServer } from './slides/Slide06SQLServer';
import { Slide07MongoDB } from './slides/Slide07MongoDB';
import { Slide08Oracle } from './slides/Slide08Oracle';
import { Slide09Comparison } from './slides/Slide09Comparison';
import { Slide10AIWorkflow } from './slides/Slide10AIWorkflow';
import { Slide11NextSteps } from './slides/Slide11NextSteps';

const SLIDES = [
  Slide01Title,
  Slide02Problem,
  Slide03Architecture,
  Slide04MySQL,
  Slide05Postgres,
  Slide06SQLServer,
  Slide07MongoDB,
  Slide08Oracle,
  Slide09Comparison,
  Slide10AIWorkflow,
  Slide11NextSteps,
];

export default function App() {
  const [current, setCurrent] = useState(0);

  const prev = useCallback(() => setCurrent((c) => Math.max(0, c - 1)), []);
  const next = useCallback(() => setCurrent((c) => Math.min(SLIDES.length - 1, c + 1)), []);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') next();
      if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') prev();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [next, prev]);

  // Touch swipe support
  useEffect(() => {
    let startX = 0;
    const onTouchStart = (e: TouchEvent) => { startX = e.touches[0].clientX; };
    const onTouchEnd = (e: TouchEvent) => {
      const dx = startX - e.changedTouches[0].clientX;
      if (Math.abs(dx) > 50) dx > 0 ? next() : prev();
    };
    window.addEventListener('touchstart', onTouchStart);
    window.addEventListener('touchend', onTouchEnd);
    return () => {
      window.removeEventListener('touchstart', onTouchStart);
      window.removeEventListener('touchend', onTouchEnd);
    };
  }, [next, prev]);

  const CurrentSlide = SLIDES[current];

  return (
    <div className="w-full h-full relative">
      <AnimatePresence mode="wait">
        <CurrentSlide key={current} />
      </AnimatePresence>
      <SlideNav current={current} total={SLIDES.length} onPrev={prev} onNext={next} />

      {/* Slide counter top-right */}
      <div className="fixed top-5 right-6 z-50 text-white/20 text-xs font-mono tabular-nums">
        {current + 1} / {SLIDES.length}
      </div>
    </div>
  );
}

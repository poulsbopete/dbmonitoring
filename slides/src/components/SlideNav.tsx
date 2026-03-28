import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SlideNavProps {
  current: number;
  total: number;
  onPrev: () => void;
  onNext: () => void;
}

export function SlideNav({ current, total, onPrev, onNext }: SlideNavProps) {
  return (
    <div className="fixed bottom-6 left-0 right-0 z-50 flex items-center justify-center gap-6 select-none">
      <button
        onClick={onPrev}
        disabled={current === 0}
        className={cn(
          'flex items-center justify-center w-10 h-10 rounded-full border border-white/20 bg-white/5 backdrop-blur-sm',
          'text-white/60 hover:text-white hover:bg-white/10 transition-all duration-200',
          'disabled:opacity-20 disabled:cursor-not-allowed',
        )}
      >
        <ChevronLeft size={20} />
      </button>

      {/* Dot indicators */}
      <div className="flex items-center gap-2">
        {Array.from({ length: total }).map((_, i) => (
          <div
            key={i}
            className={cn(
              'rounded-full transition-all duration-300',
              i === current
                ? 'w-6 h-2 bg-white'
                : 'w-2 h-2 bg-white/25',
            )}
          />
        ))}
      </div>

      <button
        onClick={onNext}
        disabled={current === total - 1}
        className={cn(
          'flex items-center justify-center w-10 h-10 rounded-full border border-white/20 bg-white/5 backdrop-blur-sm',
          'text-white/60 hover:text-white hover:bg-white/10 transition-all duration-200',
          'disabled:opacity-20 disabled:cursor-not-allowed',
        )}
      >
        <ChevronRight size={20} />
      </button>
    </div>
  );
}

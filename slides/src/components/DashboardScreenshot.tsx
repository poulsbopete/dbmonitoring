import { motion } from 'framer-motion';

interface DashboardScreenshotProps {
  /** Path under `slides/public/` (e.g. `dashboards/mysql.png`). */
  src: string;
  alt: string;
  caption?: string;
  delay?: number;
  /** Tailwind classes for the `<img>` (max height / object fit). */
  imageClassName?: string;
  /** Tailwind classes for the outer motion wrapper (width / flex). */
  wrapperClassName?: string;
}

export function DashboardScreenshot({
  src,
  alt,
  caption,
  delay = 0.35,
  imageClassName = 'max-h-[min(420px,44vh)]',
  wrapperClassName = 'flex flex-col gap-2 min-h-0 flex-1 w-[min(100%,28rem)] flex-shrink-0',
}: DashboardScreenshotProps) {
  const base = import.meta.env.BASE_URL.endsWith('/') ? import.meta.env.BASE_URL : `${import.meta.env.BASE_URL}/`;
  const url = `${base}${src.replace(/^\//, '')}`;

  return (
    <motion.div
      initial={{ opacity: 0, x: 14 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay, duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      className={wrapperClassName}
    >
      <div className="rounded-2xl border border-white/15 overflow-hidden bg-[#0d1117]/90 shadow-[0_20px_50px_-12px_rgba(0,0,0,0.65)] flex-1 min-h-0 flex items-center justify-center p-1">
        <img
          src={url}
          alt={alt}
          className={`w-full h-full object-contain object-top select-none pointer-events-none ${imageClassName}`}
          loading="lazy"
          decoding="async"
        />
      </div>
      {caption ? (
        <p className="text-white/45 text-[9px] text-center leading-tight tracking-wide uppercase font-semibold">
          {caption}
        </p>
      ) : null}
    </motion.div>
  );
}

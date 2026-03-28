import React from 'react';
import { motion } from 'framer-motion';
import { EtherealShadow } from './ui/ethereal-shadow';

interface SlideLayoutProps {
  children: React.ReactNode;
  shadowColor?: string;
  shadowSpeed?: number;
  shadowScale?: number;
  className?: string;
}

const variants = {
  enter: { opacity: 0, y: 24 },
  center: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -24 },
};

export function SlideLayout({
  children,
  shadowColor = 'rgba(59, 130, 246, 0.6)',
  shadowSpeed = 60,
  shadowScale = 80,
  className = '',
}: SlideLayoutProps) {
  return (
    <motion.div
      className={`relative w-full h-full flex flex-col ${className}`}
      variants={variants}
      initial="enter"
      animate="center"
      exit="exit"
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
    >
      {/* Animated background */}
      <div className="absolute inset-0 bg-[#0a0a0f]">
        <EtherealShadow
          color={shadowColor}
          animation={{ scale: shadowScale, speed: shadowSpeed }}
          noise={{ opacity: 0.4, scale: 1.2 }}
          sizing="fill"
        />
      </div>
      {/* Subtle grid overlay */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
                            linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
          backgroundSize: '64px 64px',
        }}
      />
      {/* Content — centered column */}
      <div className="relative z-10 w-full h-full flex flex-col items-center justify-center">
        <div className="w-full max-w-5xl h-full flex flex-col">
          {children}
        </div>
      </div>
    </motion.div>
  );
}

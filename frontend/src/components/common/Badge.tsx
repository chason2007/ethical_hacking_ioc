import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'high' | 'medium' | 'low' | 'info' | 'default' | 'success' | 'protocol';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ children, variant = 'default', className = '' }) => {
  const styles = {
    high: 'bg-red-950/60 text-red-400 border border-red-800/60 font-semibold',
    medium: 'bg-amber-950/60 text-amber-400 border border-amber-800/60 font-semibold',
    low: 'bg-blue-950/60 text-blue-400 border border-blue-800/60',
    info: 'bg-slate-800/80 text-slate-300 border border-slate-700/60',
    success: 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/60',
    protocol: 'bg-cyan-950/50 text-cyan-400 border border-cyan-800/50 font-mono text-xs',
    default: 'bg-slate-900 text-slate-400 border border-slate-800',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs tracking-wide ${styles[variant]} ${className}`}>
      {children}
    </span>
  );
};

import React from 'react';
import { BookOpen, Info, ShieldAlert, CheckCircle2 } from 'lucide-react';

interface EduCardProps {
  title: string;
  category?: string;
  children: React.ReactNode;
  icon?: 'book' | 'info' | 'shield' | 'check';
  className?: string;
}

export const EduCard: React.FC<EduCardProps> = ({
  title,
  category = 'Educational Context',
  children,
  icon = 'book',
  className = '',
}) => {
  const IconComp = {
    book: BookOpen,
    info: Info,
    shield: ShieldAlert,
    check: CheckCircle2,
  }[icon];

  return (
    <div className={`rounded-lg border border-slate-800 bg-slate-900/50 p-4 relative overflow-hidden ${className}`}>
      <div className="absolute top-0 left-0 h-full w-1 bg-gradient-to-b from-cyan-500 to-blue-600" />
      <div className="flex items-start gap-3">
        <div className="p-1.5 rounded bg-cyan-950/50 border border-cyan-800/40 text-cyan-400 mt-0.5">
          <IconComp size={16} />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[10px] font-mono tracking-wider uppercase text-cyan-500 font-semibold">
              {category}
            </span>
          </div>
          <h4 className="text-sm font-medium text-slate-200 mb-1.5">{title}</h4>
          <div className="text-xs text-slate-400 leading-relaxed space-y-1">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import {
  LayoutDashboard,
  Layers,
  Network,
  ShieldAlert,
  FileText,
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
  findingsCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onTabChange, findingsCount = 0 }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'packets', label: 'Packet Explorer', icon: Layers },
    { id: 'traffic', label: 'Traffic & Flows', icon: Network },
    {
      id: 'security',
      label: 'Security Insights',
      icon: ShieldAlert,
      badge: findingsCount > 0 ? findingsCount : undefined,
    },
    { id: 'reports', label: 'Reports & Viva', icon: FileText },
  ];

  return (
    <aside className="w-60 bg-slate-950/80 border-r border-slate-800/80 flex flex-col shrink-0 select-none">
      
      {/* Navigation Group */}
      <div className="p-4 space-y-1.5">
        <div className="px-3 py-2 text-[10px] font-mono font-semibold tracking-wider text-slate-500 uppercase">
          Forensics Platform
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                isActive
                  ? 'bg-cyan-950/80 text-cyan-300 border border-cyan-800/70 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon size={17} className={isActive ? 'text-cyan-400' : 'text-slate-500'} />
                <span>{item.label}</span>
              </div>

              {item.badge !== undefined && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-950 text-amber-400 border border-amber-800/80">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Clean Status Footer */}
      <div className="mt-auto p-4 border-t border-slate-900">
        <div className="px-3 py-2 rounded-lg bg-slate-900/50 border border-slate-800/50 text-[11px] text-slate-400">
          <div className="flex items-center gap-2 text-slate-300 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span>Local Database Active</span>
          </div>
          <div className="text-[10px] text-slate-500 font-mono mt-0.5">
            SQLite • Zero Docker
          </div>
        </div>
      </div>

    </aside>
  );
};

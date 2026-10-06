import React from 'react';
import {
  LayoutDashboard,
  Layers,
  Network,
  Users,
  Server,
  Radio,
  ShieldAlert,
  Clock,
  FileText,
  FolderArchive,
  GraduationCap,
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
    { id: 'protocols', label: 'Protocols', icon: Network },
    { id: 'conversations', label: 'Conversations', icon: Users },
    { id: 'endpoints', label: 'Endpoints', icon: Server },
    { id: 'ports', label: 'Port Analysis', icon: Radio },
    {
      id: 'security',
      label: 'Security Insights',
      icon: ShieldAlert,
      badge: findingsCount > 0 ? findingsCount : undefined,
      badgeVariant: 'amber',
    },
    { id: 'timeline', label: 'Traffic Timeline', icon: Clock },
    { id: 'reports', label: 'Reports & Export', icon: FileText },
    { id: 'captures', label: 'Analysis History', icon: FolderArchive },
    { id: 'educational', label: 'Protocol Guide', icon: GraduationCap },
  ];

  return (
    <aside className="w-56 bg-slate-950/70 border-r border-slate-800/80 flex flex-col shrink-0">
      
      {/* Navigation Group */}
      <div className="p-3 space-y-1">
        <div className="px-3 py-1.5 text-[10px] font-mono tracking-wider text-slate-500 uppercase">
          Network Forensics
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-cyan-950/60 text-cyan-300 border border-cyan-800/60 shadow-xs'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80 border border-transparent'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon size={16} className={isActive ? 'text-cyan-400' : 'text-slate-500'} />
                <span>{item.label}</span>
              </div>

              {item.badge !== undefined && (
                <span className="px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold bg-amber-950/80 text-amber-400 border border-amber-800/60">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Footer Info Box */}
      <div className="mt-auto p-3 border-t border-slate-900 text-[11px] text-slate-500">
        <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60 space-y-1">
          <div className="font-semibold text-slate-300 text-[10px] uppercase tracking-wider font-mono">
            Ethical Hacking Lab
          </div>
          <p className="text-[10px] text-slate-400 leading-tight">
            Defensive traffic inspection & protocol compliance evaluation.
          </p>
        </div>
      </div>

    </aside>
  );
};

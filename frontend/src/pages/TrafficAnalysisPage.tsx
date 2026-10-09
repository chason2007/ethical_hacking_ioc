import React, { useState } from 'react';
import { Network, Users, Server, Radio } from 'lucide-react';
import type { Capture } from '../types';
import { ProtocolsPage } from './ProtocolsPage';
import { ConversationsPage } from './ConversationsPage';
import { EndpointsPage } from './EndpointsPage';
import { PortsPage } from './PortsPage';

interface TrafficAnalysisPageProps {
  capture: Capture | null;
  initialSubTab?: 'protocols' | 'conversations' | 'endpoints' | 'ports';
}

export const TrafficAnalysisPage: React.FC<TrafficAnalysisPageProps> = ({
  capture,
  initialSubTab = 'protocols',
}) => {
  const [subTab, setSubTab] = useState<'protocols' | 'conversations' | 'endpoints' | 'ports'>(initialSubTab);

  const tabs = [
    { id: 'protocols', label: 'Protocols & DNS', icon: Network },
    { id: 'conversations', label: '5-Tuple Conversations', icon: Users },
    { id: 'endpoints', label: 'Host Endpoints', icon: Server },
    { id: 'ports', label: 'Ports & Services', icon: Radio },
  ] as const;

  return (
    <div className="space-y-4">
      {/* Streamlined Sub-Tab Navigation */}
      <div className="px-6 pt-5 max-w-7xl mx-auto flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <h2 className="text-lg font-bold text-slate-100">Traffic & Protocol Analysis</h2>
          <p className="text-xs text-slate-400">
            Inspect communication flows, active endpoints, service ports, and protocol hierarchies.
          </p>
        </div>

        <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-1 rounded-xl text-xs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = subTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setSubTab(tab.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
                  isActive
                    ? 'bg-cyan-600 text-slate-950 font-semibold shadow-xs'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon size={14} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Render Selected View */}
      <div>
        {subTab === 'protocols' && <ProtocolsPage capture={capture} />}
        {subTab === 'conversations' && <ConversationsPage capture={capture} />}
        {subTab === 'endpoints' && <EndpointsPage capture={capture} />}
        {subTab === 'ports' && <PortsPage capture={capture} />}
      </div>
    </div>
  );
};

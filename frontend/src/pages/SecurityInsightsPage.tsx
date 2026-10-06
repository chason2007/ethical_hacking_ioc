import React, { useEffect, useState } from 'react';
import {
  ShieldAlert, ShieldCheck, AlertTriangle, Info, AlertOctagon,
  CheckCircle2, HelpCircle
} from 'lucide-react';
import { api } from '../services/api';
import type { Capture, SecurityOverview, SecurityFinding } from '../types';
import { Badge } from '../components/common/Badge';

interface SecurityInsightsPageProps {
  capture: Capture | null;
}

export const SecurityInsightsPage: React.FC<SecurityInsightsPageProps> = ({ capture }) => {
  const [securityData, setSecurityData] = useState<SecurityOverview | null>(null);
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');

  useEffect(() => {
    if (!capture) return;
    const sev = selectedSeverity === 'ALL' ? undefined : selectedSeverity;

    api.getSecurity(capture.id, sev)
      .then((data: SecurityOverview) => setSecurityData(data))
      .catch((err: any) => console.error('Failed to load security insights:', err));
  }, [capture, selectedSeverity]);

  if (!capture) {
    return <div className="p-8 text-center text-slate-500">No capture selected.</div>;
  }

  const sevColors = {
    HIGH: {
      bg: 'bg-red-950/20 border-red-900/40',
      badge: 'high' as const,
      icon: AlertOctagon,
      iconColor: 'text-red-400',
    },
    MEDIUM: {
      bg: 'bg-amber-950/20 border-amber-900/40',
      badge: 'medium' as const,
      icon: AlertTriangle,
      iconColor: 'text-amber-400',
    },
    LOW: {
      bg: 'bg-blue-950/20 border-blue-900/40',
      badge: 'low' as const,
      icon: Info,
      iconColor: 'text-blue-400',
    },
    INFORMATIONAL: {
      bg: 'bg-slate-900/40 border-slate-800/60',
      badge: 'info' as const,
      icon: ShieldCheck,
      iconColor: 'text-slate-400',
    },
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldAlert size={20} className="text-amber-400" />
            Security Insights & Heuristic Anomaly Analysis
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Rule-based defensive inspection identifying port scanning patterns, SYN without ACK, DNS anomalies, and cleartext exposures.
          </p>
        </div>

        {/* Severity Filter Pills */}
        <div className="flex items-center bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs">
          {['ALL', 'HIGH', 'MEDIUM', 'LOW', 'INFORMATIONAL'].map((sev) => {
            const count =
              sev === 'ALL'
                ? securityData?.total_findings
                : (securityData?.severity_counts as any)?.[sev] ?? 0;

            return (
              <button
                key={sev}
                onClick={() => setSelectedSeverity(sev)}
                className={`px-3 py-1 rounded transition-colors flex items-center gap-1.5 cursor-pointer ${
                  selectedSeverity === sev
                    ? 'bg-cyan-600 text-slate-950 font-semibold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <span>{sev}</span>
                {count !== undefined && count > 0 && (
                  <span className={`text-[10px] font-mono px-1 rounded-full ${
                    selectedSeverity === sev ? 'bg-slate-950 text-cyan-300' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Heuristic Disclaimer Banner */}
      <div className="p-3.5 rounded-lg border border-slate-800 bg-slate-900/60 flex items-start gap-3 text-xs text-slate-400">
        <Info size={16} className="text-cyan-400 mt-0.5 shrink-0" />
        <div>
          <span className="font-semibold text-slate-200">Defensive Heuristic Analysis Methodology:</span>
          <span className="ml-1 text-slate-400">
            Observations reported below are statistical and rule-based heuristic indicators extracted from packet headers. They signal potential anomalies requiring security analyst verification, not deterministic evidence of compromise.
          </span>
        </div>
      </div>

      {/* Findings List */}
      <div className="space-y-4">
        {securityData?.findings.map((f: SecurityFinding, idx: number) => {
          const config = (sevColors as any)[f.severity] || sevColors.INFORMATIONAL;
          const Icon = config.icon;

          return (
            <div
              key={f.id || idx}
              className={`rounded-xl border p-5 space-y-4 transition-all ${config.bg}`}
            >
              {/* Finding Title & Badges */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg bg-slate-950/80 border border-slate-800 ${config.iconColor}`}>
                    <Icon size={18} />
                  </div>
                  <div>
                    <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                      {f.title}
                    </h3>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant={config.badge}>{f.severity}</Badge>
                      <Badge variant="protocol">{f.category}</Badge>
                      {f.source_ip && (
                        <span className="text-[11px] font-mono text-cyan-400">
                          Source: {f.source_ip}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {f.packets_involved && (
                  <div className="text-[11px] font-mono text-slate-400 bg-slate-950/60 border border-slate-800 px-2.5 py-1 rounded-md self-start sm:self-center">
                    {f.packets_involved}
                  </div>
                )}
              </div>

              {/* Finding Evidence */}
              <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800 font-mono text-xs text-slate-300">
                <span className="text-amber-400 font-semibold uppercase text-[10px] block mb-0.5">Observed Evidence:</span>
                {f.evidence}
              </div>

              {/* Rationale & Action Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                
                {/* Why It Matters */}
                <div className="p-3.5 rounded-lg bg-slate-900/60 border border-slate-800/80 space-y-1">
                  <div className="flex items-center gap-1.5 font-semibold text-cyan-400 text-xs">
                    <HelpCircle size={14} />
                    <span>Why It Matters (Threat Rationale)</span>
                  </div>
                  <p className="text-slate-300 leading-relaxed font-sans text-[11px] pt-1">
                    {f.why_it_matters}
                  </p>
                </div>

                {/* Recommendation */}
                <div className="p-3.5 rounded-lg bg-slate-900/60 border border-slate-800/80 space-y-1">
                  <div className="flex items-center gap-1.5 font-semibold text-emerald-400 text-xs">
                    <CheckCircle2 size={14} />
                    <span>Analyst Defensive Recommendation</span>
                  </div>
                  <p className="text-slate-300 leading-relaxed font-sans text-[11px] pt-1">
                    {f.recommendation}
                  </p>
                </div>

              </div>

            </div>
          );
        })}

        {securityData?.findings.length === 0 && (
          <div className="py-12 text-center text-slate-500 bg-slate-900/40 rounded-xl border border-slate-800">
            <ShieldCheck size={36} className="mx-auto mb-2 text-emerald-500" />
            <h4 className="text-sm font-semibold text-slate-300">No Anomalies Found in this Category</h4>
            <p className="text-xs text-slate-400 mt-1">Traffic matches normal operational baselines.</p>
          </div>
        )}
      </div>

    </div>
  );
};

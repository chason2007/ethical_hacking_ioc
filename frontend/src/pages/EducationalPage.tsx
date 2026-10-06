import React from 'react';
import { GraduationCap } from 'lucide-react';
import { Badge } from '../components/common/Badge';

export const EducationalPage: React.FC = () => {
  return (
    <div className="p-6 space-y-8 max-w-5xl mx-auto">
      
      {/* Header */}
      <div className="pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2 mb-1">
          <GraduationCap size={22} className="text-cyan-400" />
          <h1 className="text-xl font-bold text-slate-100">
            Network Protocol Analysis & Ethical Hacking Guide
          </h1>
        </div>
        <p className="text-xs text-slate-400">
          Academic reference companion for B.E./B.Tech Computer Science & Cybersecurity course viva, laboratory evaluations, and defensive traffic inspection.
        </p>
      </div>

      {/* Module 1: The TCP 3-Way Handshake */}
      <section className="space-y-4">
        <div className="flex items-center gap-2 text-sm font-bold text-slate-200">
          <span className="w-6 h-6 rounded-full bg-cyan-950 border border-cyan-800 text-cyan-400 flex items-center justify-center text-xs font-mono">1</span>
          <h3>TCP Three-Way Handshake & Session Teardown</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3 font-mono text-xs">
            <h4 className="text-cyan-400 font-semibold font-sans">Three-Way Handshake (Connection Establishment)</h4>
            <div className="space-y-2 text-slate-300">
              <div className="p-2 rounded bg-slate-950 border border-slate-800/80">
                <span className="text-cyan-400 font-bold">[Step 1] Client &rarr; Server: SYN</span>
                <p className="text-[11px] text-slate-400 font-sans mt-0.5">
                  Client transmits SYN flag with Initial Sequence Number (ISN_c). State changes to <code>SYN_SENT</code>.
                </p>
              </div>
              <div className="p-2 rounded bg-slate-950 border border-slate-800/80">
                <span className="text-blue-400 font-bold">[Step 2] Server &rarr; Client: SYN-ACK</span>
                <p className="text-[11px] text-slate-400 font-sans mt-0.5">
                  Server replies with SYN flag (ISN_s) and acknowledges client's ISN with ACK (ISN_c + 1). State: <code>SYN_RECEIVED</code>.
                </p>
              </div>
              <div className="p-2 rounded bg-slate-950 border border-slate-800/80">
                <span className="text-emerald-400 font-bold">[Step 3] Client &rarr; Server: ACK</span>
                <p className="text-[11px] text-slate-400 font-sans mt-0.5">
                  Client acknowledges server's ISN with ACK (ISN_s + 1). Connection enters <code>ESTABLISHED</code> state.
                </p>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3 font-mono text-xs">
            <h4 className="text-amber-400 font-semibold font-sans">Defensive Scan Signatures (Reconnaissance)</h4>
            <div className="space-y-2 text-slate-300">
              <div className="p-2 rounded bg-slate-950 border border-slate-800/80">
                <span className="text-red-400 font-bold">SYN Stealth Scan (Half-Open)</span>
                <p className="text-[11px] text-slate-400 font-sans mt-0.5">
                  Attacker sends SYN; if port is open, server responds with SYN-ACK. Attacker abruptly responds with RST instead of completing handshake, leaving fewer application-layer logs.
                </p>
              </div>
              <div className="p-2 rounded bg-slate-950 border border-slate-800/80">
                <span className="text-amber-400 font-bold">Closed Port Response: RST-ACK</span>
                <p className="text-[11px] text-slate-400 font-sans mt-0.5">
                  When a probe hits a port without an active listening socket, RFC 793 dictates the host respond with a TCP RST packet. A cluster of RSTs is a primary heuristic indicator of port sweeps.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Module 2: Protocol Layer Cheat Sheet */}
      <section className="space-y-4">
        <div className="flex items-center gap-2 text-sm font-bold text-slate-200">
          <span className="w-6 h-6 rounded-full bg-cyan-950 border border-cyan-800 text-cyan-400 flex items-center justify-center text-xs font-mono">2</span>
          <h3>Common Protocols in Defensive Network Forensics</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm text-cyan-400 font-mono">DNS (Port 53)</span>
              <Badge variant="protocol">UDP/TCP</Badge>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Translates domain names to IP addresses. Look for: TXT record abuse, Base64 chunks in queries (DNS Tunneling), or bursts of NXDOMAIN responses (DGA malware).
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm text-cyan-400 font-mono">HTTP vs HTTPS</span>
              <Badge variant="protocol">Port 80/443</Badge>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              HTTP port 80 is unencrypted (plain ASCII headers and cookies). HTTPS port 443 protects payload confidentiality with TLS. Forensic inspection in TLS focuses on ClientHello SNI and cert metadata.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm text-cyan-400 font-mono">ICMP</span>
              <Badge variant="protocol">Layer 3</Badge>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Diagnostic protocol. Type 8 (Echo Request) and Type 0 (Echo Reply) form ping. Sequential sweeps across consecutive IPs signal automated live host enumeration.
            </p>
          </div>
        </div>
      </section>

      {/* Module 3: Filter Query Reference */}
      <section className="space-y-4">
        <div className="flex items-center gap-2 text-sm font-bold text-slate-200">
          <span className="w-6 h-6 rounded-full bg-cyan-950 border border-cyan-800 text-cyan-400 flex items-center justify-center text-xs font-mono">3</span>
          <h3>NetProtocol Inspector Search & Filter Syntax</h3>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3 font-mono text-xs">
          <p className="text-slate-400 font-sans text-xs">
            Use the top search bar in Packet Explorer to execute fast targeted queries:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
              <span className="text-cyan-400 font-bold">protocol:tcp</span>
              <p className="text-[11px] text-slate-500 font-sans mt-0.5">Filters packets belonging to TCP protocol</p>
            </div>
            <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
              <span className="text-cyan-400 font-bold">port:443</span>
              <p className="text-[11px] text-slate-500 font-sans mt-0.5">Filters flows involving destination or source port 443</p>
            </div>
            <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
              <span className="text-cyan-400 font-bold">src:192.168.1.50</span>
              <p className="text-[11px] text-slate-500 font-sans mt-0.5">Filters packets originating from specified source IP</p>
            </div>
            <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
              <span className="text-cyan-400 font-bold">SYN</span>
              <p className="text-[11px] text-slate-500 font-sans mt-0.5">Full-text search for packets containing SYN flag</p>
            </div>
          </div>
        </div>
      </section>

      {/* Viva / Evaluation Questions */}
      <section className="space-y-4">
        <div className="flex items-center gap-2 text-sm font-bold text-slate-200">
          <span className="w-6 h-6 rounded-full bg-cyan-950 border border-cyan-800 text-cyan-400 flex items-center justify-center text-xs font-mono">4</span>
          <h3>Sample Course Viva Questions & Model Answers</h3>
        </div>

        <div className="space-y-3 text-xs">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
            <h4 className="font-semibold text-slate-200 font-sans">
              Q1: What differentiates a TCP SYN scan from a TCP Connect scan?
            </h4>
            <p className="text-slate-400 leading-relaxed font-sans">
              <strong>Answer:</strong> A TCP Connect scan utilizes the operating system's standard <code>connect()</code> system call to complete the entire 3-way handshake (SYN &rarr; SYN-ACK &rarr; ACK), which creates an established socket recorded in application access logs. A SYN scan (half-open) transmits a SYN, awaits the SYN-ACK to verify the port is listening, but sends a RST immediately to tear down the half-open connection before an application socket is established.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1.5">
            <h4 className="font-semibold text-slate-200 font-sans">
              Q2: How does TTL (Time to Live) assist in network packet forensics?
            </h4>
            <p className="text-slate-400 leading-relaxed font-sans">
              <strong>Answer:</strong> Every router hop decrements the IPv4 TTL field by 1. Operating systems initiate TTLs with standard default base values (e.g. Linux = 64, Windows = 128, Cisco IOS = 255). By inspecting the arrival TTL, analysts can estimate the distance (hop count) and infer the operating system family of the remote sender.
            </p>
          </div>
        </div>
      </section>

    </div>
  );
};

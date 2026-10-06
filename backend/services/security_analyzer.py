from collections import defaultdict
from typing import List, Dict, Any, Optional
from backend.services.pcap_parser import ParsedPacketData

class SecurityAnalyzer:
    @staticmethod
    def analyze(packets: List[ParsedPacketData], capture_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Runs defensive, heuristic, rule-based network security analysis on parsed packets.
        Generates structured findings with findings, severity, evidence, 'Why It Matters', and recommendations.
        """
        findings: List[Dict[str, Any]] = []
        if not packets:
            return findings

        total_packets = len(packets)
        duration = max(capture_summary.get("duration_seconds", 1.0), 1.0)

        # -------------------------------------------------------------
        # Data structures for tracking behaviors
        # -------------------------------------------------------------
        # Source IP -> Set of destination ports contacted
        src_to_dst_ports = defaultdict(set)
        src_to_dst_hosts = defaultdict(set)
        src_to_packets = defaultdict(list)
        
        # TCP SYN and ACK tracking
        src_syn_packets = defaultdict(list)
        src_ack_packets = defaultdict(list)
        rst_packets = []
        
        # DNS tracking
        dns_queries = []
        dns_nxdomain = []
        long_domains = []
        
        # ICMP tracking
        src_icmp_requests = defaultdict(set)
        icmp_packets = []
        
        # Broadcast tracking
        broadcast_multicast_count = 0
        
        # Cleartext protocol tracking
        plaintext_packets = defaultdict(list)

        # Oversized packets (> 1514)
        oversized_packets = []

        # Analyze each packet
        for pkt in packets:
            src = pkt.source_ip
            dst = pkt.destination_ip
            proto = pkt.protocol
            dport = pkt.destination_port
            sport = pkt.source_port

            # Broadcast / Multicast MAC check
            if pkt.destination_mac:
                dst_mac_clean = pkt.destination_mac.lower()
                if dst_mac_clean in ("ff:ff:ff:ff:ff:ff", "01:00:5e:", "33:33:"):
                    broadcast_multicast_count += 1
                elif dst and (dst.endswith(".255") or dst.startswith("224.") or dst.startswith("ff")):
                    broadcast_multicast_count += 1

            # MTU / Jumbo frame check
            if pkt.length > 1514:
                oversized_packets.append(pkt)

            # Source port and destination port mapping for probes (SYN or request)
            if src and dport:
                if proto == "TCP" and pkt.tcp_flags and "SYN" in pkt.tcp_flags and "ACK" not in pkt.tcp_flags:
                    src_to_dst_ports[src].add(dport)
                    src_to_packets[src].append(pkt.packet_number)
                elif proto == "UDP":
                    src_to_dst_ports[src].add(dport)
                    src_to_packets[src].append(pkt.packet_number)
            if src and dst:
                src_to_dst_hosts[src].add(dst)

            # TCP Flag tracking
            if proto in ("TCP", "TLS") and pkt.tcp_flags:
                flags = pkt.tcp_flags
                if "SYN" in flags and "ACK" not in flags:
                    src_syn_packets[src].append(pkt)
                if "ACK" in flags:
                    src_ack_packets[src].append(pkt)
                if "RST" in flags:
                    rst_packets.append(pkt)

            # Plaintext protocols
            if dport in (21, 23) or (dport == 80 and proto == "HTTP"):
                plaintext_packets[dport].append(pkt)

            # ICMP tracking
            if "ICMP" in proto:
                icmp_packets.append(pkt)
                if "Echo Request" in pkt.info and src and dst:
                    src_icmp_requests[src].add(dst)

            # DNS tracking
            if pkt.dns_record:
                rec = pkt.dns_record
                if rec.get("record_type") == "QUERY":
                    dns_queries.append(pkt)
                    qname = rec.get("query_name", "")
                    if len(qname) >= 42 or (qname.count(".") > 4 and len(qname) > 30):
                        long_domains.append((pkt, qname))
                if rec.get("rcode") == "NXDOMAIN":
                    dns_nxdomain.append(pkt)

        # -------------------------------------------------------------
        # RULE 1: Possible Port Scanning (Horizontal / Vertical Scan)
        # -------------------------------------------------------------
        for src, dports in src_to_dst_ports.items():
            if len(dports) >= 12:
                pkts_sample = src_to_packets[src][:8]
                pkt_nums_str = ", ".join(f"#{num}" for num in pkts_sample) + (f" (+{len(src_to_packets[src])-8} more)" if len(src_to_packets[src]) > 8 else "")
                severity = "HIGH" if len(dports) >= 25 else "MEDIUM"
                findings.append({
                    "title": "Potential Port Scanning Activity Detected",
                    "severity": severity,
                    "category": "PORT_SCAN",
                    "evidence": f"Host {src} initiated connections to {len(dports)} distinct destination ports within {duration:.1f}s.",
                    "packets_involved": f"Packets: {pkt_nums_str}",
                    "packet_count": len(src_to_packets[src]),
                    "why_it_matters": (
                        "Rapid connection attempts across a broad spectrum of port numbers typically indicate "
                        "automated port enumeration (such as Nmap, Masscan) attempting to discover open network services "
                        "and map attack surface."
                    ),
                    "recommendation": (
                        f"Investigate the origin of host {src}. Verify whether this IP corresponds to an authorized vulnerability scanner. "
                        "If unauthorized, isolate the host and evaluate firewall egress/ingress filtering rules."
                    ),
                    "source_ip": src,
                    "destination_ip": None,
                })

        # -------------------------------------------------------------
        # RULE 2: Possible SYN Scan Pattern (Half-Open Scan)
        # -------------------------------------------------------------
        for src, syn_list in src_syn_packets.items():
            if len(syn_list) >= 8:
                ack_count = len(src_ack_packets.get(src, []))
                # If high SYN with very few ACK, likely half-open scan
                if ack_count <= max(2, len(syn_list) * 0.2):
                    syn_pkt_nums = ", ".join(f"#{p.packet_number}" for p in syn_list[:6])
                    findings.append({
                        "title": "Potential TCP SYN Stealth Scan Pattern",
                        "severity": "HIGH",
                        "category": "SYN_SCAN",
                        "evidence": f"Source {src} generated {len(syn_list)} TCP SYN packets with only {ack_count} completed ACK handshakes.",
                        "packets_involved": f"Packets: {syn_pkt_nums} (+{len(syn_list)-6} more)",
                        "packet_count": len(syn_list),
                        "why_it_matters": (
                            "In standard TCP communication, a SYN is followed by SYN-ACK and an ACK completing the three-way handshake. "
                            "A disproportionately high volume of orphaned SYN packets is a classic signature of TCP half-open (SYN) scanning, "
                            "designed to determine port availability without establishing a full application socket."
                        ),
                        "recommendation": (
                            f"Inspect traffic from {src}. Configure SYN flood protection / SYN cookies on edge gateways "
                            "and enforce rate limiting for incomplete TCP handshakes."
                        ),
                        "source_ip": src,
                        "destination_ip": None,
                    })

        # -------------------------------------------------------------
        # RULE 3: TCP Reset (RST) Anomaly
        # -------------------------------------------------------------
        if len(rst_packets) >= 10:
            tcp_total = len([p for p in packets if p.protocol in ("TCP", "TLS")])
            rst_ratio = (len(rst_packets) / tcp_total) * 100 if tcp_total > 0 else 0
            if rst_ratio > 15.0 or len(rst_packets) >= 20:
                sample_rst = ", ".join(f"#{p.packet_number}" for p in rst_packets[:6])
                findings.append({
                    "title": "Elevated TCP RST (Reset) Frequency Anomaly",
                    "severity": "MEDIUM",
                    "category": "RST_ANOMALY",
                    "evidence": f"Observed {len(rst_packets)} TCP RST packets, accounting for {rst_ratio:.1f}% of all TCP traffic in this capture.",
                    "packets_involved": f"Packets: {sample_rst}",
                    "packet_count": len(rst_packets),
                    "why_it_matters": (
                        "TCP RST packets forcefully tear down a TCP connection. A high volume of RST packets is commonly observed "
                        "when hosts respond with RST to probes directed at closed ports, or when an in-line firewall/IDS injects TCP resets "
                        "to terminate policy-violating connections."
                    ),
                    "recommendation": (
                        "Determine if internal hosts are rejecting inbound scans on unassigned ports, or if a stateful firewall is rejecting "
                        "asymmetric or out-of-order packets. Correlate with port-scan indicators."
                    ),
                    "source_ip": rst_packets[0].source_ip if rst_packets else None,
                    "destination_ip": None,
                })

        # -------------------------------------------------------------
        # RULE 4: DNS Anomaly - Long Hostnames (Potential Tunneling/DGA)
        # -------------------------------------------------------------
        if long_domains:
            sample_long = long_domains[0]
            pkt_nums = ", ".join(f"#{p[0].packet_number}" for p in long_domains[:5])
            findings.append({
                "title": "Suspicious Long DNS Query (Potential Tunneling / DGA)",
                "severity": "MEDIUM",
                "category": "DNS_ANOMALY",
                "evidence": f"Detected {len(long_domains)} DNS queries with unusually long domain names. Example: '{sample_long[1][:60]}...'",
                "packets_involved": f"Packets: {pkt_nums}",
                "packet_count": len(long_domains),
                "why_it_matters": (
                    "Standard internet domain names are typically concise. Extremely long subdomains with high character entropy "
                    "are frequently associated with DNS tunneling (data exfiltration/C2 channeling over DNS TXT/A queries) or "
                    "Domain Generation Algorithms (DGA) used by modular malware."
                ),
                "recommendation": (
                    "Inspect the queried domain's entropy score and parent domain registrar. Verify whether legitimate software "
                    "uses this naming scheme, and implement DNS response policy inspection or DNS filtering."
                ),
                "source_ip": sample_long[0].source_ip,
                "destination_ip": sample_long[0].destination_ip,
            })

        # -------------------------------------------------------------
        # RULE 5: DNS Anomaly - High NXDOMAIN Error Rate
        # -------------------------------------------------------------
        if len(dns_nxdomain) >= 6:
            nx_samples = ", ".join(f"#{p.packet_number}" for p in dns_nxdomain[:5])
            findings.append({
                "title": "Elevated DNS NXDOMAIN Response Burst",
                "severity": "LOW",
                "category": "DNS_ANOMALY",
                "evidence": f"Received {len(dns_nxdomain)} NXDOMAIN (Non-Existent Domain) responses from upstream DNS resolvers.",
                "packets_involved": f"Packets: {nx_samples}",
                "packet_count": len(dns_nxdomain),
                "why_it_matters": (
                    "While occasional NXDOMAIN responses occur due to typing errors, clusters of NXDOMAIN responses suggest "
                    "endpoint misconfiguration, aggressive internal discovery, or malware attempting to contact algorithmically generated "
                    "command-and-control domains that have not yet been registered."
                ),
                "recommendation": (
                    "Identify the client IP requesting the unresolved domains and review endpoint process execution logs around the timestamp."
                ),
                "source_ip": dns_nxdomain[0].source_ip if dns_nxdomain else None,
                "destination_ip": None,
            })

        # -------------------------------------------------------------
        # RULE 6: ICMP Sweeping / High Volume Anomaly
        # -------------------------------------------------------------
        for src, target_hosts in src_icmp_requests.items():
            if len(target_hosts) >= 8:
                findings.append({
                    "title": "Potential ICMP Host Reconnaissance (Ping Sweep)",
                    "severity": "MEDIUM",
                    "category": "ICMP_ANOMALY",
                    "evidence": f"Host {src} dispatched ICMP Echo Requests targeting {len(target_hosts)} unique IP endpoints.",
                    "packets_involved": f"Targets: {', '.join(list(target_hosts)[:5])}...",
                    "packet_count": len(target_hosts),
                    "why_it_matters": (
                        "Sequential or broadcast ICMP Echo Requests are used during the discovery phase of a security assessment "
                        "or network reconnaissance to map live hosts across a subnet prior to port scanning."
                    ),
                    "recommendation": (
                        f"Verify if host {src} has administrative approval to run network discovery tools. "
                        "Enforce edge switch port security and restrict ICMP Echo forwarding between internal security zones."
                    ),
                    "source_ip": src,
                    "destination_ip": None,
                })
                break

        # -------------------------------------------------------------
        # RULE 7: Cleartext Protocol Usage (Plaintext Insecurity)
        # -------------------------------------------------------------
        if 21 in plaintext_packets or 23 in plaintext_packets:
            pts = []
            if 21 in plaintext_packets: pts.append("FTP (port 21)")
            if 23 in plaintext_packets: pts.append("Telnet (port 23)")
            proto_str = " & ".join(pts)
            findings.append({
                "title": f"Insecure Cleartext Protocol Transmission ({proto_str})",
                "severity": "MEDIUM",
                "category": "PLAIN_CREDENTIALS",
                "evidence": f"Detected unencrypted {proto_str} communication across {len(plaintext_packets.get(21, []) + plaintext_packets.get(23, []))} packets.",
                "packets_involved": "Cleartext session packets",
                "packet_count": len(plaintext_packets.get(21, []) + plaintext_packets.get(23, [])),
                "why_it_matters": (
                    "Legacy protocols such as Telnet and standard FTP transmit authentication credentials and session payloads "
                    "in raw ASCII text, making them completely susceptible to packet eavesdropping, session hijacking, and MITM attacks."
                ),
                "recommendation": (
                    "Decommission Telnet and unencrypted FTP immediately. Migrate administrative access to SSH (port 22) "
                    "and file transfers to SFTP or FTPS with modern ciphers."
                ),
                "source_ip": None,
                "destination_ip": None,
            })
        elif 80 in plaintext_packets and len(plaintext_packets[80]) >= 4:
            findings.append({
                "title": "Cleartext HTTP Traffic Observed (Non-TLS)",
                "severity": "LOW",
                "category": "HTTP_INDICATOR",
                "evidence": f"Detected {len(plaintext_packets[80])} packets communicating over standard unencrypted HTTP (TCP port 80).",
                "packets_involved": f"Packets: {', '.join(f'#{p.packet_number}' for p in plaintext_packets[80][:4])}",
                "packet_count": len(plaintext_packets[80]),
                "why_it_matters": (
                    "Standard HTTP does not encrypt session headers, cookies, or payloads. While common for non-sensitive public downloads, "
                    "any web session transferring session tokens or user parameters over HTTP is vulnerable to tampering and snooping."
                ),
                "recommendation": (
                    "Configure web servers to redirect HTTP traffic to HTTPS (port 443) with HTTP Strict Transport Security (HSTS) headers enabled."
                ),
                "source_ip": plaintext_packets[80][0].source_ip,
                "destination_ip": plaintext_packets[80][0].destination_ip,
            })

        # -------------------------------------------------------------
        # RULE 8: Broadcast / Multicast Ratio Anomaly
        # -------------------------------------------------------------
        if total_packets > 30 and (broadcast_multicast_count / total_packets) > 0.35:
            pct = (broadcast_multicast_count / total_packets) * 100
            findings.append({
                "title": "Elevated Broadcast / Multicast Ratio",
                "severity": "LOW",
                "category": "BROADCAST_STORM",
                "evidence": f"Broadcast and multicast frames account for {pct:.1f}% ({broadcast_multicast_count}/{total_packets}) of the capture.",
                "packets_involved": f"{broadcast_multicast_count} broadcast/multicast packets",
                "packet_count": broadcast_multicast_count,
                "why_it_matters": (
                    "High concentrations of broadcast traffic degrade network switch switching fabric and force connected endpoints "
                    "to process unnecessary interrupts. It can indicate ARP storming, layer 2 looping, or chatty discovery protocols (LLMNR, mDNS)."
                ),
                "recommendation": (
                    "Audit VLAN segmentation, enable broadcast storm control on managed switches, and disable unnecessary discovery daemons."
                ),
                "source_ip": None,
                "destination_ip": None,
            })

        # -------------------------------------------------------------
        # RULE 9: Large Packet / MTU Outlier
        # -------------------------------------------------------------
        if oversized_packets:
            max_len = max(p.length for p in oversized_packets)
            findings.append({
                "title": "Oversized Frame / Jumbo Packet Observation",
                "severity": "INFORMATIONAL",
                "category": "LARGE_PACKET",
                "evidence": f"Observed {len(oversized_packets)} packets exceeding standard Ethernet MTU (1514 bytes), maximum observed length: {max_len} bytes.",
                "packets_involved": f"Packets: {', '.join(f'#{p.packet_number}' for p in oversized_packets[:4])}",
                "packet_count": len(oversized_packets),
                "why_it_matters": (
                    "Standard Ethernet MTU is 1500 bytes (1514 bytes with Ethernet header). Frames exceeding this length signify Jumbo Frame support "
                    "or Large Send Offload (LSO) / TCP Segmentation Offload (TSO) enabled on the capturing network interface."
                ),
                "recommendation": (
                    "Informational only. If Jumbo Frames are unintentional, ensure end-to-end MTU uniformity to prevent MTU black holes or fragmentation drops."
                ),
                "source_ip": oversized_packets[0].source_ip,
                "destination_ip": oversized_packets[0].destination_ip,
            })

        # Default Informational finding if no anomalies are detected
        if not findings:
            findings.append({
                "title": "Baseline Protocol Inspection - No High-Risk Anomalies Detected",
                "severity": "INFORMATIONAL",
                "category": "INFORMATIONAL",
                "evidence": f"Analyzed {total_packets} packets across {duration:.1f}s. Protocol distribution appears consistent with standard baseline activity.",
                "packets_involved": f"All {total_packets} packets",
                "packet_count": total_packets,
                "why_it_matters": (
                    "Routine packet capture inspection helps establish an accurate baseline of network behavior and protocol distributions."
                ),
                "recommendation": (
                    "Continue continuous baseline monitoring to detect deviations in protocol volumes and connection patterns."
                ),
                "source_ip": None,
                "destination_ip": None,
            })

        return findings

import math
from collections import defaultdict
from typing import List, Dict, Any, Tuple
from backend.services.pcap_parser import ParsedPacketData, is_ip_private, COMMON_PORTS

class AnalysisEngine:
    @staticmethod
    def analyze_capture(packets: List[ParsedPacketData], total_bytes: int, duration: float) -> Dict[str, Any]:
        """
        Runs comprehensive analytical processing on parsed packets.
        Returns endpoints, conversations, protocol stats, port stats, and timeline points.
        """
        if not packets:
            return {
                "endpoints": [],
                "conversations": [],
                "protocol_stats": [],
                "port_stats": [],
                "timeline": [],
                "statistics": {},
            }

        total_packet_count = len(packets)
        
        # 1. Endpoints aggregation
        endpoints_dict = defaultdict(lambda: {
            "packets_sent": 0, "packets_received": 0,
            "bytes_sent": 0, "bytes_received": 0,
            "address_type": "IPv4", "is_private": False,
        })

        # 2. Conversations aggregation
        # Key: (min(addrA, addrB), max(addrA, addrB), protocol, min(portA, portB), max(portA, portB))
        conversations_dict = defaultdict(lambda: {
            "packets_a_to_b": 0, "packets_b_to_a": 0,
            "bytes_a_to_b": 0, "bytes_b_to_a": 0,
            "start_time": float("inf"), "end_time": float("-inf"),
            "port_a": None, "port_b": None,
            "proto": "",
        })

        # 3. Protocol breakdown
        protocol_counts = defaultdict(int)
        protocol_bytes = defaultdict(int)

        # 4. Port analysis
        port_counts = defaultdict(lambda: {"packets": 0, "bytes": 0, "protocol": set()})

        # 5. Packet size buckets
        size_buckets = {
            "<64 bytes": 0,
            "64-128 bytes": 0,
            "129-512 bytes": 0,
            "513-1024 bytes": 0,
            "1025-1518 bytes": 0,
            ">1518 bytes": 0,
        }

        # 6. Timeline binning setup
        start_ts = packets[0].timestamp
        end_ts = packets[-1].timestamp
        span = max(end_ts - start_ts, 1.0)
        num_bins = min(max(int(span), 10), 60)
        bin_size = span / num_bins

        timeline_bins = [
            {
                "timestamp": round(start_ts + i * bin_size, 2),
                "time_label": f"{round(i * bin_size, 1)}s",
                "packet_count": 0,
                "byte_count": 0,
                "tcp_count": 0,
                "udp_count": 0,
                "icmp_count": 0,
                "dns_count": 0,
                "http_count": 0,
            }
            for i in range(num_bins)
        ]

        # Iterate over packets
        for pkt in packets:
            # Protocol stats
            proto = pkt.protocol
            protocol_counts[proto] += 1
            protocol_bytes[proto] += pkt.length

            # Size bucket
            if pkt.length < 64:
                size_buckets["<64 bytes"] += 1
            elif pkt.length <= 128:
                size_buckets["64-128 bytes"] += 1
            elif pkt.length <= 512:
                size_buckets["129-512 bytes"] += 1
            elif pkt.length <= 1024:
                size_buckets["513-1024 bytes"] += 1
            elif pkt.length <= 1518:
                size_buckets["1025-1518 bytes"] += 1
            else:
                size_buckets[">1518 bytes"] += 1

            # Timeline bin
            bin_idx = min(int((pkt.timestamp - start_ts) / bin_size), num_bins - 1)
            b = timeline_bins[bin_idx]
            b["packet_count"] += 1
            b["byte_count"] += pkt.length
            if proto in ("TCP", "TLS"):
                b["tcp_count"] += 1
            elif proto == "UDP":
                b["udp_count"] += 1
            elif "ICMP" in proto:
                b["icmp_count"] += 1
            if proto == "DNS" or pkt.dns_record:
                b["dns_count"] += 1
            if proto == "HTTP" or pkt.http_record:
                b["http_count"] += 1

            # Endpoints
            src = pkt.source_ip
            dst = pkt.destination_ip
            if src:
                ep_src = endpoints_dict[src]
                ep_src["packets_sent"] += 1
                ep_src["bytes_sent"] += pkt.length
                ep_src["address_type"] = "IPv6" if ":" in src else "IPv4"
                ep_src["is_private"] = is_ip_private(src)
            if dst:
                ep_dst = endpoints_dict[dst]
                ep_dst["packets_received"] += 1
                ep_dst["bytes_received"] += pkt.length
                ep_dst["address_type"] = "IPv6" if ":" in dst else "IPv4"
                ep_dst["is_private"] = is_ip_private(dst)

            # Ports
            sport = pkt.source_port
            dport = pkt.destination_port
            if sport:
                port_counts[sport]["packets"] += 1
                port_counts[sport]["bytes"] += pkt.length
                port_counts[sport]["protocol"].add(proto)
            if dport:
                port_counts[dport]["packets"] += 1
                port_counts[dport]["bytes"] += pkt.length
                port_counts[dport]["protocol"].add(proto)

            # Conversation
            if src and dst:
                # Canonical pair
                if src <= dst:
                    pair_key = (src, dst, proto, sport or 0, dport or 0)
                    is_a_to_b = True
                else:
                    pair_key = (dst, src, proto, dport or 0, sport or 0)
                    is_a_to_b = False

                conv = conversations_dict[pair_key]
                conv["proto"] = proto
                conv["port_a"] = pair_key[3] if pair_key[3] != 0 else None
                conv["port_b"] = pair_key[4] if pair_key[4] != 0 else None
                conv["start_time"] = min(conv["start_time"], pkt.timestamp)
                conv["end_time"] = max(conv["end_time"], pkt.timestamp)

                if is_a_to_b:
                    conv["packets_a_to_b"] += 1
                    conv["bytes_a_to_b"] += pkt.length
                else:
                    conv["packets_b_to_a"] += 1
                    conv["bytes_b_to_a"] += pkt.length

        # Finalize Endpoints list
        endpoints_list = []
        for addr, edata in endpoints_dict.items():
            tot_p = edata["packets_sent"] + edata["packets_received"]
            tot_b = edata["bytes_sent"] + edata["bytes_received"]
            endpoints_list.append({
                "address": addr,
                "address_type": edata["address_type"],
                "packets_sent": edata["packets_sent"],
                "packets_received": edata["packets_received"],
                "bytes_sent": edata["bytes_sent"],
                "bytes_received": edata["bytes_received"],
                "total_packets": tot_p,
                "total_bytes": tot_b,
                "is_private": edata["is_private"],
                "hostname": None,
            })
        endpoints_list.sort(key=lambda x: x["total_packets"], reverse=True)

        # Finalize Conversations list
        conversations_list = []
        for pair_key, cdata in conversations_dict.items():
            tot_p = cdata["packets_a_to_b"] + cdata["packets_b_to_a"]
            tot_b = cdata["bytes_a_to_b"] + cdata["bytes_b_to_a"]
            dur = max(cdata["end_time"] - cdata["start_time"], 0.0)
            conversations_list.append({
                "protocol": cdata["proto"],
                "endpoint_a": pair_key[0],
                "endpoint_b": pair_key[1],
                "port_a": cdata["port_a"],
                "port_b": cdata["port_b"],
                "packets_a_to_b": cdata["packets_a_to_b"],
                "packets_b_to_a": cdata["packets_b_to_a"],
                "bytes_a_to_b": cdata["bytes_a_to_b"],
                "bytes_b_to_a": cdata["bytes_b_to_a"],
                "total_packets": tot_p,
                "total_bytes": tot_b,
                "start_time": cdata["start_time"],
                "end_time": cdata["end_time"],
                "duration": round(dur, 4),
            })
        conversations_list.sort(key=lambda x: x["total_packets"], reverse=True)

        # Finalize Protocol stats
        protocol_stats_list = []
        for proto_name, pcount in protocol_counts.items():
            pbytes = protocol_bytes[proto_name]
            pct = round((pcount / total_packet_count) * 100, 2) if total_packet_count > 0 else 0.0
            layer = "Application" if proto_name in ("DNS", "HTTP", "TLS", "DHCP") else "Transport" if proto_name in ("TCP", "UDP") else "Network" if proto_name in ("IPv4", "IPv6", "ICMP", "ARP") else "Link"
            protocol_stats_list.append({
                "protocol_name": proto_name,
                "layer": layer,
                "packet_count": pcount,
                "byte_count": pbytes,
                "percentage": pct,
            })
        protocol_stats_list.sort(key=lambda x: x["packet_count"], reverse=True)

        # Finalize Port stats
        port_stats_list = []
        for port_num, pdata in port_counts.items():
            svc = COMMON_PORTS.get(port_num, "Unassigned / Custom Service")
            desc = f"Commonly associated with {svc}" if port_num in COMMON_PORTS else "Dynamic / Private / Unregistered port"
            port_stats_list.append({
                "port": port_num,
                "protocol": "/".join(sorted(pdata["protocol"])) or "TCP/UDP",
                "packet_count": pdata["packets"],
                "byte_count": pdata["bytes"],
                "common_service": svc,
                "description": desc,
            })
        port_stats_list.sort(key=lambda x: x["packet_count"], reverse=True)

        # Summary statistics
        tcp_p = sum(p["packet_count"] for p in protocol_stats_list if p["protocol_name"] in ("TCP", "TLS"))
        udp_p = sum(p["packet_count"] for p in protocol_stats_list if p["protocol_name"] in ("UDP", "DNS"))
        icmp_p = sum(p["packet_count"] for p in protocol_stats_list if "ICMP" in p["protocol_name"])
        other_p = total_packet_count - (tcp_p + udp_p + icmp_p)

        stats_summary = {
            "total_packets": total_packet_count,
            "total_bytes": total_bytes,
            "duration_seconds": duration,
            "unique_ips": len(endpoints_list),
            "unique_conversations": len(conversations_list),
            "protocol_count": len(protocol_stats_list),
            "findings_count": 0,  # to be updated after security analysis
            "avg_packet_size": round(total_bytes / total_packet_count, 1) if total_packet_count > 0 else 0,
            "tcp_packet_count": tcp_p,
            "udp_packet_count": udp_p,
            "icmp_packet_count": icmp_p,
            "other_packet_count": max(other_p, 0),
            "packet_size_buckets": size_buckets,
        }

        return {
            "endpoints": endpoints_list,
            "conversations": conversations_list,
            "protocol_stats": protocol_stats_list,
            "port_stats": port_stats_list[:100],  # top 100 ports
            "timeline": timeline_bins,
            "statistics": stats_summary,
        }

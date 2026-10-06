import os
import json
import socket
import ipaddress
from typing import Dict, List, Any, Tuple, Optional
from scapy.all import rdpcap, PcapReader, Packet as ScapyPacket
from scapy.layers.l2 import Ether, ARP
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.inet6 import IPv6, ICMPv6EchoRequest, ICMPv6EchoReply
from scapy.layers.dns import DNS, DNSQR, DNSRR
# TLS parsing is done via robust byte header extraction below to support all Python/Scapy environments
TLS = None
TLSClientHello = None
TLSServerHello = None

COMMON_PORTS = {
    20: "FTP-Data",
    21: "FTP-Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    67: "DHCP-Server",
    68: "DHCP-Client",
    69: "TFTP",
    80: "HTTP",
    110: "POP3",
    123: "NTP",
    143: "IMAP",
    161: "SNMP",
    194: "IRC",
    389: "LDAP",
    443: "HTTPS",
    445: "SMB",
    465: "SMTPS",
    587: "SMTP-Submission",
    993: "IMAPS",
    995: "POP3S",
    1433: "MSSQL",
    1521: "Oracle-DB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    8080: "HTTP-Proxy/Alt",
    8443: "HTTPS-Alt",
}

def is_ip_private(ip_str: str) -> bool:
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        return ip_obj.is_private
    except ValueError:
        return False

def parse_tcp_flags(flags_val) -> str:
    if flags_val is None:
        return ""
    flag_str = str(flags_val)
    # Scapy flags representation
    flag_names = []
    if "F" in flag_str: flag_names.append("FIN")
    if "S" in flag_str: flag_names.append("SYN")
    if "R" in flag_str: flag_names.append("RST")
    if "P" in flag_str: flag_names.append("PSH")
    if "A" in flag_str: flag_names.append("ACK")
    if "U" in flag_str: flag_names.append("URG")
    if "E" in flag_str: flag_names.append("ECE")
    if "C" in flag_str: flag_names.append("CWR")
    return "-".join(flag_names) if flag_names else flag_str

def format_hex_preview(raw_bytes: bytes, max_len: int = 128) -> str:
    if not raw_bytes:
        return ""
    snippet = raw_bytes[:max_len]
    hex_part = snippet.hex(" ")
    ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in snippet)
    return f"{hex_part}\n| {ascii_part}"

class ParsedPacketData:
    def __init__(self):
        self.packet_number: int = 0
        self.timestamp: float = 0.0
        self.relative_time: float = 0.0
        self.length: int = 0
        self.source_mac: Optional[str] = None
        self.destination_mac: Optional[str] = None
        self.eth_type: Optional[str] = None
        self.ip_version: Optional[int] = None
        self.source_ip: Optional[str] = None
        self.destination_ip: Optional[str] = None
        self.ip_ttl: Optional[int] = None
        self.ip_id: Optional[int] = None
        self.protocol: str = "Unknown"
        self.source_port: Optional[int] = None
        self.destination_port: Optional[int] = None
        self.tcp_flags: Optional[str] = None
        self.tcp_seq: Optional[int] = None
        self.tcp_ack: Optional[int] = None
        self.tcp_window: Optional[int] = None
        self.info: str = ""
        self.layers_json: str = "{}"
        self.payload_preview: Optional[str] = None
        
        # DNS specific
        self.dns_record: Optional[Dict[str, Any]] = None
        
        # HTTP specific
        self.http_record: Optional[Dict[str, Any]] = None

def parse_single_packet(pkt: ScapyPacket, pkt_num: int, base_time: float) -> ParsedPacketData:
    data = ParsedPacketData()
    data.packet_number = pkt_num
    data.timestamp = float(pkt.time)
    data.relative_time = round(data.timestamp - base_time, 6)
    data.length = len(pkt)
    
    layers_tree = []
    
    # Layer 1: Frame
    frame_fields = {
        "Packet Number": pkt_num,
        "Timestamp": data.timestamp,
        "Relative Time (s)": f"{data.relative_time:.6f}",
        "Frame Length (bytes)": data.length,
    }
    layers_tree.append({"layer": "Frame", "summary": f"Frame {pkt_num}: {data.length} bytes on wire", "fields": frame_fields})
    
    # Layer 2: Ethernet / ARP
    if pkt.haslayer(Ether):
        eth = pkt[Ether]
        data.source_mac = eth.src
        data.destination_mac = eth.dst
        data.eth_type = f"0x{eth.type:04x}"
        eth_fields = {
            "Source MAC": eth.src,
            "Destination MAC": eth.dst,
            "Type": f"0x{eth.type:04x} ({eth.sprintf('%Ether.type%')})",
        }
        layers_tree.append({"layer": "Ethernet", "summary": f"Ethernet II, Src: {eth.src}, Dst: {eth.dst}", "fields": eth_fields})
    
    if pkt.haslayer(ARP):
        arp = pkt[ARP]
        data.protocol = "ARP"
        data.source_ip = arp.psrc
        data.destination_ip = arp.pdst
        arp_op = "Request" if arp.op == 1 else "Reply" if arp.op == 2 else str(arp.op)
        data.info = f"ARP {arp_op} who-has {arp.pdst} tell {arp.psrc}" if arp.op == 1 else f"ARP {arp_op} {arp.psrc} is-at {arp.hwsrc}"
        arp_fields = {
            "Hardware type": arp.hwtype,
            "Protocol type": f"0x{arp.ptype:04x}",
            "Operation": f"{arp_op} ({arp.op})",
            "Sender MAC": arp.hwsrc,
            "Sender IP": arp.psrc,
            "Target MAC": arp.hwdst,
            "Target IP": arp.pdst,
        }
        layers_tree.append({"layer": "ARP", "summary": f"Address Resolution Protocol ({arp_op})", "fields": arp_fields})

    # Layer 3: IPv4 / IPv6
    if pkt.haslayer(IP):
        ip = pkt[IP]
        data.ip_version = 4
        data.source_ip = ip.src
        data.destination_ip = ip.dst
        data.ip_ttl = ip.ttl
        data.ip_id = ip.id or 0
        ihl_val = ip.ihl or 5
        tos_val = getattr(ip, "tos", 0) or 0
        id_val = ip.id or 0
        chk_val = getattr(ip, "chksum", 0) or 0
        ip_fields = {
            "Version": 4,
            "Header Length": f"{ihl_val * 4} bytes ({ihl_val})",
            "Differentiated Services Field": f"0x{tos_val:02x}",
            "Total Length": ip.len or len(ip),
            "Identification": f"0x{id_val:04x} ({id_val})",
            "Flags": str(ip.flags),
            "Time to Live (TTL)": ip.ttl,
            "Protocol": f"{ip.proto} ({ip.sprintf('%IP.proto%')})",
            "Header Checksum": f"0x{chk_val:04x}",
            "Source": ip.src,
            "Destination": ip.dst,
        }
        layers_tree.append({"layer": "IPv4", "summary": f"Internet Protocol Version 4, Src: {ip.src}, Dst: {ip.dst}", "fields": ip_fields})
    elif pkt.haslayer(IPv6):
        ip6 = pkt[IPv6]
        data.ip_version = 6
        data.source_ip = ip6.src
        data.destination_ip = ip6.dst
        data.ip_ttl = ip6.hlim
        ip6_fields = {
            "Version": 6,
            "Traffic Class": f"0x{getattr(ip6, 'tc', 0) or 0:02x}",
            "Flow Label": f"0x{getattr(ip6, 'fl', 0) or 0:05x}",
            "Payload Length": ip6.plen or len(ip6.payload),
            "Next Header": ip6.nh,
            "Hop Limit": ip6.hlim,
            "Source": ip6.src,
            "Destination": ip6.dst,
        }
        layers_tree.append({"layer": "IPv6", "summary": f"Internet Protocol Version 6, Src: {ip6.src}, Dst: {ip6.dst}", "fields": ip6_fields})

    # Layer 4: TCP / UDP / ICMP
    if pkt.haslayer(TCP):
        tcp = pkt[TCP]
        data.protocol = "TCP"
        data.source_port = tcp.sport
        data.destination_port = tcp.dport
        data.tcp_flags = parse_tcp_flags(tcp.flags)
        data.tcp_seq = tcp.seq or 0
        data.tcp_ack = tcp.ack or 0
        data.tcp_window = tcp.window or 0
        
        tcp_dataofs = tcp.dataofs or 5
        tcp_flags_int = int(tcp.flags) if tcp.flags is not None else 0
        tcp_chksum = getattr(tcp, "chksum", 0) or 0
        tcp_urgptr = getattr(tcp, "urgptr", 0) or 0
        
        tcp_fields = {
            "Source Port": tcp.sport,
            "Destination Port": tcp.dport,
            "Sequence Number": data.tcp_seq,
            "Acknowledgment Number": data.tcp_ack,
            "Header Length": f"{tcp_dataofs * 4} bytes",
            "Flags": f"0x{tcp_flags_int:03x} ({data.tcp_flags})",
            "Window Size": data.tcp_window,
            "Checksum": f"0x{tcp_chksum:04x}",
            "Urgent Pointer": tcp_urgptr,
        }
        layers_tree.append({"layer": "TCP", "summary": f"Transmission Control Protocol, Src Port: {tcp.sport}, Dst Port: {tcp.dport}, [{data.tcp_flags}], Seq: {data.tcp_seq}, Ack: {data.tcp_ack}", "fields": tcp_fields})
        data.info = f"{tcp.sport} \u2192 {tcp.dport} [{data.tcp_flags}] Seq={data.tcp_seq} Ack={data.tcp_ack} Win={data.tcp_window} Len={len(tcp.payload)}"

    elif pkt.haslayer(UDP):
        udp = pkt[UDP]
        data.protocol = "UDP"
        data.source_port = udp.sport
        data.destination_port = udp.dport
        udp_len = udp.len or len(udp)
        udp_chksum = getattr(udp, "chksum", 0) or 0
        udp_fields = {
            "Source Port": udp.sport,
            "Destination Port": udp.dport,
            "Length": udp_len,
            "Checksum": f"0x{udp_chksum:04x}",
        }
        layers_tree.append({"layer": "UDP", "summary": f"User Datagram Protocol, Src Port: {udp.sport}, Dst Port: {udp.dport}", "fields": udp_fields})
        data.info = f"{udp.sport} \u2192 {udp.dport} Len={udp_len}"

    elif pkt.haslayer(ICMP):
        icmp = pkt[ICMP]
        data.protocol = "ICMP"
        icmp_type_names = {0: "Echo Reply", 3: "Destination Unreachable", 8: "Echo Request", 11: "Time Exceeded"}
        icmp_desc = icmp_type_names.get(icmp.type, f"Type {icmp.type}")
        icmp_chksum = getattr(icmp, "chksum", 0) or 0
        icmp_fields = {
            "Type": f"{icmp.type} ({icmp_desc})",
            "Code": icmp.code,
            "Checksum": f"0x{icmp_chksum:04x}",
            "Identifier": getattr(icmp, "id", 0) or 0,
            "Sequence Number": getattr(icmp, "seq", 0) or 0,
        }
        layers_tree.append({"layer": "ICMP", "summary": f"Internet Control Message Protocol ({icmp_desc})", "fields": icmp_fields})
        data.info = f"ICMP {icmp_desc} (type={icmp.type}, code={icmp.code}, id={getattr(icmp, 'id', 0)}, seq={getattr(icmp, 'seq', 0)})"

    elif pkt.haslayer(ICMPv6EchoRequest) or pkt.haslayer(ICMPv6EchoReply):
        data.protocol = "ICMPv6"
        data.info = "ICMPv6 Echo Message"
        layers_tree.append({"layer": "ICMPv6", "summary": "ICMPv6 Echo Message", "fields": {}})

    # Layer 7: DNS
    if pkt.haslayer(DNS):
        dns = pkt[DNS]
        data.protocol = "DNS"
        qr_type = "RESPONSE" if dns.qr == 1 else "QUERY"
        qname = ""
        qtype_str = "A"
        rcode_str = "NOERROR" if dns.rcode == 0 else "NXDOMAIN" if dns.rcode == 3 else f"RCODE-{dns.rcode}"
        
        qtype_map = {1: "A", 2: "NS", 5: "CNAME", 6: "SOA", 12: "PTR", 15: "MX", 16: "TXT", 28: "AAAA", 255: "ANY"}
        
        if dns.qd and isinstance(dns.qd, DNSQR):
            qname = dns.qd.qname.decode("utf-8", errors="ignore").rstrip(".")
            qtype_str = qtype_map.get(dns.qd.qtype, f"TYPE{dns.qd.qtype}")
        
        resp_data = ""
        if dns.qr == 1 and dns.an:
            # First answer
            answers = []
            curr = dns.an
            while curr and isinstance(curr, DNSRR):
                rdata_val = getattr(curr, "rdata", "")
                if isinstance(rdata_val, bytes):
                    rdata_val = rdata_val.decode("utf-8", errors="ignore")
                answers.append(str(rdata_val))
                curr = curr.payload if hasattr(curr, "payload") and isinstance(curr.payload, DNSRR) else None
            resp_data = ", ".join(answers[:3])
            
        dns_fields = {
            "Transaction ID": f"0x{dns.id:04x}",
            "Flags": f"0x{int(dns.qr):04x} ({qr_type})",
            "Questions": dns.qdcount,
            "Answer RRs": dns.ancount,
            "Authority RRs": dns.nscount,
            "Additional RRs": dns.arcount,
            "Query Name": qname,
            "Query Type": qtype_str,
            "Response Code": rcode_str,
            "Resolved Data": resp_data or "(None)",
        }
        layers_tree.append({"layer": "DNS", "summary": f"Domain Name System ({qr_type} {qname})", "fields": dns_fields})
        
        data.info = f"Standard query {qtype_str} {qname}" if qr_type == "QUERY" else f"Standard response {qtype_str} {qname} -> {resp_data or rcode_str}"
        
        # Check suspicious DNS indicators
        is_susp = False
        susp_reason = ""
        if len(qname) > 50:
            is_susp = True
            susp_reason = "Unusually long domain name (possible tunneling/DGA)"
        elif dns.rcode == 3:
            is_susp = True
            susp_reason = "NXDOMAIN Non-Existent Domain"
        elif qtype_str in ("ANY", "TXT") and len(resp_data) > 100:
            is_susp = True
            susp_reason = f"High volume {qtype_str} DNS payload"

        data.dns_record = {
            "query_id": dns.id,
            "record_type": qr_type,
            "query_name": qname or "unknown",
            "query_type": qtype_str,
            "rcode": rcode_str,
            "response_data": resp_data,
            "is_suspicious": is_susp,
            "anomaly_reason": susp_reason,
        }

    # Layer 7: HTTP Inspection (Cleartext)
    if data.protocol == "TCP" and (data.source_port in (80, 8080, 8000) or data.destination_port in (80, 8080, 8000)):
        payload_bytes = bytes(pkt[TCP].payload)
        if payload_bytes:
            first_line = payload_bytes.split(b"\r\n")[0].decode("utf-8", errors="ignore")
            # Check for HTTP Request
            for method in ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"]:
                if first_line.startswith(method + " "):
                    parts = first_line.split(" ")
                    uri = parts[1] if len(parts) > 1 else "/"
                    host = ""
                    ua = ""
                    for line in payload_bytes.split(b"\r\n"):
                        l_str = line.decode("utf-8", errors="ignore")
                        if l_str.lower().startswith("host:"):
                            host = l_str[5:].strip()
                        elif l_str.lower().startswith("user-agent:"):
                            ua = l_str[11:].strip()
                    
                    data.protocol = "HTTP"
                    data.info = f"{method} {uri} HTTP/1.1 (Host: {host})"
                    data.http_record = {
                        "traffic_type": "REQUEST",
                        "method": method,
                        "host": host,
                        "uri": uri,
                        "status_code": None,
                        "status_phrase": None,
                        "user_agent": ua,
                        "content_type": None,
                        "server": None,
                    }
                    layers_tree.append({
                        "layer": "HTTP",
                        "summary": f"Hypertext Transfer Protocol ({method} {uri})",
                        "fields": {"Method": method, "URI": uri, "Host": host, "User-Agent": ua}
                    })
                    break
            
            # Check for HTTP Response
            if first_line.startswith("HTTP/1.0 ") or first_line.startswith("HTTP/1.1 ") or first_line.startswith("HTTP/2 "):
                parts = first_line.split(" ")
                status_code = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 200
                phrase = " ".join(parts[2:]) if len(parts) > 2 else ""
                ctype = ""
                srv = ""
                for line in payload_bytes.split(b"\r\n"):
                    l_str = line.decode("utf-8", errors="ignore")
                    if l_str.lower().startswith("content-type:"):
                        ctype = l_str[13:].strip()
                    elif l_str.lower().startswith("server:"):
                        srv = l_str[7:].strip()
                data.protocol = "HTTP"
                data.info = f"HTTP/1.1 {status_code} {phrase}"
                data.http_record = {
                    "traffic_type": "RESPONSE",
                    "method": None,
                    "host": None,
                    "uri": None,
                    "status_code": status_code,
                    "status_phrase": phrase,
                    "user_agent": None,
                    "content_type": ctype,
                    "server": srv,
                }
                layers_tree.append({
                    "layer": "HTTP",
                    "summary": f"Hypertext Transfer Protocol Response ({status_code} {phrase})",
                    "fields": {"Status Code": status_code, "Status Phrase": phrase, "Content-Type": ctype, "Server": srv}
                })

    # TLS / HTTPS (Port 443 / Handshake detection)
    if data.protocol == "TCP" and (data.source_port == 443 or data.destination_port == 443 or (TLS and pkt.haslayer(TLS))):
        payload_bytes = bytes(pkt[TCP].payload)
        tls_ver = "TLS"
        sni_name = ""
        is_tls_handshake = False
        
        # Raw TLS Record Header parse (0x16 = Handshake, 0x03 0x01/02/03 = TLS 1.0/1.1/1.2)
        if len(payload_bytes) >= 5 and payload_bytes[0] == 0x16:
            is_tls_handshake = True
            v_minor = payload_bytes[2]
            v_map = {1: "TLS 1.0", 2: "TLS 1.1", 3: "TLS 1.2", 4: "TLS 1.3"}
            tls_ver = v_map.get(v_minor, "TLS 1.2")
            
            # Extract SNI if Client Hello (handshake type 0x01)
            if len(payload_bytes) > 43 and payload_bytes[5] == 0x01:
                try:
                    # Scan for server_name extension (0x00 0x00)
                    sni_idx = payload_bytes.find(b"\x00\x00")
                    if sni_idx != -1 and sni_idx + 9 < len(payload_bytes):
                        name_len = payload_bytes[sni_idx + 7]
                        sni_bytes = payload_bytes[sni_idx + 8 : sni_idx + 8 + name_len]
                        if sni_bytes.isascii():
                            sni_name = sni_bytes.decode("ascii")
                except Exception:
                    sni_name = ""
            
            data.protocol = "TLS"
            desc = f"Handshake ({tls_ver})" + (f" SNI={sni_name}" if sni_name else "")
            data.info = f"{data.source_port} \u2192 {data.destination_port} {desc}"
            data.http_record = {
                "traffic_type": "TLS_HANDSHAKE",
                "method": None,
                "host": sni_name or None,
                "uri": None,
                "status_code": None,
                "status_phrase": None,
                "user_agent": None,
                "content_type": None,
                "server": None,
                "tls_version": tls_ver,
                "tls_sni": sni_name or None,
            }
            layers_tree.append({
                "layer": "TLS",
                "summary": f"Transport Layer Security ({tls_ver} Handshake)",
                "fields": {
                    "Version": tls_ver,
                    "Handshake Type": "Client Hello" if payload_bytes[5] == 0x01 else "Handshake",
                    "Server Name Indication (SNI)": sni_name or "Encrypted / Not specified"
                }
            })
        elif data.source_port == 443 or data.destination_port == 443:
            # Encrypted TLS Application Data
            if len(payload_bytes) > 0 and payload_bytes[0] == 0x17:
                data.protocol = "TLS"
                data.info = f"{data.source_port} \u2192 {data.destination_port} Application Data (Encrypted)"
                layers_tree.append({
                    "layer": "TLS",
                    "summary": "Transport Layer Security (Application Data)",
                    "fields": {
                        "Content Type": "Application Data (23)",
                        "Encryption Note": "Payload is encrypted by TLS session keys. Deep payload inspection is defensively limited to handshake metadata."
                    }
                })

    # Fallback info
    if not data.info:
        data.info = f"{data.protocol} packet, len={data.length}"

    # Extract safe payload preview
    raw_payload = bytes(pkt.payload)
    if raw_payload:
        data.payload_preview = format_hex_preview(raw_payload)

    data.layers_json = json.dumps(layers_tree)
    return data

def parse_pcap_file(filepath: str, max_packets: int = 10000) -> Tuple[List[ParsedPacketData], Dict[str, Any]]:
    """
    Parses a PCAP/PCAPNG file using Scapy.
    Returns list of ParsedPacketData and capture summary statistics.
    """
    packets_data = []
    base_time: Optional[float] = None
    first_time: float = 0.0
    last_time: float = 0.0
    total_bytes = 0

    # Read packets
    count = 0
    with PcapReader(filepath) as pcap_reader:
        for pkt in pcap_reader:
            count += 1
            pkt_time = float(pkt.time)
            if base_time is None:
                base_time = pkt_time
                first_time = pkt_time
            last_time = pkt_time
            total_bytes += len(pkt)
            
            parsed_pkt = parse_single_packet(pkt, count, base_time)
            packets_data.append(parsed_pkt)
            
            if count >= max_packets:
                break

    duration = round(last_time - first_time, 4) if base_time is not None else 0.0

    summary = {
        "packet_count": count,
        "total_bytes": total_bytes,
        "duration_seconds": duration,
        "start_time": first_time,
        "end_time": last_time,
    }
    return packets_data, summary

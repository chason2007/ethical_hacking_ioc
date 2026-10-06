import time
from pathlib import Path
from scapy.all import wrpcap
from scapy.layers.l2 import Ether, ARP
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.dns import DNS, DNSQR, DNSRR
from backend.config import settings

def generate_demo_pcap(output_path: Path = None) -> Path:
    if output_path is None:
        output_path = settings.SAMPLE_DATA_DIR / "demo_capture.pcap"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    packets = []
    base_t = time.time() - 120.0  # 2 minutes ago
    
    # 1. ARP Resolution (192.168.1.50 asks for gateway 192.168.1.1)
    p1 = Ether(src="00:1a:2b:3c:4d:5e", dst="ff:ff:ff:ff:ff:ff") / ARP(
        op=1, hwsrc="00:1a:2b:3c:4d:5e", psrc="192.168.1.50",
        hwdst="00:00:00:00:00:00", pdst="192.168.1.1"
    )
    p1.time = base_t + 0.1
    packets.append(p1)

    p2 = Ether(src="00:50:56:c0:00:01", dst="00:1a:2b:3c:4d:5e") / ARP(
        op=2, hwsrc="00:50:56:c0:00:01", psrc="192.168.1.1",
        hwdst="00:1a:2b:3c:4d:5e", pdst="192.168.1.50"
    )
    p2.time = base_t + 0.15
    packets.append(p2)

    # 2. DNS Queries and Responses
    # Query 1: api.github.com -> 140.82.121.4
    p3 = Ether(src="00:1a:2b:3c:4d:5e", dst="00:50:56:c0:00:01") / IP(src="192.168.1.50", dst="1.1.1.1") / UDP(sport=54321, dport=53) / DNS(
        id=0x1a2b, qr=0, opcode=0, rd=1, qd=DNSQR(qname="api.github.com", qtype="A")
    )
    p3.time = base_t + 0.4
    packets.append(p3)

    p4 = Ether(src="00:50:56:c0:00:01", dst="00:1a:2b:3c:4d:5e") / IP(src="1.1.1.1", dst="192.168.1.50") / UDP(sport=53, dport=54321) / DNS(
        id=0x1a2b, qr=1, opcode=0, aa=0, rd=1, ra=1, rcode=0,
        qd=DNSQR(qname="api.github.com", qtype="A"),
        an=DNSRR(rrname="api.github.com", type="A", rclass=1, ttl=300, rdata="140.82.121.4")
    )
    p4.time = base_t + 0.46
    packets.append(p4)

    # Query 2: NXDOMAIN test
    p5 = Ether(src="00:1a:2b:3c:4d:5e", dst="00:50:56:c0:00:01") / IP(src="192.168.1.50", dst="1.1.1.1") / UDP(sport=54322, dport=53) / DNS(
        id=0x3c4d, qr=0, rd=1, qd=DNSQR(qname="nonexistent-target-9988.corp.internal", qtype="A")
    )
    p5.time = base_t + 1.1
    packets.append(p5)

    p6 = Ether(src="00:50:56:c0:00:01", dst="00:1a:2b:3c:4d:5e") / IP(src="1.1.1.1", dst="192.168.1.50") / UDP(sport=53, dport=54322) / DNS(
        id=0x3c4d, qr=1, rd=1, ra=1, rcode=3,  # NXDOMAIN
        qd=DNSQR(qname="nonexistent-target-9988.corp.internal", qtype="A")
    )
    p6.time = base_t + 1.18
    packets.append(p6)

    # Query 3: Long domain (tunneling/DGA simulation)
    long_q = "chunk-01-a7f9b2c3d4e5f60718293a4b5c6d7e8f.exfil-stream.internal"
    p7 = Ether(src="00:1a:2b:3c:4d:5e", dst="00:50:56:c0:00:01") / IP(src="192.168.1.50", dst="1.1.1.1") / UDP(sport=54323, dport=53) / DNS(
        id=0x5e6f, qr=0, rd=1, qd=DNSQR(qname=long_q, qtype="TXT")
    )
    p7.time = base_t + 2.0
    packets.append(p7)

    # 3. HTTP Cleartext Traffic (GET /index.html on port 80)
    # 3-Way Handshake
    p8 = Ether(src="00:1a:2b:3c:4d:5e", dst="00:50:56:c0:00:01") / IP(src="192.168.1.50", dst="192.168.1.100") / TCP(sport=49160, dport=80, flags="S", seq=1000, window=64240)
    p8.time = base_t + 2.5
    packets.append(p8)

    p9 = Ether(src="00:50:56:c0:00:01", dst="00:1a:2b:3c:4d:5e") / IP(src="192.168.1.100", dst="192.168.1.50") / TCP(sport=80, dport=49160, flags="SA", seq=5000, ack=1001, window=65535)
    p9.time = base_t + 2.52
    packets.append(p9)

    p10 = Ether(src="00:1a:2b:3c:4d:5e", dst="00:50:56:c0:00:01") / IP(src="192.168.1.50", dst="192.168.1.100") / TCP(sport=49160, dport=80, flags="A", seq=1001, ack=5001, window=64240)
    p10.time = base_t + 2.53
    packets.append(p10)

    # HTTP Request
    http_req = b"GET /api/v1/status HTTP/1.1\r\nHost: internal-portal.local\r\nUser-Agent: Mozilla/5.0 NetworkAuditor/1.0\r\nAccept: application/json\r\n\r\n"
    p11 = Ether(src="00:1a:2b:3c:4d:5e", dst="00:50:56:c0:00:01") / IP(src="192.168.1.50", dst="192.168.1.100") / TCP(sport=49160, dport=80, flags="PA", seq=1001, ack=5001, window=64240) / http_req
    p11.time = base_t + 2.55
    packets.append(p11)

    # HTTP Response
    http_resp = b"HTTP/1.1 200 OK\r\nServer: nginx/1.24\r\nContent-Type: application/json\r\nContent-Length: 35\r\n\r\n{\"status\":\"ok\",\"service\":\"gateway\"}"
    p12 = Ether(src="00:50:56:c0:00:01", dst="00:1a:2b:3c:4d:5e") / IP(src="192.168.1.100", dst="192.168.1.50") / TCP(sport=80, dport=49160, flags="PA", seq=5001, ack=1001 + len(http_req), window=65535) / http_resp
    p12.time = base_t + 2.58
    packets.append(p12)

    # Teardown
    p13 = Ether(src="00:1a:2b:3c:4d:5e", dst="00:50:56:c0:00:01") / IP(src="192.168.1.50", dst="192.168.1.100") / TCP(sport=49160, dport=80, flags="FA", seq=1001 + len(http_req), ack=5001 + len(http_resp), window=64240)
    p13.time = base_t + 2.65
    packets.append(p13)

    p14 = Ether(src="00:50:56:c0:00:01", dst="00:1a:2b:3c:4d:5e") / IP(src="192.168.1.100", dst="192.168.1.50") / TCP(sport=80, dport=49160, flags="A", seq=5001 + len(http_resp), ack=1002 + len(http_req), window=65535)
    p14.time = base_t + 2.66
    packets.append(p14)

    # 4. ICMP Echo Request & Reply (Ping diagnostics)
    for i in range(4):
        t_offset = 3.5 + i * 0.2
        req = Ether(src="00:1a:2b:3c:4d:5e", dst="00:50:56:c0:00:01") / IP(src="192.168.1.50", dst="8.8.8.8", ttl=64) / ICMP(type=8, code=0, id=0x1234, seq=i+1)
        req.time = base_t + t_offset
        packets.append(req)

        rep = Ether(src="00:50:56:c0:00:01", dst="00:1a:2b:3c:4d:5e") / IP(src="8.8.8.8", dst="192.168.1.50", ttl=56) / ICMP(type=0, code=0, id=0x1234, seq=i+1)
        rep.time = base_t + t_offset + 0.02
        packets.append(rep)

    # 5. HTTPS / TLS Handshake Simulation on Port 443
    tls_client_hello_payload = (
        b"\x16\x03\x01\x00\x55"  # Content type: Handshake (22), Version: TLS 1.0 (03 01), Length: 85
        b"\x01\x00\x00\x51"      # Handshake type: Client Hello (1), Length: 81
        b"\x03\x03"              # Client Version: TLS 1.2
        + b"\x00" * 32           # Random bytes (32)
        + b"\x00"                # Session ID len
        + b"\x00\x02\xc0\x2f"    # Cipher suites
        + b"\x01\x00"            # Compression methods
        + b"\x00\x1a"            # Extensions length
        + b"\x00\x00\x00\x16\x00\x14\x00\x00\x11api.service.internal" # Server Name Indication (SNI)
    )
    p_tls_syn = Ether(src="00:1a:2b:3c:4d:5e", dst="00:50:56:c0:00:01") / IP(src="192.168.1.50", dst="104.16.132.229") / TCP(sport=51200, dport=443, flags="S", seq=20000, window=65535)
    p_tls_syn.time = base_t + 5.0
    packets.append(p_tls_syn)

    p_tls_synack = Ether(src="00:50:56:c0:00:01", dst="00:1a:2b:3c:4d:5e") / IP(src="104.16.132.229", dst="192.168.1.50") / TCP(sport=443, dport=51200, flags="SA", seq=80000, ack=20001, window=65535)
    p_tls_synack.time = base_t + 5.03
    packets.append(p_tls_synack)

    p_tls_ack = Ether(src="00:1a:2b:3c:4d:5e", dst="00:50:56:c0:00:01") / IP(src="192.168.1.50", dst="104.16.132.229") / TCP(sport=51200, dport=443, flags="A", seq=20001, ack=80001, window=65535)
    p_tls_ack.time = base_t + 5.04
    packets.append(p_tls_ack)

    p_tls_hello = Ether(src="00:1a:2b:3c:4d:5e", dst="00:50:56:c0:00:01") / IP(src="192.168.1.50", dst="104.16.132.229") / TCP(sport=51200, dport=443, flags="PA", seq=20001, ack=80001, window=65535) / tls_client_hello_payload
    p_tls_hello.time = base_t + 5.05
    packets.append(p_tls_hello)

    # TLS Encrypted Application Data
    tls_app_data = b"\x17\x03\x03\x00\x60" + b"\xaa" * 96  # Type 23 (Application Data), TLS 1.2
    p_tls_data = Ether(src="00:1a:2b:3c:4d:5e", dst="00:50:56:c0:00:01") / IP(src="192.168.1.50", dst="104.16.132.229") / TCP(sport=51200, dport=443, flags="PA", seq=20001 + len(tls_client_hello_payload), ack=80001, window=65535) / tls_app_data
    p_tls_data.time = base_t + 5.12
    packets.append(p_tls_data)

    # 6. Port Scan Pattern (Reconnaissance demonstration: 192.168.1.95 scanning 192.168.1.100 across 16 ports)
    scan_ports = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 1433, 3306, 3389, 5432, 8080]
    for idx, port in enumerate(scan_ports):
        t_scan = base_t + 7.0 + idx * 0.1
        # SYN probe
        p_syn = Ether(src="00:0c:29:ab:cd:ef", dst="00:50:56:c0:00:01") / IP(src="192.168.1.95", dst="192.168.1.100") / TCP(sport=43000 + idx, dport=port, flags="S", seq=10000 + idx, window=1024)
        p_syn.time = t_scan
        packets.append(p_syn)

        # Closed ports reply with RST-ACK
        if port not in (80, 443, 22):
            p_rst = Ether(src="00:50:56:c0:00:01", dst="00:0c:29:ab:cd:ef") / IP(src="192.168.1.100", dst="192.168.1.95") / TCP(sport=port, dport=43000 + idx, flags="RA", seq=0, ack=10001 + idx, window=0)
            p_rst.time = t_scan + 0.01
            packets.append(p_rst)

    # 7. Oversized Frame (Jumbo frame / LSO test observation)
    jumbo_payload = b"X" * 1600
    p_jumbo = Ether(src="00:1a:2b:3c:4d:5e", dst="00:50:56:c0:00:01") / IP(src="192.168.1.50", dst="192.168.1.200") / UDP(sport=9999, dport=9999) / jumbo_payload
    p_jumbo.time = base_t + 9.5
    packets.append(p_jumbo)

    # Sort packets by time
    packets.sort(key=lambda p: float(p.time))

    # Write PCAP
    wrpcap(str(output_path), packets)
    return output_path

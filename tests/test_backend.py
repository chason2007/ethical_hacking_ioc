import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from scapy.all import Ether, IP, TCP, UDP, ICMP, wrpcap

from backend.main import app
from backend.services.synthetic_pcap_generator import generate_demo_pcap
from backend.services.pcap_parser import parse_pcap_file, parse_single_packet
from backend.services.analysis_engine import AnalysisEngine
from backend.services.security_analyzer import SecurityAnalyzer
from backend.database import Base, engine
from backend.models import Capture, Packet, Endpoint, Conversation, ProtocolStat, SecurityFinding

Base.metadata.create_all(bind=engine)
client = TestClient(app)

@pytest.fixture(scope="session")
def demo_pcap_path(tmp_path_factory):
    p = tmp_path_factory.mktemp("data") / "test_demo.pcap"
    generate_demo_pcap(p)
    return p

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "uptime_seconds" in data

def test_pcap_parser_valid_file(demo_pcap_path):
    packets, summary = parse_pcap_file(str(demo_pcap_path))
    assert len(packets) > 0
    assert summary["packet_count"] == len(packets)
    assert summary["total_bytes"] > 0
    assert summary["duration_seconds"] >= 0

def test_single_packet_parsing():
    pkt = Ether(src="00:11:22:33:44:55", dst="66:77:88:99:aa:bb") / IP(src="192.168.1.10", dst="192.168.1.20") / TCP(sport=1234, dport=80, flags="S", seq=100)
    parsed = parse_single_packet(pkt, 1, float(pkt.time))
    assert parsed.packet_number == 1
    assert parsed.protocol == "TCP"
    assert parsed.source_ip == "192.168.1.10"
    assert parsed.destination_ip == "192.168.1.20"
    assert parsed.source_port == 1234
    assert parsed.destination_port == 80
    assert "SYN" in parsed.tcp_flags
    assert parsed.layers_json is not None

def test_udp_icmp_parsing():
    udp_pkt = Ether() / IP(src="10.0.0.1", dst="10.0.0.2") / UDP(sport=53, dport=53000)
    parsed_udp = parse_single_packet(udp_pkt, 1, float(udp_pkt.time))
    assert parsed_udp.protocol == "UDP"
    assert parsed_udp.source_port == 53
    assert parsed_udp.destination_port == 53000

    icmp_pkt = Ether() / IP(src="10.0.0.1", dst="10.0.0.2") / ICMP(type=8, code=0)
    parsed_icmp = parse_single_packet(icmp_pkt, 2, float(icmp_pkt.time))
    assert parsed_icmp.protocol == "ICMP"
    assert "Echo Request" in parsed_icmp.info

def test_security_analyzer_rules(demo_pcap_path):
    packets, summary = parse_pcap_file(str(demo_pcap_path))
    findings = SecurityAnalyzer.analyze(packets, summary)
    assert len(findings) > 0
    
    categories = [f["category"] for f in findings]
    # Check key defensive rules triggered
    assert "PORT_SCAN" in categories or "SYN_SCAN" in categories
    assert any(f["severity"] in ("HIGH", "MEDIUM", "LOW", "INFORMATIONAL") for f in findings)
    
    for f in findings:
        assert "why_it_matters" in f
        assert "recommendation" in f
        assert "evidence" in f

def test_analysis_engine_metrics(demo_pcap_path):
    packets, summary = parse_pcap_file(str(demo_pcap_path))
    res = AnalysisEngine.analyze_capture(packets, summary["total_bytes"], summary["duration_seconds"])
    assert len(res["endpoints"]) > 0
    assert len(res["conversations"]) > 0
    assert len(res["protocol_stats"]) > 0
    assert len(res["timeline"]) > 0
    assert res["statistics"]["total_packets"] == len(packets)

def test_demo_capture_api():
    response = client.post("/api/captures/demo")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    capture_id = data["id"]

    # Verify packets listing
    pkt_resp = client.get(f"/api/captures/{capture_id}/packets?page=1&page_size=10")
    assert pkt_resp.status_code == 200
    pkt_data = pkt_resp.json()
    assert len(pkt_data["items"]) == 10
    assert pkt_data["total"] > 10

    # Verify statistics
    stats_resp = client.get(f"/api/captures/{capture_id}/statistics")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["total_packets"] > 0

    # Verify security findings
    sec_resp = client.get(f"/api/captures/{capture_id}/security")
    assert sec_resp.status_code == 200
    sec = sec_resp.json()
    assert sec["total_findings"] > 0

    # Verify PDF report generation
    rep_resp = client.get(f"/api/captures/{capture_id}/report")
    assert rep_resp.status_code == 200
    assert rep_resp.headers["content-type"] == "application/pdf"

    # Verify CSV export
    csv_resp = client.get(f"/api/captures/{capture_id}/export/csv")
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]

def test_invalid_upload_extension():
    response = client.post(
        "/api/captures/upload",
        files={"file": ("test.txt", b"plain text data", "text/plain")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

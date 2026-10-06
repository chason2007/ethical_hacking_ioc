# Chapter 8: Module Description

## 8.1 Backend Core Modules
1. **`pcap_parser.py` (Packet Dissection Module):**
   - Implements `parse_pcap_file()` and `parse_single_packet()`.
   - Traverses frame layers using Scapy objects.
   - Extracts detailed field dictionaries for Ethernet, ARP, IP, TCP, UDP, ICMP, DNS, HTTP, and TLS.
   - Builds human-readable information summaries and safe hex dump previews.

2. **`analysis_engine.py` (Analytical Aggregator):**
   - Implements `AnalysisEngine.analyze_capture()`.
   - Aggregates bidirectional flows into 5-tuple conversation structures.
   - Computes endpoint transmit/receive statistics and classifies IP scope (RFC 1918 private vs public).
   - Generates temporal time-series bins for the traffic timeline.

3. **`security_analyzer.py` (Defensive Anomaly Engine):**
   - Implements `SecurityAnalyzer.analyze()`.
   - Evaluates rule heuristics for port scanning, TCP SYN half-open probing, RST bursts, long DNS subdomains, NXDOMAIN spikes, cleartext credentials, and oversized frames.
   - Generates structured security finding objects with severity, evidence, rationale, and mitigation advice.

4. **`synthetic_pcap_generator.py` (Demo Data Generator):**
   - Constructs realistic, non-malicious synthetic PCAP files using Scapy.
   - Simulates legitimate ARP, DNS, HTTP, HTTPS/TLS, ICMP, and educational scan sequences.

5. **`report_generator.py` (Audit Report Engine):**
   - Uses `ReportLab` to compile PDF audit reports with cybersecurity styles, tables, and severity badges.

## 8.2 Frontend Interface Modules
1. **`DashboardPage.tsx`:** Primary SOC operations dashboard displaying high-level KPIs, protocol distribution charts, and security alerts.
2. **`PacketExplorerPage.tsx`:** Fast, paginated packet inspection grid supporting sorting, full-text search, and visual filter builders.
3. **`PacketInspectorModal.tsx`:** Deep packet hierarchy modal rendering expandable layer trees and hex previews.
4. **`ProtocolsPage.tsx`:** Detailed protocol analysis view with dedicated tabs for DNS and HTTP/TLS forensics.
5. **`ConversationsPage.tsx`:** 5-tuple flow viewer showing directional packet ratios and session durations.
6. **`EndpointsPage.tsx`:** Network node directory displaying transmission volumes and private/public classification.
7. **`PortsPage.tsx`:** Port frequency histogram with standard IANA service mappings.
8. **`SecurityInsightsPage.tsx`:** Dedicated defensive security portal detailing detected anomalies and recommendations.
9. **`TimelinePage.tsx`:** Interactive time-series telemetry chart with multi-protocol series toggles.
10. **`ReportsPage.tsx`:** Deliverable download portal for PDF, CSV, and JSON deliverables.
11. **`CapturesPage.tsx`:** Historical capture management with delete and switch capabilities.
12. **`EducationalPage.tsx`:** Comprehensive academic protocol theory and viva preparation reference guide.

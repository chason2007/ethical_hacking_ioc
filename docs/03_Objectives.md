# Chapter 3: Objectives

## 3.1 Primary Objectives
1. **Multi-Format Packet Ingestion:** Implement secure upload and asynchronous parsing for standard packet capture formats (`.pcap`, `.pcapng`, `.cap`) up to 500MB (configurable).
2. **Comprehensive Protocol Dissection:** Develop dissection modules covering Link (Ethernet, ARP), Network (IPv4, IPv6, ICMP), Transport (TCP, UDP), and Application (DNS, HTTP, TLS) layers.
3. **Structured Flow & Node Aggregation:** Automatically compute bidirectional conversation pairs and endpoint traffic volume metrics with private/public IP classification.
4. **Defensive Anomaly Engine:** Implement rule-based heuristic anomaly detection covering:
   - Port scanning (horizontal/vertical reconnaissance sweeps).
   - TCP SYN stealth scans (half-open probes).
   - Elevated TCP RST frequencies.
   - DNS tunneling and DGA indicators (oversized domain names, NXDOMAIN bursts).
   - Insecure plaintext protocols (HTTP, FTP, Telnet).
   - Frame MTU outliers and broadcast traffic saturation.
5. **Interactive Cybersecurity Operations Dashboard:** Build a modern, dark-first React/TypeScript frontend incorporating responsive charts, Wireshark-compatible hierarchical tree inspectors, filter builders, and instant synthetic demo datasets.
6. **Executive Audit Deliverables:** Provide automated generation of PDF security audit reports and data exports in CSV and JSON formats.
7. **Educational Pedagogical Integration:** Embed technical context cards, threat rationales, defensive mitigations, and viva reference materials directly inside the user interface.

# Chapter 12: Results & Experimental Evaluation

## 12.1 Performance Benchmark
The system was evaluated against various trace sizes on standard hardware (Intel Core i5, 8GB RAM, Windows 11):

| Capture Dataset | Frame Count | File Size | Dissection & Analysis Time | Database Commit Time | UI Render Latency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Synthetic Demo PCAP** | 57 packets | 4.8 KB | 0.08 seconds | 0.03 seconds | < 50 ms |
| **Lab Network Capture** | 1,250 packets | 640 KB | 0.72 seconds | 0.18 seconds | < 80 ms |
| **Campus Boundary Capture** | 10,000 packets | 5.8 MB | 4.95 seconds | 0.94 seconds | < 120 ms |

## 12.2 Heuristic Detection Efficacy
The defensive security rules successfully identified:
1. **Vertical Port Scanning:** Host `192.168.1.95` was correctly flagged with `MEDIUM`/`HIGH` severity for probing 16 distinct ports within 1.6 seconds.
2. **SYN Stealth Scanning:** Accurately correlated 16 orphaned SYN packets without completed ACKs, distinguishing malicious scans from normal browsing.
3. **Elevated RST Frequency:** Flagged closed-port RST responses from the target host (`192.168.1.100`), illustrating the classic RFC 793 rejection signature.
4. **Cleartext Transmission:** Flagged legacy FTP and Telnet sessions as security risks, recommending cryptographic migration to SFTP/SSH.
5. **DNS Anomalies:** Identified Base64-encoded subdomains exceeding 50 characters, simulating DNS data exfiltration attempts.

## 12.3 Reporting & Usability
- Generated formal PDF reports containing executive summaries, protocol tables, and structured security recommendations in under 1.5 seconds.
- Filter builder enabled sub-second search across thousands of packets.

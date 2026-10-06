# Chapter 13: Limitations

## 13.1 Current System Limitations
1. **Encrypted Payload Opacity:** In accordance with cryptographic standards, TLS/HTTPS payloads cannot be decrypted without endpoint private keys or session pre-master secrets. Deep inspection is intentionally confined to handshake metadata (SNI, cipher suites, TLS version).
2. **In-Memory Frame Threshold:** For single-node desktop development, capture ingestion is optimized for PCAPs up to 50MB (approximately 50,000–100,000 packets). Ultra-large enterprise captures (> 1GB) require distributed big-data pipelines (e.g. Apache Spark or ClickHouse).
3. **Passive Offline Analysis:** The platform operates on pre-recorded PCAP files and does not perform live network interface promiscuous sniffing (which requires administrative/root privileges on host operating systems).
4. **Heuristic False Positives:** Highly active authorized administrative scanners (e.g. Tenable Nessus, Qualys) trigger the same heuristic flags as unauthorized reconnaissance tools.

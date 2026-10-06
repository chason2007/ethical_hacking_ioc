# Chapter 14: Future Scope

## 14.1 Planned Enhancements
1. **Live Network Sniffing Daemon:** Implement an optional local agent with libpcap/Npcap bindings for authorized real-time interface capture.
2. **TLS Keylog Ingestion (Defensive Decryption):** Allow security students in lab settings to supply an `SSLKEYLOGFILE` to decrypt simulated lab TLS flows for educational inspection.
3. **Machine Learning Anomaly Detection:** Train unsupervised isolation forests and autoencoders on flow telemetry to identify zero-day beaconing patterns without hardcoded static thresholds.
4. **Snort / Suricata Rule Compilation:** Allow students to write custom IDS rules and test them directly against uploaded PCAP traces.
5. **GeoIP & Autonomous System Number (ASN) Mapping:** Integrate MaxMind GeoLite2 databases to visualize international geographic endpoint flows on world map projections.

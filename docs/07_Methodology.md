# Chapter 7: Methodology

## 7.1 Engineering Workflow
The platform operates on a twelve-stage defensive packet analysis lifecycle:

### Step 1: Capture Ingestion
Packet capture traces are uploaded via the web interface or synthesized dynamically through the built-in generator.

### Step 2: File Validation
Uploaded binaries undergo verification:
- Extension matching against `.pcap`, `.pcapng`, and `.cap`.
- Zero-byte file checks and maximum file size enforcement (50MB threshold).
- Magic byte validation to ensure legitimate libpcap / pcapng structure.

### Step 3: Layer Parsing
The `PcapReader` iterates sequentially through wire frames, extracting raw byte slices without invoking third-party external daemons or system utilities.

### Step 4: Protocol Identification
Frames are inspected through protocol dissectors:
- Layer 2: Ethernet II (MAC addresses, EtherType), ARP (OpCode, Target MAC/IP).
- Layer 3: IPv4 (IHL, TTL, Identification, Protocol ID), IPv6 (Next Header, Hop Limit).
- Layer 4: TCP (Ports, Seq, Ack, Flags, Window, Options), UDP (Ports, Length), ICMP (Type, Code, Id, Seq).
- Layer 7: DNS (ID, QR, Questions, Answers, RCODE), HTTP (Request Methods, Response Codes, Headers), TLS (Record Types, SNI, Versions).

### Step 5: Metadata Extraction & Tree Construction
Each dissected packet is transformed into an expandable hierarchical JSON layer tree (`layers_json`) and an ASCII/Hex preview string.

### Step 6: Normalized Persistence
Entities are batch-inserted into relational tables via SQLAlchemy ORM with indexed foreign keys.

### Step 7: Traffic Statistical Computation
The platform calculates total packet volume, byte counts, average packet lengths, protocol percentages, and MTU size distribution histograms.

### Step 8: Conversation & Endpoint Aggregation
Packets sharing canonical 5-tuples are aggregated into bidirectional conversations, measuring directional flow volume (A &rarr; B and B &rarr; A) and active duration.

### Step 9: Defensive Anomaly Detection
Rule-based heuristic analyzers evaluate the parsed traces for reconnaissance activity, half-open SYN probing, excessive RST packets, DNS tunneling, and plaintext protocol risks.

### Step 10: Interactive Visualization
The frontend renders time-series telemetry charts, protocol breakdowns, and endpoint tables using Recharts SVG components.

### Step 11: Security Insights Correlation
Heuristic findings are categorized by severity (HIGH, MEDIUM, LOW, INFORMATIONAL) and augmented with threat rationales and defensive recommendations.

### Step 12: Executive Report Compilation
Users can generate official PDF audit reports via ReportLab or export normalized packet streams as CSV or JSON.

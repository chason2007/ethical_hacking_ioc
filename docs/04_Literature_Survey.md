# Chapter 4: Literature Survey

## 4.1 Comparative Analysis of Existing Solutions

| Tool / Technology | Strengths | Limitations in Educational Context |
| :--- | :--- | :--- |
| **Wireshark** | Industry standard, thousands of dissectors, real-time capture support | Complex UI, native desktop install required, no automated security anomaly reporting, lacks built-in executive PDF generation. |
| **tcpdump** | Fast command-line capture, low memory footprint | Lacks visual hierarchy, requires mastery of BPF (Berkeley Packet Filters), steep learning curve for undergraduate students. |
| **Zeek (formerly Bro)** | Excellent behavioral scripting, flow-level telemetry logging | High operational complexity, requires dedicated Linux infrastructure, outputs raw logs rather than interactive educational UI. |
| **Moloch / Arkime** | Distributed, large-scale indexing of multi-gigabyte PCAPs | High resource footprint (requires Elasticsearch/OpenSearch clusters), unsuitable for standalone classroom or viva evaluation. |
| **NetworkMiner** | Intuitive artifact and credential extraction | Windows-only GUI, limited cross-platform web capabilities, lacks automated educational reasoning cards. |

## 4.2 Research Motivation
By combining the dissecting flexibility of Python (Scapy) with the speed of FastAPI and the responsiveness of modern React component architectures, **NetProtocol Inspector** delivers a standalone, zero-external-dependency platform optimized for coursework, lab demonstrations, and viva examinations.

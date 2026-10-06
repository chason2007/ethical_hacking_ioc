# Chapter 2: Problem Statement

## 2.1 Background
Traditional network analysis tools like Wireshark and tcpdump are powerful diagnostic instruments. However, for undergraduate engineering students and early-career cybersecurity analysts, desktop packet viewers present significant learning curves:
1. **Steep Visual Complexity:** Raw packet hex streams and overwhelming configuration options often obscure higher-level understanding of protocol interactions.
2. **Lack of Automated Heuristic Correlation:** Standard viewers require manual crafting of complex display filters to infer scanning or exfiltration behaviors.
3. **Absence of Contextual Pedagogical Feedback:** Desktop analyzers display fields without explaining *why* a particular flag combination, sequence jump, or long DNS record matters from a defensive security perspective.
4. **Desktop Confinement & Lack of Shareable Reporting:** Traditional tools lack seamless web-accessible dashboards and automated executive audit report generation.

## 2.2 Formal Problem Definition
There is an acute need for a lightweight, web-native, defensively-oriented packet forensics platform tailored for academic learning that can:
- Parse `.pcap` and `.pcapng` traces asynchronously using robust Python-based dissection libraries (Scapy).
- Decouple low-level byte dissection from presentation, providing responsive pagination and structured protocol hierarchy trees.
- Automatically correlate 5-tuple conversations and active network endpoints.
- Execute defensive heuristic rules capable of flagging reconnaissance patterns and protocol violations with concrete evidence and actionable recommendations.
- Bridge theoretical networking curricula with real-world SOC forensics workflows.

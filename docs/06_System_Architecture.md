# Chapter 6: System Architecture

## 6.1 Architectural Overview
The platform employs a decoupled, multi-tier client-server architecture designed for high maintainability, fast asynchronous packet dissection, and clean separation of concerns.

```mermaid
flowchart TD
    subgraph ClientLayer["Frontend Client Tier (React + TypeScript)"]
        UI["Cybersecurity Dashboard UI"]
        PE["Packet Explorer Table"]
        PI["Deep Layer Tree Inspector"]
        SI["Security Insights Panel"]
        TL["Traffic Timeline Charts"]
        RP["Report Generator Interface"]
    end

    subgraph APILayer["REST API Gateway (FastAPI)"]
        Router["FastAPI Application Routers"]
        AuthMid["CORS & Request Validation Middleware"]
        Paging["Pagination & Filter Parameters"]
    end

    subgraph ServiceLayer["Forensics Core & Service Layer"]
        Upload["File Validation & Upload Handler"]
        Parser["Scapy Packet Parser & Dissector"]
        Analysis["Analytical Aggregation Engine"]
        SecEngine["Rule-Based Defensive Anomaly Detector"]
        RepGen["ReportLab PDF Document Compiler"]
        SynthGen["Synthetic PCAP Generator"]
    end

    subgraph DataLayer["Persistence Layer (SQLAlchemy ORM)"]
        DB[(SQLite / PostgreSQL Database)]
        CapturesTable["captures"]
        PacketsTable["packets"]
        EndpointsTable["endpoints"]
        ConvsTable["conversations"]
        FindingsTable["security_findings"]
    end

    UI -->|HTTP / JSON Requests| Router
    Router --> AuthMid
    AuthMid --> Paging
    Paging --> ServiceLayer

    Upload --> Parser
    Parser --> Analysis
    Analysis --> SecEngine
    SecEngine --> DB
    Analysis --> DB
    Parser --> DB

    DB --> Router
    Router --> RepGen
    RepGen -->|Binary PDF Stream| RP
```

## 6.2 Data Processing Pipeline
1. **Ingestion & Validation:** A `.pcap` or `.pcapng` capture is uploaded via the web interface. The server validates file headers, file extensions, and file sizes.
2. **Layer Demultiplexing:** `Scapy` sequentially reads wire frames using `PcapReader`, extracting Layer 2 (Ethernet/ARP), Layer 3 (IPv4/IPv6), Layer 4 (TCP/UDP/ICMP), and Layer 7 (DNS/HTTP/TLS) metadata.
3. **Hierarchical Serialization:** Each packet is dissected into an expandable JSON tree (`layers_json`) containing all protocol fields, ready for the frontend inspector.
4. **Statistical Correlation:** The `AnalysisEngine` aggregates bidirectional 5-tuple conversations and calculates IP endpoints, scope (private vs public), and port associations.
5. **Heuristic Anomaly Detection:** The `SecurityAnalyzer` evaluates traffic against defensive anomaly rules, outputting evidence-backed security findings with severity ratings.
6. **Persistence & Presentation:** Structured entities are committed to the database in bulk transactions. The React frontend visualizes statistics through responsive charts and interactive tables.

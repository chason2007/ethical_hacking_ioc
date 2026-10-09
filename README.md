# Packet Analysis of Common Network Protocols

> **Academic Final-Year Project / Elective Coursework:** Ethical Hacking & Network Security (B.E. / B.Tech Computer Science & Engineering)  
> **Tool Classification:** Defensive Network Traffic Forensics & Pedagogical Deep Packet Inspection Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.x-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.x-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Scapy](https://img.shields.io/badge/Scapy-2.8-red?style=flat)](https://scapy.net)
[![License](https://img.shields.io/badge/License-Educational-blue.svg)](#educational-purpose)

---

## 1. Overview
**NetProtocol Inspector** is a production-quality, web-based defensive network analysis platform designed to inspect, dissect, and visualize captured network traffic (`.pcap`, `.pcapng`, `.cap`). 

Engineered specifically for undergraduate computer science and cybersecurity curricula, the platform bridges the gap between theoretical networking concepts and practical security operations. It allows students to explore frame-level protocol hierarchies (like in Wireshark), inspect 5-tuple conversations and active endpoints, evaluate heuristic security anomalies (e.g. port scanning, SYN floods, DNS tunneling), and generate formal executive audit reports in PDF format.

> **Defensive Security Notice:** This system is an educational and forensic analysis tool. It strictly performs **passive offline analysis** of captured traces and does NOT implement packet injection, credential theft, denial-of-service, or offensive attack automation.

---

## 2. Key Features

- **Multi-Format PCAP Ingestion:** Fast drag-and-drop parsing of `.pcap`, `.pcapng`, and `.cap` traces up to 50MB with multi-stage progress tracking (Upload &rarr; Parse &rarr; Analyze &rarr; Store).
- **Interactive Packet Explorer:** Monospace packet grid featuring real-time column sorting, pagination, full-text search, and visual multi-field filter builder.
- **Wireshark-Style Deep Inspector:** Click any packet to open a hierarchical protocol tree (Frame &rarr; Ethernet &rarr; IPv4 &rarr; TCP/UDP &rarr; DNS/HTTP) alongside safe ASCII & Hex payload previews.
- **Protocol-Specific Forensics:** Dedicated diagnostic views for:
  - **DNS:** Query vs Response ratios, top requested hostnames, record type distributions (A, AAAA, MX, TXT), and high-entropy domain detection.
  - **HTTP & TLS:** Cleartext HTTP methods (GET, POST), status codes, Host headers, and TLS handshake SNI inspection without compromising payload encryption.
- **Conversations & Endpoint Analysis:** Automatic tracking of bidirectional network flows with directional volume ratios, session durations, and RFC 1918 private/public IP classification.
- **Port Usage & Service Correlation:** Transport port frequency histogram mapped against IANA service associations with defensive pedagogical context.
- **Defensive Heuristic Anomaly Engine:** Rule-based detection of:
  - Vertical and horizontal port enumeration sweeps.
  - TCP SYN stealth scans (half-open probes).
  - Elevated TCP RST frequencies (closed port rejection bursts).
  - DNS tunneling and DGA indicators (oversized subdomains, NXDOMAIN storms).
  - Cleartext transport risks (Telnet 23, FTP 21, plain HTTP 80).
  - Jumbo frames and MTU outliers.
  - Broadcast and multicast storm saturation.
- **Executive PDF Audit Report Generator:** Compiles publication-ready security audit deliverables complete with executive summaries, protocol tables, and prioritized analyst recommendations.
- **One-Click Synthetic Demo Capture:** Built-in packet generator allowing immediate demonstration and evaluation without requiring external captures or Wireshark.
- **Pedagogical Knowledge Cards:** Embedded "Why this matters", protocol theory callouts, and viva preparation questions throughout the UI.

---

## 3. System Architecture

```
User (Browser)
      │
      ▼
┌────────────────────────────────────────────────────────┐
│               React + TypeScript Frontend              │
│  - SOC Operations Dashboard      - Packet Grid Explorer│
│  - Deep Layer Tree Modal         - Anomaly Insights    │
│  - Timeline & Telemetry Charts   - PDF Report Viewer   │
└──────────────────────────┬─────────────────────────────┘
                           │ REST / JSON (Port 8000)
                           ▼
┌────────────────────────────────────────────────────────┐
│                   FastAPI REST API                     │
│  - Route Handlers & Controllers  - CORS & Middleware   │
│  - Pydantic Validation Schemas   - Pagination Engine   │
└──────────────┬───────────────────────────┬─────────────┘
               │                           │
               ▼                           ▼
┌───────────────────────────┐ ┌──────────────────────────┐
│   Forensics Engine Core   │ │   Persistence Layer      │
│  - Scapy Packet Dissector │ │  - SQLAlchemy ORM        │
│  - Analytical Aggregator  │ │  - SQLite / PostgreSQL   │
│  - Defensive Rule Analyzer│ │  - Indexed Models        │
│  - ReportLab PDF Compiler │ └──────────────────────────┘
│  - Synthetic PCAP Creator │
└───────────────────────────┘
```

---

## 4. Technology Stack

### Frontend
- **Framework:** React 19 + TypeScript
- **Build Tool:** Vite 8
- **Styling:** Tailwind CSS 4 (Custom dark cybersecurity palette)
- **Visualizations:** Recharts (SVG Time-series & Histograms)
- **Icons:** Lucide React
- **Linter:** OxLint

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Packet Dissection:** Scapy 2.8.0
- **Database & ORM:** SQLAlchemy 2.0+ (SQLite local default / PostgreSQL ready)
- **PDF Generation:** ReportLab 5.0+
- **Data Validation:** Pydantic 2.13+
- **Server:** Uvicorn ASGI

---

## 5. Supported Protocols

| OSI Layer | Protocol | Parsed Fields & Defensive Forensics |
| :--- | :--- | :--- |
| **Layer 2 (Data Link)** | **Ethernet II** | Source MAC, Destination MAC, EtherType, Frame Length |
| | **ARP** | Hardware type, OpCode (Request/Reply), Sender MAC/IP, Target MAC/IP |
| **Layer 3 (Network)** | **IPv4** | Version, Header Length (IHL), Total Length, Identification, TTL, Protocol ID, Checksum |
| | **IPv6** | Traffic Class, Flow Label, Payload Length, Next Header, Hop Limit |
| | **ICMP** | Type, Code, Identifier, Sequence Number (Echo Requests, Replies, Unreachables) |
| **Layer 4 (Transport)** | **TCP** | Source/Destination Port, Seq, Ack, Data Offset, Flags (SYN, ACK, FIN, RST, PSH, URG), Window Size |
| | **UDP** | Source/Destination Port, Length, Checksum |
| **Layer 7 (Application)**| **DNS** | Transaction ID, QR Type, Question Count, Answers, Query Name, Query Type, RCODE |
| | **HTTP** | Request Methods (GET, POST, etc.), Response Status Codes, URIs, Host Header, User-Agent |
| | **TLS / HTTPS** | Record Type, Version (TLS 1.2/1.3), Handshake Type, Server Name Indication (SNI) |

---

## 6. Security Analysis Rules

The platform applies 8 deterministic heuristic rules:
1. **Vertical/Horizontal Port Scan:** Triggered when a source contacts $\ge 12$ distinct ports within the capture window.
2. **TCP SYN Half-Open Scan:** Identifies disproportionate SYN packets with fewer than 20% completing an ACK handshake.
3. **TCP RST Bursts:** Flags elevated RST ratios ($> 15\%$ of TCP traffic), indicating closed port rejections or firewall resets.
4. **DNS Tunneling / DGA:** Flags domain names $> 42$ characters or featuring high character entropy.
5. **DNS NXDOMAIN Bursts:** Flags repeated failed domain lookups indicating host misconfiguration or domain fluxing.
6. **ICMP Ping Sweeps:** Flags source IPs dispatching Echo Requests to 8 or more unique destination endpoints.
7. **Cleartext Transmission:** Identifies legacy unencrypted FTP (port 21), Telnet (port 23), or cleartext HTTP (port 80).
8. **Jumbo Frame MTU Outliers:** Flags frames exceeding standard 1514-byte Ethernet MTU.

---

## 7. Installation & Quick Start

### Prerequisites
- Python 3.10 to 3.14
- Node.js v18+ and npm

### 1. Clone & Set Up Python Virtual Environment
```bash
git clone <repo-url>
cd "ethical hacking ioc"

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Install Python requirements
pip install -r requirements.txt
```

### 2. Set Up Frontend
```bash
cd frontend
npm install
cd ..
```

### 3. Initialize Database & Seed Demo Data
```bash
python scripts/init_db.py
python scripts/generate_sample_pcap.py
```

---

## 8. Running the Application

### Option A: One-Click Windows PowerShell Starter
```powershell
.\scripts\start_dev.ps1
```

### Option B: Manual Execution

**Terminal 1 — Backend (FastAPI):**
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be accessible at: `http://127.0.0.1:8000/docs`

**Terminal 2 — Frontend (Vite/React):**
```bash
cd frontend
npm run dev
```
Open your browser at: `http://localhost:5173`

---

## 9. Automated Testing

Run the automated backend test suite:
```bash
python -m pytest tests/test_backend.py -v
```

Run the frontend linter and production build test:
```bash
cd frontend
npm run lint
npm run build
```

---

## 10. Project Directory Structure

```
ethical-hacking-ioc/
├── backend/                  # FastAPI Backend
│   ├── api/                  # REST Routers (Captures, Packets, Security, Reports)
│   ├── models/               # SQLAlchemy DB Models
│   ├── schemas/              # Pydantic Schemas
│   ├── services/             # Scapy Parser, Analysis Engine, Security Rules
│   ├── config.py             # App Configuration
│   ├── database.py           # Database Engine & Session
│   └── main.py               # Application Entry Point
├── frontend/                 # React 19 + TypeScript + Vite
│   ├── src/
│   │   ├── components/       # Badges, Modals, Navbar, Sidebar
│   │   ├── pages/            # Dashboard, Explorer, Protocols, Security, etc.
│   │   ├── services/         # API Client
│   │   └── types/            # TypeScript Interfaces
├── docs/                     # Academic Submission Chapters (01 to 16)
│   ├── 01_Introduction.md ... 16_References.md
├── sample-data/              # Synthetic Educational PCAPs
├── reports/                  # Generated PDF Audit Reports
├── scripts/                  # Init, PCAP Generator, and Starter Scripts
├── tests/                    # Pytest Test Suites
├── requirements.txt          # Python Dependencies
└── README.md                 # Project Documentation
```

---

## 11. Academic Evaluation & Viva Companion

A dedicated `/docs` directory is included containing all 16 academic project chapters formatted for thesis and project report inclusion:
- `01_Introduction.md`
- `02_Problem_Statement.md`
- `03_Objectives.md`
- `04_Literature_Survey.md`
- `05_System_Requirements.md`
- `06_System_Architecture.md` (Includes Mermaid System Flowcharts)
- `07_Methodology.md` (12-step forensic pipeline)
- `08_Module_Description.md`
- `09_Database_Design.md` (Entity-Relationship schemas)
- `10_API_Documentation.md`
- `11_Testing.md` (Test matrices and results)
- `12_Results.md` (Performance benchmarks)
- `13_Limitations.md`
- `14_Future_Scope.md`
- `15_Conclusion.md`
- `16_References.md` (RFCs and textbooks)

Additionally, visit the in-app **"Protocol Guide"** tab for interactive viva review questions, TCP state diagrams, and packet analysis cheat sheets.
#   e t h i c a l _ h a c k i n g _ i o c  
 
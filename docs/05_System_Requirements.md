# Chapter 5: System Requirements

## 5.1 Hardware Requirements
- **Processor:** Intel Core i3 / AMD Ryzen 3 or higher (dual-core 2.0 GHz minimum; quad-core recommended for large PCAP analysis).
- **RAM:** Minimum 4 GB (8 GB recommended for 50MB+ captures).
- **Disk Space:** 500 MB free space for code, dependencies, and SQLite database storage.
- **Display Resolution:** 1280 x 720 minimum (1920 x 1080 optimal for packet inspection grids).

## 5.2 Software Requirements
- **Operating System:** Cross-platform (Windows 10/11, Ubuntu 20.04/22.04 LTS, macOS 12+).
- **Python Runtime:** Python 3.10 to 3.14.
- **Node.js Runtime:** Node.js v18.0+ / v20.0+ with npm v9+.
- **Backend Libraries:**
  - `fastapi` & `uvicorn` (ASGI Web API)
  - `scapy` (PCAP parsing and frame construction)
  - `sqlalchemy` (ORM and transactional data modeling)
  - `reportlab` (PDF document generation)
  - `pydantic` (Data schema validation)
  - `pytest` (Automated regression testing)
- **Frontend Libraries:**
  - `react` 19.x & `react-dom`
  - `typescript` 5.x / 6.x
  - `vite` 8.x
  - `tailwindcss` 4.x
  - `lucide-react` (Cybersecurity vector iconography)
  - `recharts` (Responsive SVG charting)
- **Containerization (Optional):** Docker Engine 24+ & Docker Compose v2+.

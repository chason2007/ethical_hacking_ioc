# Chapter 10: API Documentation

## 10.1 REST Endpoints Reference

### System & Health
- `GET /api/health`
  - Returns service status, operational uptime, and parser engine version.

### Capture Management
- `POST /api/captures/upload`
  - Uploads a `.pcap` or `.pcapng` multipart file for asynchronous parsing and analysis.
- `POST /api/captures/demo`
  - Generates or loads the built-in synthetic PCAP demonstration dataset.
- `GET /api/captures`
  - Retrieves all analyzed captures with summary statistics.
- `GET /api/captures/{id}`
  - Retrieves detailed metadata for a specific capture.
- `DELETE /api/captures/{id}`
  - Deletes a capture and cascades deletion of associated database records.

### Packet Telemetry
- `GET /api/captures/{id}/packets`
  - Query parameters: `page`, `page_size`, `protocol`, `source_ip`, `destination_ip`, `port`, `search`, `sort_by`, `sort_dir`.
  - Returns paginated packet records.
- `GET /api/captures/{id}/packets/{number}`
  - Returns complete packet metadata including the hierarchical `layers_json` tree and hex dump.

### Forensics & Statistics
- `GET /api/captures/{id}/statistics`
  - Returns high-level metrics (packet count, volume, duration, unique IPs, MTU distribution).
- `GET /api/captures/{id}/protocols`
  - Returns protocol breakdown with packet counts, byte volumes, and percentages.
- `GET /api/captures/{id}/conversations`
  - Returns bidirectional conversation flows sorted by packets, bytes, or duration.
- `GET /api/captures/{id}/endpoints`
  - Returns active network endpoints with private/public classification.
- `GET /api/captures/{id}/ports`
  - Returns transport ports mapped to standard IANA service descriptions.
- `GET /api/captures/{id}/dns`
  - Returns DNS analysis (query types, top domains, anomalous queries).
- `GET /api/captures/{id}/http`
  - Returns HTTP methods, response codes, and TLS handshake SNI metadata.
- `GET /api/captures/{id}/security`
  - Returns rule-based security anomaly findings with severity ratings.
- `GET /api/captures/{id}/timeline`
  - Returns time-series telemetry buckets for traffic charts.

### Reporting & Export
- `GET /api/captures/{id}/report`
  - Compiles and downloads an executive PDF security report.
- `GET /api/captures/{id}/export/csv`
  - Streams filtered packets as a downloadable CSV spreadsheet.
- `GET /api/captures/{id}/export/json`
  - Exports the entire structured analysis model as JSON.

# Chapter 9: Database Design

## 9.1 Entity Relationship Model
The data model is implemented via SQLAlchemy ORM, fully compatible with SQLite (default local file) and PostgreSQL (production).

```mermaid
erDiagram
    CAPTURES ||--o{ PACKETS : contains
    CAPTURES ||--o{ ENDPOINTS : identifies
    CAPTURES ||--o{ CONVERSATIONS : tracks
    CAPTURES ||--o{ PROTOCOL_STATS : summarizes
    CAPTURES ||--o{ SECURITY_FINDINGS : flags
    CAPTURES ||--o{ DNS_RECORDS : logs
    CAPTURES ||--o{ HTTP_RECORDS : logs

    CAPTURES {
        string id PK
        string filename
        string filepath
        int file_size_bytes
        int packet_count
        int total_bytes
        float duration_seconds
        string status
        int is_demo
        datetime created_at
    }

    PACKETS {
        int id PK
        string capture_id FK
        int packet_number
        float timestamp
        float relative_time
        string source_ip
        string destination_ip
        string protocol
        int source_port
        int destination_port
        string tcp_flags
        int length
        string info
        text layers_json
    }

    ENDPOINTS {
        int id PK
        string capture_id FK
        string address
        string address_type
        int packets_sent
        int packets_received
        int total_bytes
        boolean is_private
    }

    CONVERSATIONS {
        int id PK
        string capture_id FK
        string protocol
        string endpoint_a
        string endpoint_b
        int port_a
        int port_b
        int total_packets
        int total_bytes
        float duration
    }

    SECURITY_FINDINGS {
        int id PK
        string capture_id FK
        string title
        string severity
        string category
        text evidence
        text why_it_matters
        text recommendation
        string source_ip
    }
```

## 9.2 Database Indexes
To maintain responsive queries across captures with thousands of frames:
- `packets`: Index on `(capture_id, packet_number)` and `(capture_id, protocol, source_ip, destination_ip)`.
- `endpoints`: Index on `(capture_id, address)`.
- `conversations`: Index on `(capture_id, endpoint_a, endpoint_b)`.
- `security_findings`: Index on `capture_id`.

<!--
  README นี้ใช้สำหรับอธิบายระบบ Docker Compose ของโปรเจค Network Monitor
  โดยมี Mermaid diagram แสดงความสัมพันธ์ระหว่าง Flask app, Redis และเป้าหมายที่ ping
-->

# Network Health Monitor with Docker Compose

<!--
  โปรเจคนี้ใช้ Flask เพื่อแสดงหน้า dashboard
  และใช้งาน Redis สำหรับเก็บสถิติการ ping ของแต่ละ target host
-->

This project monitors internet connectivity by sending ICMP ping checks to target hosts and storing uptime statistics in Redis.

## System Architecture

```mermaid
graph TD
    User([User / Browser]) -->|HTTP request on port 5000| App[Network Monitor App<br/>Container 1: Flask + Python]
    App -->|store uptime stats| Redis[(Redis Database<br/>Container 2: redis:alpine)]
    App -.->|ICMP ping test| Target1[8.8.8.8]
    App -.->|ICMP ping test| Target2[1.1.1.1]
    App -.->|ICMP ping test| Target3[google.com]

    classDef app fill:#E3F2FD,stroke:#1E88E5,stroke-width:2px;
    classDef db fill:#E8F5E9,stroke:#43A047,stroke-width:2px;
    class App app;
    class Redis db;
# 💳 BankX — Secure Modular Banking Application on Kubernetes

BankX is a modern, modular, and secure banking application built using **FastAPI** microservices, a **React** frontend, and a comprehensive **Kubernetes** DevSecOps stack. It supports typical banking operations such as user registration, account management, fund transfers, and analytics — all while emphasizing security, scalability, and observability.

---

## 🧱 Architecture Overview
                    +------------------------+
                    |   React Frontend (UI)  |
                    +-----------+------------+
                                |
                                v
                 +-----------------------------+
                 |     API Gateway (FastAPI)    |
                 +-----------------------------+
                                |
  +-----------------------------+-----------------------------+
  |                             |                             |
  v                             v                             v
+-----------+         +------------------+         +----------------------+
|  User     |         |   Account         |         |     Transaction      |
|  Service  |         |   Service         |         |     Service          |
+-----------+         +------------------+         +----------------------+
   |                       |                              |
   v                       v                              v
PostgreSQL             PostgreSQL                     PostgreSQL 

                                |
                                v
                        +------------------+
                        |  Analytics Service |
                        +------------------+
                                |
                                v
                            MongoDB

- **Frontend**: React-based dashboard (Kubernetes Service)
- **API Gateway**: FastAPI-based gateway (NGINX)
- **Microservices**:
  - User Service (PostgreSQL)
  - Account Service (PostgreSQL)
  - Transaction Service (PostgreSQL)
  - Analytics Service (MongoDB)
- **Database Layer**: PostgreSQL, MongoDB
- **Ingress**: NGINX Ingress Controller + TLS (cert-manager)
- **Security & Policies**:
  - NetworkPolicies 
  - Pod Security Policies (Gatekeeper)
- **Monitoring & Logging**:
  - Prometheus + Grafana
  - Falco (Runtime Threat Detection)
- **CI/CD**:
  - GitHub Actions with Trivy for container scanning

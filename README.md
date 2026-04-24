# DappGenius CyberFlow™
**AI-Governed Workflow Intelligence Engine**

DappGenius CyberFlow™ is an AI-powered workflow orchestration and anomaly detection platform designed to help developers generate, execute, and monitor workflows through a unified governance dashboard.

The platform integrates AI-generated workflows, anomaly detection, and system governance monitoring into a single developer-friendly environment.

---

# Features

## AI Workflow Generation
DappGenius can automatically generate workflow models composed of:

- States
- Events
- Transitions
- Domain-specific logic

Example supported domains:

- Cybersecurity event management
- Authentication sessions
- Financial transaction workflows
- Organizational lifecycle workflows

---

## Real-Time Workflow Execution

Developers can programmatically manage workflows using the API:

1. Generate a workflow model
2. Activate the model version
3. Create workflow instances
4. Execute state transitions

Each transition is tracked and logged for governance and anomaly monitoring.

---

## Anomaly Detection Engine

DappGenius includes an anomaly detection module powered by **Isolation Forest**.

The system evaluates workflow transitions based on:

- State index
- Transition timing
- Behavioral patterns

Each transition receives:

- Raw anomaly score
- Normalized score
- Severity classification

Severity categories:

| Severity | Description |
|--------|--------|
| LOW | Normal system behavior |
| MEDIUM | Potential anomaly |
| HIGH | Critical anomaly |

---

## Governance Dashboard

The platform includes a Streamlit-based dashboard for monitoring system activity.

Visualization features include:

- Severity distribution charts
- Workflow anomaly heatmaps
- Anomaly timing heatmaps
- Full audit logs
- Real-time anomaly alerts

These tools allow operators to quickly identify abnormal workflow activity.

---

## Batch Anomaly Scoring

Users can upload CSV datasets to evaluate large volumes of workflow events.

Example CSV format:

workflow_id,state_index,time_delta
abc123,0,0.4
abc123,1,1.8
abc123,2,0.9

The system returns anomaly scores and severity classifications for each record.

---

# System Architecture

DappGenius uses a modular architecture designed for scalability.

Streamlit Dashboard
│
▼
FastAPI API Layer
│
▼
Workflow Engine
│
├── Audit Ledger (SQL Database)
│
└── Anomaly Detection Engine (Isolation Forest)

# Example Use Cases 
1. AI Workflow Governance

Monitor and detect anomalies in automated workflows.

2. Cybersecurity Monitoring

Detect abnormal authentication behavior or suspicious activity patterns.

3. Financial Transaction Monitoring

Identify unusual transaction patterns using anomaly detection.

4. Developer Workflow Automation

Generate and test workflow models programmatically.

5. Project structure 
dappgenius/

backend/
    main.py
    models.py
    anomaly.py
    registry.py
    database.py

frontend/
    streamlit_app.py

static/
    goknown.png

data/
    test_datasets/

docs/
    architecture.md
    workflows.md

requirements.txt
README.md

# Testing 

The system supports multiple testing strategies:

synthetic anomaly datasets

CSV batch scoring

workflow simulation

Test datasets can be generated using provided scripts.


# Roadmap
Planned enhancements include:

Secure Data Room functionality

Two-party crypto payment workflows

Distributed multi-node deployment

Real-time anomaly alerting

Enterprise governance monitoring

# Contributions
Alisa Tiselska
AI Engineer

# Acknowledgements 

This project builds on open-source technologies including:

FastAPI

Streamlit

SQLAlchemy

Plotly

Scikit-learn

# License 
Proprietary software developed by GoKnown LLC


# Learn more
GoKnown LLC
https://www.goknown.com
# CloudSOC: Cloud Security Operations Center

**Automated Threat Detection and Response System for AWS Environments**

[![Status](https://img.shields.io/badge/status-fully%20restored-brightgreen)]()
[![AWS](https://img.shields.io/badge/AWS-CloudTrail%20%7C%20Lambda%20%7C%20EventBridge-orange)]()
[![SIEM](https://img.shields.io/badge/SIEM-ELK%20Stack%208.11.0-blue)]()
[![Cost](https://img.shields.io/badge/cost-%240%2Fmonth-success)]()

---

## Quick Start (5 minutes)

### 1. Start the SIEM
```bash
cd docker
docker-compose up -d
```

### 2. Verify System Health
```bash
cd scripts
python health_check.py
```

### 3. Generate Test Events
```bash
cd attack-simulations
python run_all_simulations.py
```

### 4. View Dashboard
Open browser: **http://localhost:5601**

---

## Project Overview

CloudSOC is a **production-grade Security Operations Center** that monitors AWS environments for threats and responds automatically. It combines:

- **Real-time Detection** (< 30 seconds)
- **Automated Response** (< 5 seconds)
- **Machine Learning** (anomaly detection)
- **Zero Cost** (AWS Free Tier)

### Key Achievements
- ✅ Detects 6 threat categories
- ✅ 100% detection accuracy in testing
- ✅ Sub-5-second automated remediation
- ✅ 588+ security events analyzed
- ✅ ML anomaly scores up to 95% confidence
- ✅ Zero monthly operational cost

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER ACTIVITIES                          │
│         (Console Logins, API Calls, Resource Changes)       │
└────────────────────────┬────────────────────────────────────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    ▼                    ▼                    ▼
┌─────────┐        ┌─────────┐        ┌─────────┐
│CloudTrail│───────▶│EventBridge│─────▶│  Lambda  │
│(Logging)│        │(Filtering)│       │(Detection)│
└─────────┘        └─────────┘        └─────┬─────┘
    │                                        │
    ▼                                        ▼
┌─────────┐                            ┌─────────┐
│   S3    │                            │   SNS   │
│(Storage)│                            │(Alerts) │
76: └────┬────┘                            └─────────┘
     │
     ▼
┌──────────────────────────────────────────────┐
│           LOCAL SIEM (Docker)                │
│  ┌────────┐  ┌────────┐  ┌────────┐         │
│  │Filebeat│─▶│Logstash│─▶│Elastic-│─▶Kibana │
│  │        │  │        │  │search  │  (5601) │
│  └────────┘  └────────┘  └────────┘         │
│                    ML Anomaly Detection      │
└──────────────────────────────────────────────┘
```

---

## Components

### AWS Layer
- **CloudTrail**: Captures all API calls and console actions
- **EventBridge**: Filters events using pattern matching (7 rules)
- **Lambda**: Analyzes threats (5 functions)
- **SNS**: Publishes email alerts
- **S3**: Stores CloudTrail logs (30-day retention)

### Local SIEM (Docker)
- **Elasticsearch**: Search engine and data store
- **Logstash**: Log processing pipeline
- **Kibana**: Dashboard and visualization
- **Filebeat**: Log shipping from S3

### Threat Detection (6 categories)
1. **Brute Force** - Multiple failed logins
2. **Privilege Escalation** - Admin policy attachments
3. **Data Exfiltration** - Suspicious S3 downloads
4. **Root Usage** - Any root account activity
5. **Security Misconfiguration** - Overly permissive firewall rules
6. **ML Anomalies** - Behavioral deviations

### Automated Response
- **Credential Revocation**: Disables compromised access keys
- **EC2 Isolation**: Network isolation of compromised instances

---

## Documentation

| File | Description |
|------|-------------|
| `docs/MACHINE_LEARNING.md` | Details on ML anomaly detection jobs |
| `attack-simulations/README.md` | Guide to running attack simulations |

---

## Directory Structure

```
CloudSOC/
├── attack-simulations/      # Test attack scenarios
│   ├── simulate_brute_force.py
│   ├── simulate_privilege_escalation.py
│   ├── simulate_root_usage.py
│   ├── simulate_data_exfiltration.py
│   └── run_all_simulations.py
│
├── aws-infrastructure/      # Terraform IaC
│   └── terraform/
│       ├── main.tf
│       └── variables.tf
│
├── docker/                  # SIEM configuration
│   ├── docker-compose.yml
│   ├── logstash.conf
│   └── filebeat.yml
│
├── lambda-functions/        # AWS Lambda code
│   ├── detection/
│   │   ├── brute_force_detector.py
│   │   ├── privilege_escalation.py
│   │   └── data_exfiltration.py
│   └── response/
│       ├── ec2_isolation.py
│       └── credential_revocation.py
│
├── scripts/                 # Utilities
│   ├── health_check.py
│   └── test_detection.py
│
└── docs/                    # Documentation
    └── MACHINE_LEARNING.md
```

---

## Prerequisites

### Local Machine
- Docker & Docker Compose
- Python 3.8+ with `requests` library
- 6GB RAM minimum (for Elasticsearch)

### AWS Account
- AWS CLI configured
- CloudTrail enabled
- S3 bucket created
- EventBridge rules configured
- Lambda functions deployed
- SNS topic subscribed

---

## Installation

### 1. Clone/Extract Project
```bash
git clone https://github.com/tejcodes-rex/CloudSOC.git
cd CloudSOC
```

### 2. Start Docker Containers
```bash
cd docker
docker-compose up -d
```

Wait 2-3 minutes for Elasticsearch to initialize.

### 3. Verify System Health
```bash
cd ../scripts
python health_check.py
```

### 4. Deploy AWS Infrastructure (Optional)
```bash
cd ../aws-infrastructure/terraform
terraform init
terraform plan
terraform apply
```

### 5. Deploy Lambda Functions (Optional)
Package and upload Lambda functions via AWS Console or AWS CLI.

---

## Usage

### View Dashboard
```bash
# Open Kibana
open http://localhost:5601
```

1. Navigate to **Dashboard** section
2. Select **CloudSOC Security Dashboard**
3. View event timeline, severity distribution, top event types

### Run Attack Simulations
```bash
cd attack-simulations
python run_all_simulations.py
```

Generates 4 test attack scenarios:
- Brute force (6 failed logins)
- Privilege escalation (AdminAccess attachment)
- Root account usage
- Data exfiltration (10 S3 downloads)

### Check ML Anomalies
```bash
# In Kibana UI:
# 1. Menu → Machine Learning
# 2. Anomaly Detection
# 3. View 3 active jobs
# 4. Click job → View Results
```

---

## Testing

### Quick Test (30 seconds)
```bash
cd scripts
python test_detection.py
```

Sends 4 test events to Elasticsearch.

### Full Test Suite (2 minutes)
```bash
cd attack-simulations
python run_all_simulations.py
```

Runs all attack scenarios and generates comprehensive test data.

---

## Troubleshooting

### Elasticsearch Not Starting
```bash
# Check Docker memory (needs 4GB)
docker stats

# Increase Docker Desktop memory:
# Docker Desktop → Settings → Resources → Memory → 4GB
```

### Kibana Shows "Elasticsearch Unavailable"
Wait 2-3 minutes. Elasticsearch takes time to start.

### No Data in Dashboard
1. Set time range to "Last 7 days"
2. Run attack simulations to generate data
3. Refresh Kibana page

### Check Logs
```bash
docker logs elasticsearch
docker logs logstash
docker logs kibana
docker logs filebeat
```

---

## Performance

| Metric | Value |
|--------|-------|
| Detection Latency | < 30 seconds |
| Response Time | < 5 seconds |
| Detection Accuracy | 100% (in testing) |
| False Positive Rate | 2.1% |
| Events Processed | 588+ |
| ML Anomaly Score | Up to 95/100 |
| Monthly Cost | $0 (AWS Free Tier) |

---

## Technology Stack

- **Cloud**: AWS (CloudTrail, Lambda, EventBridge, SNS, S3, CloudWatch)
- **SIEM**: Elasticsearch, Logstash, Kibana, Filebeat (ELK 8.11.0)
- **ML**: Elasticsearch Machine Learning
- **IaC**: Terraform
- **Containers**: Docker & Docker Compose
- **Language**: Python 3.11

---

## Support

- **Documentation**: See `docs/MACHINE_LEARNING.md`
- **Simulation Guide**: See `attack-simulations/README.md`
- **Troubleshooting**: See sections above.

---

## Status

✅ **Project Status**: Stable
✅ **Ready for**: Deployment, Testing, Demonstration

Last Updated: November 2025

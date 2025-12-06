# CloudSOC Attack Simulations

This directory contains Python scripts that simulate various security attacks to test CloudSOC's detection capabilities.

## Prerequisites

```bash
pip install requests
```

Ensure Elasticsearch is running:
```bash
cd ../docker
docker-compose up -d
```

## Available Simulations

### 1. Brute Force Attack
**Script:** `simulate_brute_force.py`

Generates 6 failed console login attempts from the same IP address.

```bash
python simulate_brute_force.py
```

**Expected Detection:**
- High severity events in Kibana
- Brute force threat classification
- Potential EventBridge alert (if configured)

---

### 2. Privilege Escalation
**Script:** `simulate_privilege_escalation.py`

Simulates attaching AdministratorAccess policy to a user account.

```bash
python simulate_privilege_escalation.py
```

**Expected Detection:**
- CRITICAL severity event
- Immediate alert recommended
- Credential revocation suggested

---

### 3. Root Account Usage
**Script:** `simulate_root_usage.py`

Generates root account activity (always critical).

```bash
python simulate_root_usage.py
```

**Expected Detection:**
- CRITICAL severity
- Root usage should NEVER occur in production
- Immediate investigation required

---

### 4. Data Exfiltration
**Script:** `simulate_data_exfiltration.py`

Simulates suspicious pattern of downloading sensitive S3 objects.

```bash
python simulate_data_exfiltration.py
```

**Expected Detection:**
- High volume S3 GetObject events
- Pattern indicates potential data theft
- Manual review recommended

---

## Run All Simulations

To run all attack scenarios in sequence:

```bash
python run_all_simulations.py
```

This will:
- Execute all 4 attack simulations
- Wait 5 seconds between each
- Generate comprehensive test data
- Provide summary at completion

## Viewing Results

After running simulations:

1. **Open Kibana Dashboard**
   ```
   http://localhost:5601
   ```

2. **Go to Discover**
   - Set index pattern: `cloudsoc-logs-*`
   - Set time range: "Last 24 hours"
   - Filter by `severity: high` or `severity: critical`

3. **View Security Dashboard**
   - Navigate to Dashboard section
   - Select "CloudSOC Security Dashboard"
   - Review severity distribution and event timeline

4. **Check ML Anomalies** (wait 15 minutes after simulation)
   - Menu → Machine Learning → Anomaly Detection
   - Look for anomaly scores > 75

## Customization

Each script accepts parameters:

```python
# Brute force with custom IP and count
simulate_failed_logins(count=10, attacker_ip="1.2.3.4")

# Privilege escalation with custom user
simulate_privilege_escalation(target_user="my-user", attacker_ip="1.2.3.4")

# Root usage with custom action
simulate_root_usage(action="CreateUser", source_ip="1.2.3.4")

# Data exfiltration with custom bucket
simulate_data_exfiltration(bucket="my-sensitive-data", count=20)
```

## Notes

- These scripts send events directly to Elasticsearch
- They do NOT interact with actual AWS resources
- Safe to run repeatedly for testing
- Events are timestamped with current time
- Index pattern: `cloudsoc-logs-YYYY.MM.DD`

## Troubleshooting

**"Connection refused" error:**
- Verify Elasticsearch is running: `docker ps`
- Check Elasticsearch is accessible: `curl http://localhost:9200`

**Events not appearing in Kibana:**
- Refresh Kibana Discover page
- Check time range is set correctly (last 24 hours)
- Verify index pattern `cloudsoc-logs-*` exists

**No ML anomalies detected:**
- ML jobs run every 15 minutes
- Wait at least 15 minutes after generating events
- Ensure ML jobs are started in Kibana ML section

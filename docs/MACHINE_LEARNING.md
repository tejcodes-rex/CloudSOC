# Machine Learning in CloudSOC

## Overview

CloudSOC integrates Elasticsearch Machine Learning to detect anomalies that static rules cannot catch. By learning normal behavior patterns, the system automatically flags deviations, such as unusual API call volumes or access times, which often indicate sophisticated attacks like insider threats or zero-day exploits.

## Detected Anomalies

The system currently runs 3 active ML jobs:

### 1. Rare Events Detector
*   **Purpose**: Detects unusual AWS API calls that are rarely or never seen for a specific user.
*   **Example**: A developer account suddenly accessing KMS keys or changing IAM policies.

### 2. Severity Spike Detector
*   **Purpose**: Detects statistical surges in high-severity events.
*   **Example**: A sudden spike from 5 daily high-severity logs to 50 in one hour.

### 3. Failed Login Spike Detector
*   **Purpose**: Detects brute force patterns that may bypass static thresholds.
*   **Example**: 20 failed logins from a single IP where the baseline is 1-2.

## Anomaly Scoring

Elasticsearch assigns a normalized anomaly score (0-100) to each event:

*   **0-25**: Normal behavior
*   **25-50**: Minor anomaly
*   **50-75**: Warning
*   **75-100**: **CRITICAL** (Highly likely to be malicious)

> **Note**: A score of 87+ implies less than 0.01% probability that the event is normal.

## Rules vs. Machine Learning

| Feature | Static Rules | Machine Learning | CloudSOC Approach |
| :--- | :--- | :--- | :--- |
| **Known Threats** | ✅ Excellent | ✅ Good | **Combined** |
| **Unknown Threats** | ❌ Cannot detect | ✅ Excellent | **ML Only** |
| **Context Awareness** | ❌ Static thresholds | ✅ Dynamic baselines | **ML Only** |
| **Response Time** | Fast (< 30s) | Batch (15 min) | **Combined** |

## Implementation Details

*   **Engine**: Elasticsearch Machine Learning (X-Pack)
*   **Schedule**: Jobs run every 15 minutes
*   **Data Source**: CloudTrail logs via Logstash

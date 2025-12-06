"""
CloudSOC System Health Check
Verifies that all components are running and accessible.
"""

import requests
import subprocess
import sys
from datetime import datetime

def print_header(text):
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")

def check_docker_containers():
    """Check status of Docker containers."""
    print_header("DOCKER CONTAINERS")

    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(result.stdout)
            cloudsoc_containers = ['elasticsearch', 'logstash', 'kibana', 'filebeat']
            running_containers = result.stdout.lower()

            all_running = all(container in running_containers for container in cloudsoc_containers)

            if all_running:
                print("[✓] All CloudSOC containers are running")
                return True
            else:
                missing = [c for c in cloudsoc_containers if c not in running_containers]
                print(f"[✗] Missing containers: {', '.join(missing)}")
                return False
        else:
            print("[✗] Docker command failed. Is Docker running?")
            return False

    except FileNotFoundError:
        print("[✗] Docker not found. Please install Docker.")
        return False
    except Exception as e:
        print(f"[✗] Error checking Docker: {e}")
        return False

def check_elasticsearch():
    """Check Elasticsearch health."""
    print_header("ELASTICSEARCH")

    try:
        response = requests.get("http://localhost:9200/_cluster/health", timeout=5)

        if response.status_code == 200:
            health = response.json()
            status = health.get('status', 'unknown')
            nodes = health.get('number_of_nodes', 0)
            indices = health.get('active_primary_shards', 0)

            print(f"Status: {status}")
            print(f"Nodes: {nodes}")
            print(f"Active Indices: {indices}")

            if status in ['green', 'yellow']:
                print(f"[✓] Elasticsearch is {status}")
                return True
            else:
                print(f"[✗] Elasticsearch status is {status}")
                return False
        else:
            print(f"[✗] Elasticsearch returned status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("[✗] Cannot connect to Elasticsearch at http://localhost:9200")
        print("    Make sure the container is running and port 9200 is exposed")
        return False
    except Exception as e:
        print(f"[✗] Error checking Elasticsearch: {e}")
        return False

def check_kibana():
    """Check Kibana health."""
    print_header("KIBANA")

    try:
        response = requests.get("http://localhost:5601/api/status", timeout=10)

        if response.status_code == 200:
            status_data = response.json()
            overall_status = status_data.get('status', {}).get('overall', {}).get('level', 'unknown')

            print(f"Status: {overall_status}")
            print(f"URL: http://localhost:5601")

            if overall_status == 'available':
                print(f"[✓] Kibana is available")
                return True
            else:
                print(f"[✗] Kibana status is {overall_status}")
                return False
        else:
            print(f"[✗] Kibana returned status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("[✗] Cannot connect to Kibana at http://localhost:5601")
        print("    Kibana may still be starting up (can take 2-3 minutes)")
        return False
    except Exception as e:
        print(f"[✗] Error checking Kibana: {e}")
        return False

def check_logstash():
    """Check Logstash health."""
    print_header("LOGSTASH")

    try:
        response = requests.get("http://localhost:9600/_node/stats", timeout=5)

        if response.status_code == 200:
            stats = response.json()
            pipeline = stats.get('pipelines', {})

            print(f"Pipelines configured: {len(pipeline)}")
            print(f"Status: Running")
            print(f"[✓] Logstash is operational")
            return True
        else:
            print(f"[✗] Logstash returned status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("[✗] Cannot connect to Logstash at http://localhost:9600")
        print("    Check if logstash container is running")
        return False
    except Exception as e:
        print(f"[✗] Error checking Logstash: {e}")
        return False

def check_indices():
    """Check CloudSOC indices in Elasticsearch."""
    print_header("ELASTICSEARCH INDICES")

    try:
        response = requests.get("http://localhost:9200/_cat/indices/cloudsoc-*?v", timeout=5)

        if response.status_code == 200:
            indices_output = response.text.strip()

            if indices_output:
                print(indices_output)
                lines = indices_output.split('\n')
                index_count = len(lines) - 1
                print(f"\n[✓] Found {index_count} CloudSOC index/indices")
                return True
            else:
                print("[!] No CloudSOC indices found")
                print("    This is normal for a fresh installation")
                print("    Run attack simulations to generate data")
                return True

        else:
            print(f"[✗] Failed to retrieve indices (status {response.status_code})")
            return False

    except Exception as e:
        print(f"[✗] Error checking indices: {e}")
        return False

def check_document_count():
    """Check total document count in CloudSOC indices."""
    print_header("DOCUMENT COUNT")

    try:
        response = requests.get("http://localhost:9200/cloudsoc-*/_count", timeout=5)

        if response.status_code == 200:
            count_data = response.json()
            doc_count = count_data.get('count', 0)

            print(f"Total security events indexed: {doc_count:,}")

            if doc_count > 0:
                print(f"[✓] CloudSOC has indexed {doc_count} events")
                return True
            else:
                print("[!] No events indexed yet")
                print("    Run attack simulations to generate test data")
                return True
        else:
            print(f"[✗] Failed to count documents")
            return False

    except Exception as e:
        print(f"[✗] Error counting documents: {e}")
        return False

def print_summary(checks):
    """Print overall health summary."""
    print_header("HEALTH CHECK SUMMARY")

    total = len(checks)
    passed = sum(checks.values())
    failed = total - passed

    print(f"Total checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print(f"\n[✓] ALL SYSTEMS OPERATIONAL")
        print(f"\nCloudSOC is ready to use!")
        print(f"  - Kibana Dashboard: http://localhost:5601")
        print(f"  - Elasticsearch API: http://localhost:9200")
    else:
        print(f"\n[✗] SOME CHECKS FAILED")
        print(f"\nTroubleshooting:")
        print(f"  1. Ensure Docker is running: docker ps")
        print(f"  2. Start containers: cd CloudSOC/docker && docker-compose up -d")
        print(f"  3. Check logs: docker logs [container-name]")
        print(f"  4. Wait 2-3 minutes for services to fully start")

    return failed == 0

def main():
    """Run all health checks."""
    print("\n")
    print(f"{'#'*70}")
    print(f"#  CloudSOC Health Check")
    print(f"#  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*70}")

    checks = {
        'docker': check_docker_containers(),
        'elasticsearch': check_elasticsearch(),
        'kibana': check_kibana(),
        'logstash': check_logstash(),
        'indices': check_indices(),
        'documents': check_document_count()
    }

    all_healthy = print_summary(checks)

    sys.exit(0 if all_healthy else 1)

if __name__ == "__main__":
    main()

import requests
import time

def check_status():
    url = "https://api.github.com/repos/viraj0710/loan-approval-mlops/actions/runs"
    for attempt in range(20):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                print(f"API HTTP {r.status_code}: {r.text[:200]}")
                time.sleep(10)
                continue
            data = r.json()
            runs = data.get("workflow_runs", [])
            if not runs:
                print("No runs detected yet. Waiting...")
                time.sleep(5)
                continue

            latest = runs[0]
            status = latest.get("status")
            conclusion = latest.get("conclusion")
            name = latest.get("name")
            html_url = latest.get("html_url")
            print(f"[Attempt {attempt+1}] Run: {name} | Status: {status} | Conclusion: {conclusion} | URL: {html_url}")

            if status == "completed":
                print(f"Workflow finished with conclusion: {conclusion}")
                return conclusion == "success"
        except Exception as e:
            print(f"Exception: {e}")
        time.sleep(10)
    return False

if __name__ == "__main__":
    check_status()


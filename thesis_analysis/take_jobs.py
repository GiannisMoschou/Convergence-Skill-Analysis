import os
from dotenv import load_dotenv
import requests as req
import pandas as pd
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

API = "https://skillab-tracker.csd.auth.gr/api"
USERNAME = os.getenv("API_USERNAME")
PASSWORD = os.getenv("API_PASSWORD")


session = req.Session()
retries = Retry(total=5, backoff_factor=2, status_forcelist=[500, 502, 503, 504], allowed_methods=["POST", "GET"])
session.mount('https://', HTTPAdapter(max_retries=retries))
session.mount('http://', HTTPAdapter(max_retries=retries))

def get_token() -> str:
    try:
        res = session.post(f"{API}/login", json={"username": USERNAME, "password": PASSWORD}, verify=False, timeout=30)
        res.raise_for_status()
        return res.text.replace('"', "")
    except Exception as e:
        print(f"Login failed: {e}")
        exit(1)

token = get_token()
headers = {
    "accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Bearer {token}"
}

# Monthly intervals
start_date = datetime(2020, 1, 1)
end_date = datetime(2025, 6, 1)
# Ensure interval_months is always defined (use existing global if present, otherwise default to 1)
interval_months = globals().get('interval_months', 1)
jobs_per_interval = 2000
all_jobs = []

# Helper: add N months to a date
def add_months(dt, months):
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, 28)  # Keeps the day in safe range
    return datetime(year, month, day)

current = start_date
while current < end_date:
    interval_start = current.strftime('%Y-%m-%d')
    interval_end = add_months(current, interval_months) - timedelta(days=1)
    if interval_end > end_date:
        interval_end = end_date
    interval_end_str = interval_end.strftime('%Y-%m-%d')

    collected = 0
    page = 1
    interval_jobs = []
    seen_ids = set() # Track IDs for this interval to prevent duplicates

    while collected < jobs_per_interval:
        query_params = {
            "page": str(page),
            "page_size": "100"
        }
        form_data = {
            "sources": "OJA",
            "min_upload_date": interval_start,
            "max_upload_date": interval_end_str
        }
        print(f"  Fetching page {page} (collected: {collected})...")
        try:
            response = session.post(f"{API}/jobs", headers=headers, data=form_data, params=query_params, verify=False, timeout=30)
        except Exception as e:
            print(f"  Request error after retries: {e}")
            break

        if response.status_code != 200:
            print(f"Request failed for interval {interval_start} to {interval_end_str} at page {page}")
            break
        data = response.json()
        items = data.get("items", [])
        if not items:
            break
        
        new_items = []
        for item in items:
            job_id = item.get('id')
            if job_id and job_id not in seen_ids:
                seen_ids.add(job_id)
                new_items.append(item)
        
        if not new_items:
            print(f"  Warning: No new unique items found on page {page}. Stopping interval.")
            break
            
        interval_jobs.extend(new_items)
        collected = len(interval_jobs)
        
        # If we got fewer items than requested, we likely hit the end
        if len(items) < 100:
            break
        page += 1

    # Only keep up to jobs_per_interval
    all_jobs.extend(interval_jobs[:jobs_per_interval])
    print(f"Interval {interval_start} to {interval_end_str}: {len(interval_jobs[:jobs_per_interval])} jobs collected.")
    current = add_months(current, interval_months) # Move to next interval

df = pd.DataFrame(all_jobs)
df.to_csv("jobs_monthly_2020_2025.csv", index=False)
#!/usr/bin/env python3
"""
Commute Dashboard - Text Interface
Fetches real-time transit data from 511.org via proxy
"""

import json
import urllib.request
import urllib.error
from datetime import datetime

PROXY_URL = "https://round-heart-428a.infraredhammerhead.workers.dev"

# Stop configurations
STOPS = {
    "vta": {"agency": "SC", "stop": "64818", "name": "Middlefield LRT"},
    "caltrain": {"agency": "CT", "stop": "70211", "name": "Mountain View NB"},
}


def fetch_arrivals(agency: str, stop_code: str) -> dict:
    """Fetch arrivals from the proxy."""
    url = f"{PROXY_URL}?agency={agency}&stopCode={stop_code}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read().decode('utf-8-sig')  # Handle BOM
            return json.loads(data)
    except urllib.error.URLError as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse error: {e}"}


def parse_arrivals(data: dict) -> list:
    """Extract arrival info from API response."""
    arrivals = []
    try:
        visits = (data.get("ServiceDelivery", {})
                     .get("StopMonitoringDelivery", {})
                     .get("MonitoredStopVisit", []))

        for visit in visits[:5]:
            journey = visit.get("MonitoredVehicleJourney", {})
            call = journey.get("MonitoredCall", {})

            line = journey.get("PublishedLineName", journey.get("LineRef", "?"))
            dest = journey.get("DestinationName", "Unknown")
            expected = call.get("ExpectedArrivalTime") or call.get("ExpectedDepartureTime", "")

            mins = format_minutes(expected)
            arrivals.append({"line": line, "dest": dest, "mins": mins})
    except Exception as e:
        return [{"error": str(e)}]

    return arrivals


def format_minutes(iso_time: str) -> str:
    """Convert ISO timestamp to minutes until arrival."""
    if not iso_time:
        return "?"
    try:
        # Parse ISO format
        expected = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
        now = datetime.now(expected.tzinfo)
        diff = (expected - now).total_seconds() / 60

        if diff < 1:
            return "Now"
        elif diff < 60:
            return f"{int(diff)}m"
        else:
            return expected.strftime("%H:%M")
    except:
        return "?"


def print_arrivals(name: str, arrivals: list):
    """Print arrivals in a clean text format."""
    print(f"\n=== {name} ===")
    if not arrivals:
        print("  No arrivals")
        return

    if arrivals and "error" in arrivals[0]:
        print(f"  Error: {arrivals[0]['error']}")
        return

    for arr in arrivals:
        line = arr["line"][:12].ljust(12)
        dest = arr["dest"][:25].ljust(25)
        mins = arr["mins"].rjust(6)
        print(f"  {line} {dest} {mins}")


def main():
    print("=" * 50)
    print("COMMUTE DASHBOARD")
    print(f"Updated: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)

    for key, config in STOPS.items():
        data = fetch_arrivals(config["agency"], config["stop"])
        if "error" in data:
            print(f"\n=== {config['name']} ===")
            print(f"  Error: {data['error']}")
        else:
            arrivals = parse_arrivals(data)
            print_arrivals(config["name"], arrivals)

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()

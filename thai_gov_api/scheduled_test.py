import requests
import xml.etree.ElementTree as ET
import csv
from datetime import datetime
import os
import schedule
import time

# Config
url = "https://data.tmd.go.th/api/Weather3Hours/V2/?uid=api&ukey=api12345"
target_wmo = "48455"
csv_file = "weather_data.csv"

def fetch_and_save():
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        stations_node = root.find("Stations")
        if stations_node is None:
            print("❌ No <Stations> element found in XML.")
            return

        found = False
        for station in stations_node.findall("Station"):
            wmo = station.findtext("WmoStationNumber")
            if wmo == target_wmo:
                found = True

                obs = station.find("Observation")
                if obs is None:
                    print("⚠️ No observation data found.")
                    return

                # Extract data
                data = {
                    "DateTime": obs.findtext("DateTime", ""),
                    "StationID": wmo,
                    "StationName": station.findtext("StationNameEnglish", ""),
                    "Province": station.findtext("Province", ""),
                    "Latitude": station.findtext("Latitude", ""),
                    "Longitude": station.findtext("Longitude", ""),
                    "StationPressure": obs.findtext("StationPressure", ""),
                    "MeanSeaLevelPressure": obs.findtext("MeanSeaLevelPressure", ""),
                    "AirTemperature": obs.findtext("AirTemperature", ""),
                    "DewPoint": obs.findtext("DewPoint", ""),
                    "RelativeHumidity": obs.findtext("RelativeHumidity", ""),
                    "VaporPressure": obs.findtext("VaporPressure", ""),
                    "LandVisibility": obs.findtext("LandVisibility", ""),
                    "WindDirection": obs.findtext("WindDirection", ""),
                    "WindSpeed": obs.findtext("WindSpeed", ""),
                    "Rainfall": obs.findtext("Rainfall", ""),
                    "Rainfall24Hr": obs.findtext("Rainfall24Hr", "")
                }

                # Check if file exists to write header
                file_exists = os.path.isfile(csv_file)

                with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=list(data.keys()))
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow(data)

                print(f"✅ Data for station {wmo} saved at {datetime.now()}")
                break

        if not found:
            print(f"❌ Station with WMO {target_wmo} not found.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch data: {e}")

    except ET.ParseError as e:
        print(f"❌ Failed to parse XML: {e}")

def job():
    print(f"Job started at {datetime.now()}")
    fetch_and_save()
    print(f"Job finished at {datetime.now()}")

if __name__ == "__main__":
    # Run once immediately when script starts
    job()

    # Schedule job every 3 hours
    schedule.every(3).hours.do(job)

    print("Scheduler started. Running every 3 hours...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # check every minute

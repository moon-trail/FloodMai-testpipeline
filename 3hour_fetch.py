import requests
import xml.etree.ElementTree as ET
import csv
from datetime import datetime
import os
import schedule
import time
import pytz  # for timezone awareness

# Config
url = "https://data.tmd.go.th/api/Weather3Hours/V2/?uid=api&ukey=api12345"
target_wmo = "48455"
csv_file = "3hourweather_data.csv"
tz = pytz.timezone("Asia/Bangkok")

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

                now = datetime.now(tz)
                print(f"✅ Data for station {wmo} saved at {now.strftime('%Y-%m-%d %H:%M:%S')} Bangkok time")
                break

        if not found:
            print(f"❌ Station with WMO {target_wmo} not found.")

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch data: {e}")

    except ET.ParseError as e:
        print(f"❌ Failed to parse XML: {e}")

def job():
    now = datetime.now(tz)
    print(f"⏰ Job started at {now.strftime('%Y-%m-%d %H:%M:%S')} Bangkok time")
    fetch_and_save()

if __name__ == "__main__":
    # Schedule job at specific hours in Bangkok time
    times = ["01:00", "04:00", "07:00", "10:00", "13:00", "16:00", "19:00", "22:00"]
    for t in times:
        schedule.every().day.at(t).do(job)

    print("📅 Scheduler started. Will run job at:")
    for t in times:
        print(f" - {t} (Bangkok time)")

    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds

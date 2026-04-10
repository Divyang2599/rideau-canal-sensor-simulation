import os
import json
import time
import random
import threading
from datetime import datetime, timezone
from pathlib import Path
from azure.iot.device import IoTHubDeviceClient, Message
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

with open(Path(__file__).parent / "config/sensor_config.json", "r") as f:
    config = json.load(f)

SEND_INTERVAL = config["send_interval_seconds"]

DEVICE_CONFIG = {
    "dows-lake": {
        "connection_string": os.getenv("IOTHUB_DEVICE_CONNECTION_STRING_DOWS_LAKE"),
        "display_name": "Dow's Lake"
    },
    "fifth-avenue": {
        "connection_string": os.getenv("IOTHUB_DEVICE_CONNECTION_STRING_FIFTH_AVE"),
        "display_name": "Fifth Avenue"
    },
    "nac": {
        "connection_string": os.getenv("IOTHUB_DEVICE_CONNECTION_STRING_NAC"),
        "display_name": "NAC"
    }
}


def generate_sensor_reading(location_key):
    loc_config = config["locations"][location_key]
    ice_thickness = round(random.uniform(*loc_config["ice_thickness_range"]), 1)
    surface_temp = round(random.uniform(*loc_config["surface_temp_range"]), 1)
    snow_accumulation = round(random.uniform(*loc_config["snow_accumulation_range"]), 1)
    external_temp = round(random.uniform(*loc_config["external_temp_range"]), 1)

    if ice_thickness >= 30 and surface_temp <= -2:
        safety_status = "Safe"
    elif ice_thickness >= 25 and surface_temp <= 0:
        safety_status = "Caution"
    else:
        safety_status = "Unsafe"

    return {
        "deviceId": f"{location_key}-sensor",
        "location": location_key,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "iceThickness": ice_thickness,
        "surfaceTemperature": surface_temp,
        "snowAccumulation": snow_accumulation,
        "externalTemperature": external_temp,
        "safetyStatus": safety_status
    }


def run_sensor(location_key, device_info):
    conn_str = device_info["connection_string"]
    display_name = device_info["display_name"]

    if not conn_str:
        print(f"[ERROR] No connection string found for {display_name}. Check your .env file.")
        return

    print(f"[{display_name}] Connecting to IoT Hub...")
    client = IoTHubDeviceClient.create_from_connection_string(conn_str)
    client.connect()
    print(f"[{display_name}] Connected. Sending data every {SEND_INTERVAL} seconds.")

    try:
        while True:
            reading = generate_sensor_reading(location_key)
            message_body = json.dumps(reading)
            message = Message(message_body)
            message.content_encoding = "utf-8"
            message.content_type = "application/json"
            client.send_message(message)
            print(f"[{display_name}] Sent: Ice={reading['iceThickness']}cm | "
                  f"SurfaceTemp={reading['surfaceTemperature']}°C | "
                  f"Snow={reading['snowAccumulation']}cm | "
                  f"Status={reading['safetyStatus']}")
            time.sleep(SEND_INTERVAL)

    except KeyboardInterrupt:
        print(f"[{display_name}] Stopping.")
    finally:
        client.disconnect()
        print(f"[{display_name}] Disconnected.")


def main():
    print("=" * 60)
    print("  Rideau Canal Skateway - IoT Sensor Simulator")
    print("  Locations: Dow's Lake | Fifth Avenue | NAC")
    print("=" * 60)

    threads = []
    for location_key, device_info in DEVICE_CONFIG.items():
        t = threading.Thread(
            target=run_sensor,
            args=(location_key, device_info),
            daemon=True
        )
        threads.append(t)
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[MAIN] Shutting down all sensors. Goodbye.")


if __name__ == "__main__":
    main()
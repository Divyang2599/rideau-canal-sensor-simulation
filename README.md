# Rideau Canal Sensor Simulator

This is the IoT sensor simulator for the Rideau Canal Skateway monitoring project.
It pretends to be 3 physical sensors placed at different locations along the canal and sends fake-but-realistic sensor readings to Azure IoT Hub every 10 seconds.

---

## What It Does

- Connects 3 devices to Azure IoT Hub simultaneously
- Each device runs in its own thread (they send data independently, just like real sensors would)
- Generates random but realistic values for ice thickness, surface temperature, snow accumulation, and external temperature
- Each location has its own realistic ranges (NAC is more sheltered, Dow's Lake is more exposed)
- Calculates a safety status for each reading and includes it in the message

---

## Technologies Used

- Python 3.x
- `azure-iot-device` - connects to Azure IoT Hub and sends messages
- `python-dotenv` - loads connection strings from a `.env` file safely
- `threading` - runs all 3 sensors at the same time

---

## Prerequisites

- Python 3.8 or higher
- An Azure IoT Hub with 3 registered devices
- The 3 device connection strings

---

## Installation

```bash
# Clone the repo
git clone https://github.com/Divyang2599/rideau-canal-sensor-simulation.git
cd rideau-canal-sensor-simulation

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Copy `.env.example` to a new file called `.env`:

```bash
cp .env.example .env
```

Open `.env` and replace the placeholders with your real device connection strings from Azure IoT Hub:

```
IOTHUB_DEVICE_CONNECTION_STRING_DOWS_LAKE=HostName=...
IOTHUB_DEVICE_CONNECTION_STRING_FIFTH_AVE=HostName=...
IOTHUB_DEVICE_CONNECTION_STRING_NAC=HostName=...
```

To get these strings: Azure Portal → IoT Hub → Devices → click each device → copy Primary Connection String.

**Never commit your `.env` file.** It is already in `.gitignore`.

---

## Usage

```bash
# Make sure venv is activated
venv\Scripts\activate

# Run the simulator
python sensor_simulator.py
```

You will see output like this:

```
Rideau Canal Skateway - IoT Sensor Simulator
Locations: Dow's Lake | Fifth Avenue | NAC

[Dow's Lake] Connecting to IoT Hub...
[Dow's Lake] Connected. Sending data every 10 seconds.
[Dow's Lake] Sent: Ice=33.7cm | SurfaceTemp=-6.5°C | Snow=12.1cm | Status=Safe
```

Press `Ctrl+C` to stop.

---

## Sensor Data Format

Each message sent to IoT Hub is a JSON object:

```json
{
  "deviceId": "dows-lake-sensor",
  "location": "dows-lake",
  "timestamp": "2026-04-10T00:26:34.123456+00:00",
  "iceThickness": 33.7,
  "surfaceTemperature": -6.5,
  "snowAccumulation": 12.1,
  "externalTemperature": -9.6,
  "safetyStatus": "Safe"
}
```

---

## Code Structure

| File | Purpose |
| :--- | :--- |
| `sensor_simulator.py` | Main script — connects devices and sends data |
| `config/sensor_config.json` | Defines value ranges per location and send interval |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template showing required environment variables |
| `.env` | Your real secrets — never committed to git |

---

## Troubleshooting

**Error: No connection string found**  
Your `.env` file is missing or has wrong variable names. Check spelling exactly matches `.env.example`.

**Error: Invalid Connection String**  
The value in `.env` has extra spaces or line breaks. Make sure each connection string is on one single line.

**Error: Connection refused / timeout**  
Check your internet connection. Also verify the device exists in IoT Hub and the connection string is current (not regenerated after you copied it).

#!/usr/bin/env python3

import time

import requests

from hardware.moisture_sensor import MoistureSensor


def send_data_to_api(data: dict) -> None:
    """Send sensor data to Flask API"""
    try:
        requests.post('http://localhost:8765/api/sensor-data', json=data)
    except requests.exceptions.RequestException as e:
        print(f"Error sending data: {e}")


def main():
    sensor = MoistureSensor(channel=3)
    print("Starting moisture monitoring system...")

    try:
        while True:
            raw, voltage = sensor.read_values()
            moisture, status = sensor.get_moisture_status()

            data = {
                'timestamp': time.time(),
                'raw': raw,
                'voltage': round(voltage, 2),
                'moisture': round(moisture, 1),
                'status': status
            }

            send_data_to_api(data)
            time.sleep(1)  # Update every 2 seconds

    except KeyboardInterrupt:
        print("\nProgram terminated by user")


if __name__ == "__main__":
    main()

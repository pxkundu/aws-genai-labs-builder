#!/usr/bin/env python3
"""
AWS IoT Device Simulator

Simulates IoT devices publishing telemetry to AWS IoT Core.
Supports multiple device types, shadow updates, and configurable publishing intervals.

Usage:
    python device_simulator.py --endpoint <iot-endpoint> --cert <cert.pem> --key <key.pem> --root-ca <root-ca.pem> --thing-name <thing-name>
"""

import argparse
import json
import random
import time
import sys
from datetime import datetime
from typing import Dict, Any

try:
    import boto3
    from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Install with: pip install boto3 AWSIoTPythonSDK")
    sys.exit(1)


class IoTDeviceSimulator:
    """Simulates an IoT device publishing telemetry to AWS IoT Core."""

    def __init__(self, endpoint: str, cert_path: str, key_path: str, root_ca_path: str, thing_name: str):
        self.endpoint = endpoint
        self.cert_path = cert_path
        self.key_path = key_path
        self.root_ca_path = root_ca_path
        self.thing_name = thing_name
        self.client = None
        self.running = False

    def connect(self):
        """Establish MQTT connection to AWS IoT Core."""
        self.client = AWSIoTMQTTClient(self.thing_name)
        self.client.configureEndpoint(self.endpoint, 8883)
        self.client.configureCredentials(self.root_ca_path, self.key_path, self.cert_path)
        self.client.configureAutoReconnectBackoffTime(1, 32, 20)
        self.client.configureOfflinePublishQueueing(-1)
        self.client.configureDrainingFrequency(2)
        self.client.configureConnectDisconnectTimeout(10)
        self.client.configureMQTTOperationTimeout(5)

        print(f"Connecting to {self.endpoint}...")
        self.client.connect()
        print("Connected successfully!")

    def disconnect(self):
        """Disconnect from AWS IoT Core."""
        if self.client:
            self.client.disconnect()
            print("Disconnected.")

    def generate_telemetry(self, device_type: str = "sensor") -> Dict[str, Any]:
        """Generate sample telemetry based on device type."""
        base_payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "deviceId": self.thing_name,
            "deviceType": device_type
        }

        if device_type == "temperature_sensor":
            base_payload.update({
                "temperature": round(random.uniform(18.0, 35.0), 2),
                "humidity": round(random.uniform(30.0, 80.0), 2),
                "pressure": round(random.uniform(980.0, 1020.0), 2),
                "status": "ok"
            })
        elif device_type == "industrial":
            base_payload.update({
                "rpm": random.randint(1000, 5000),
                "vibration": round(random.uniform(0.1, 5.0), 3),
                "temperature": round(random.uniform(20.0, 85.0), 2),
                "pressure": round(random.uniform(1.0, 10.0), 2),
                "status": random.choice(["ok", "warning", "critical"])
            })
        elif device_type == "vehicle":
            base_payload.update({
                "speed": random.randint(0, 120),
                "fuelLevel": round(random.uniform(10.0, 100.0), 2),
                "engineTemp": round(random.uniform(80.0, 110.0), 2),
                "latitude": round(random.uniform(-90.0, 90.0), 6),
                "longitude": round(random.uniform(-180.0, 180.0), 6),
                "status": "running"
            })
        else:  # generic sensor
            base_payload.update({
                "value": round(random.uniform(0.0, 100.0), 2),
                "unit": "generic",
                "status": "ok"
            })

        return base_payload

    def publish_telemetry(self, topic: str, payload: Dict[str, Any], qos: int = 1):
        """Publish telemetry to a topic."""
        message = json.dumps(payload)
        self.client.publish(topic, message, qos)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Published to {topic}: {payload.get('deviceType', 'unknown')}")

    def update_shadow(self, desired_state: Dict[str, Any]):
        """Update device shadow desired state."""
        shadow_payload = {
            "state": {
                "desired": desired_state
            }
        }
        topic = f"$aws/things/{self.thing_name}/shadow/update"
        message = json.dumps(shadow_payload)
        self.client.publish(topic, message, 1)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Updated shadow desired state: {desired_state}")

    def simulate_continuous(self, device_type: str, topic: str, interval: float = 5.0, duration: int = None):
        """Continuously publish telemetry at specified interval."""
        self.running = True
        start_time = time.time()
        count = 0

        print(f"Starting simulation: {device_type} device, interval={interval}s, topic={topic}")
        if duration:
            print(f"Will run for {duration} seconds")

        try:
            while self.running:
                payload = self.generate_telemetry(device_type)
                self.publish_telemetry(topic, payload)
                count += 1

                if duration and (time.time() - start_time) >= duration:
                    break

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nSimulation stopped by user")
        finally:
            print(f"\nPublished {count} messages total")
            self.running = False

    def simulate_anomaly(self, topic: str):
        """Simulate an anomaly (e.g., high temperature) for testing IoT Events."""
        print("Simulating anomaly...")
        anomaly_payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "deviceId": self.thing_name,
            "deviceType": "temperature_sensor",
            "temperature": 95.0,  # High temperature to trigger IoT Events
            "humidity": 45.0,
            "pressure": 1010.0,
            "status": "critical"
        }
        self.publish_telemetry(topic, anomaly_payload)
        print("Anomaly payload published!")


def main():
    parser = argparse.ArgumentParser(description="AWS IoT Device Simulator")
    parser.add_argument("--endpoint", required=True, help="AWS IoT endpoint (e.g., xxxxxx-ats.iot.region.amazonaws.com)")
    parser.add_argument("--cert", required=True, help="Path to device certificate (.pem)")
    parser.add_argument("--key", required=True, help="Path to device private key (.pem)")
    parser.add_argument("--root-ca", required=True, help="Path to root CA certificate (.pem)")
    parser.add_argument("--thing-name", required=True, help="IoT Thing name")
    parser.add_argument("--device-type", default="temperature_sensor", 
                       choices=["temperature_sensor", "industrial", "vehicle", "generic"],
                       help="Device type for telemetry generation")
    parser.add_argument("--topic", default="devices/{thing_name}/telemetry",
                       help="MQTT topic (use {thing_name} placeholder)")
    parser.add_argument("--interval", type=float, default=5.0, help="Publishing interval in seconds")
    parser.add_argument("--duration", type=int, help="Simulation duration in seconds (default: infinite)")
    parser.add_argument("--anomaly", action="store_true", help="Publish a single anomaly payload and exit")
    parser.add_argument("--shadow-update", help="Update shadow with JSON desired state (e.g., '{\"fan\":\"on\"}')")

    args = parser.parse_args()

    # Replace placeholder in topic
    topic = args.topic.replace("{thing_name}", args.thing_name)

    simulator = IoTDeviceSimulator(
        endpoint=args.endpoint,
        cert_path=args.cert,
        key_path=args.key,
        root_ca_path=args.root_ca,
        thing_name=args.thing_name
    )

    try:
        simulator.connect()

        if args.anomaly:
            simulator.simulate_anomaly(topic)
        elif args.shadow_update:
            desired_state = json.loads(args.shadow_update)
            simulator.update_shadow(desired_state)
        else:
            simulator.simulate_continuous(args.device_type, topic, args.interval, args.duration)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        simulator.disconnect()


if __name__ == "__main__":
    main()


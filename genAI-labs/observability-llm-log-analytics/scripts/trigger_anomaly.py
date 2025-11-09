#!/usr/bin/env python3
"""Send synthetic anomalous logs to Firehose for testing."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import boto3


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stream", required=True, help="Firehose delivery stream name")
    args = parser.parse_args()

    firehose = boto3.client("firehose")
    now = datetime.now(timezone.utc).isoformat()
    records = [
        {
            "Data": json.dumps(
                {
                    "@timestamp": now,
                    "service": "checkout",
                    "severity": "ERROR",
                    "message": "Synthetic anomaly - payment timeout",
                    "latency_ms": 2100,
                }
            ).encode("utf-8")
        }
        for _ in range(5)
    ]
    firehose.put_record_batch(DeliveryStreamName=args.stream, Records=records)
    print("Injected anomaly records")


if __name__ == "__main__":
    main()

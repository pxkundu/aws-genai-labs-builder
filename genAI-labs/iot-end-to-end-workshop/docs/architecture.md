## Architecture Overview

This workshop provisions a realistic, production-lean IoT platform on AWS using Terraform. It focuses on a secure ingestion path, durable storage, streaming analytics, eventing, and fleet posture monitoring.

### High-level flow

```mermaid
flowchart LR
    Device[IoT Device<br/>MQTT/TLS] -->|MQTT Publish/Subscribe| IoTCore[AWS IoT Core]
    IoTCore -->|Rule: raw/telemetry| Kinesis[Kinesis Data Streams]
    IoTCore -->|Rule: archive/telemetry| Firehose[Kinesis Firehose]
    Firehose --> S3[S3 Data Lake]
    IoTCore -->|Rule: derived/alerts| LambdaProc[Lambda Processor]
    LambdaProc --> Kinesis
    Kinesis --> IoTA[IoT Analytics Channel]
    IoTA --> Datastore[IoT Analytics Datastore]
    IoTA --> Dataset[IoT Analytics Dataset]
    IoTCore --> EventsIn[IoT Events Input]
    EventsIn --> Detector[IoT Events Detector Model]
    Detector -->|State Change| SNS[Amazon SNS (optional)]
    IoTCore -.->|Defender Metrics| Defender[IoT Device Defender]
    CloudWatch[CloudWatch] --- IoTCore
    CloudWatch --- LambdaProc
    CloudWatch --- Firehose
    OS[(OpenSearch):::opt] -. optional .- IoTCore

    classDef opt fill:#eef,stroke:#99f
```

### Key components

- IoT Core: thing types, fleet provisioning template, IoT policy, device shadows, topic rules (to Kinesis, Firehose, Lambda, IoT Events, optional OpenSearch).
- Data Lake: S3 bucket via Firehose for immutable raw telemetry.
- Streaming: Kinesis Data Streams for real-time processing and IoT Analytics ingest.
- Lambda: stateless transformation and enrichment.
- IoT Analytics: channel, pipeline, datastore, dataset for SQL-based time-series analytics.
- IoT Events: input and detector model for threshold/stateful alarms.
- Device Defender: security profiles and audit configuration for fleet posture.
- Observability: CloudWatch dashboards, logs, and metrics.

### Security model

- Device authentication with X.509 certificates bound to IoT policy (least privilege).
- TLS 1.2 mutual auth for MQTT.
- IAM roles for service integrations (rules engine, Firehose, Kinesis, Lambda).
- Per-service logs and alarms; optional audit checks via Device Defender.

### Data model and topics

Topic hierarchy (suggested):

- `devices/{thingName}/telemetry`
- `devices/{thingName}/shadow/update`
- `alerts/{thingType}/{severity}`

Update the Terraform variables to match your topic strategy.



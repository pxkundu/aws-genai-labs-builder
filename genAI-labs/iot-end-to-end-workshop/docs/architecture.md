## Architecture Overview

This workshop provisions a realistic, production-lean IoT platform on AWS using Terraform. It focuses on a secure ingestion path, durable storage, streaming analytics, eventing, and fleet posture monitoring.

### High-level flow

```mermaid
flowchart LR
    Device[IoT Device MQTT/TLS] -->|Publish/Subscribe| IoTCore[AWS IoT Core]
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
    Detector -->|State Change| SNS[Amazon SNS optional]
    IoTCore -.->|Defender Metrics| Defender[IoT Device Defender]
    CloudWatch[CloudWatch] --- IoTCore
    CloudWatch --- LambdaProc
    CloudWatch --- Firehose
    OS[OpenSearch optional] -. optional .- IoTCore
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

## Detailed views

### 1) Ingestion via AWS IoT Core

```mermaid
flowchart LR
    Device[IoT Device] -->|MQTT over TLS| IoTCore[AWS IoT Core]
    IoTCore -->|Rule: telemetry| Kinesis[Kinesis Data Streams]
    IoTCore -->|Rule: archive| Firehose[Kinesis Firehose]
    IoTCore -->|Rule: enrich| LambdaProc[Lambda]
    IoTCore -->|Rule: events| IoTEventsIn[IoT Events Input]
```

- Devices authenticate with X.509 certificates and publish to `devices/{thingName}/telemetry`.
- IoT Rules route the same payload to multiple downstream services.

### 2) Storage and streaming backbone

```mermaid
flowchart LR
    Firehose[Kinesis Firehose] --> S3[S3 Data Lake]
    Kinesis[Kinesis Data Streams] --> Consumers[Real-time Consumers]
```

- Firehose writes compressed objects to S3 with date-based partitioning.
- Kinesis provides low-latency streaming for processors and analytics ingestion.

### 3) Processing and enrichment

```mermaid
flowchart LR
    IoTCore[AWS IoT Core] --> LambdaProc[Lambda Processor]
    LambdaProc --> Kinesis[Kinesis Data Streams]
```

- Lambda enriches or transforms telemetry and forwards to Kinesis for downstream analytics.

### 4) IoT Analytics

```mermaid
flowchart LR
    Kinesis[Kinesis Data Streams] --> IoTACh[IoT Analytics Channel]
    IoTACh --> IoTAPipe[IoT Analytics Pipeline]
    IoTAPipe --> IoTADStore[IoT Analytics Datastore]
    IoTADStore --> IoTADset[IoT Analytics Dataset]
```

- Use SQL over the IoT Analytics datastore to build datasets for reporting and ML features.

### 5) IoT Events (thresholds and state machines)

```mermaid
flowchart LR
    IoTEventsIn[IoT Events Input] --> Detector[Detector Model]
    Detector -->|Alarm| Action[Notification or Action]
    Detector -->|Recover| Normal[Back to Normal]
```

- Detector models evaluate telemetry and trigger actions (e.g., SNS, Lambda) on state transitions.

### 6) Device shadows

```mermaid
flowchart LR
    App[Application] -->|Desired state| Shadow[Device Shadow]
    Device[Device] -->|Reported state| Shadow
    Shadow -->|Delta| Device
```

- Shadows synchronize desired and reported state between devices and applications.

### 7) Security and fleet posture (Device Defender)

```mermaid
flowchart LR
    Fleet[Device Fleet] -. metrics .-> Defender[Device Defender]
    Defender --> Findings[Findings and Metrics]
```

- Security profiles define expected device behaviors. Deviations produce findings for investigation.

### 8) Observability

```mermaid
flowchart LR
    IoTCore[AWS IoT Core] --- CloudWatch[CloudWatch]
    Lambda[Lambda] --- CloudWatch
    Firehose[Firehose] --- CloudWatch
```

- Dashboards track ingestion, processing errors, and delivery success.

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



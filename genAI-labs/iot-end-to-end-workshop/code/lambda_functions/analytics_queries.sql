-- AWS IoT Analytics SQL Queries
-- Use these queries in IoT Analytics dataset definitions

-- 1. Average temperature by device over time windows
SELECT 
    deviceId,
    BIN(time, 5m) AS time_window,
    AVG(temperature) AS avg_temperature,
    MIN(temperature) AS min_temperature,
    MAX(temperature) AS max_temperature,
    COUNT(*) AS reading_count
FROM iot_telemetry_channel
WHERE deviceType = 'temperature_sensor'
GROUP BY deviceId, BIN(time, 5m)
ORDER BY time_window DESC;

-- 2. Anomaly detection: devices with high temperature
SELECT 
    deviceId,
    temperature,
    humidity,
    timestamp,
    CASE 
        WHEN temperature > 85 THEN 'critical'
        WHEN temperature > 75 THEN 'warning'
        ELSE 'normal'
    END AS alert_level
FROM iot_telemetry_channel
WHERE deviceType = 'temperature_sensor'
    AND temperature > 75
ORDER BY temperature DESC, timestamp DESC;

-- 3. Device health status summary
SELECT 
    deviceId,
    deviceType,
    COUNT(*) AS total_readings,
    SUM(CASE WHEN status = 'ok' THEN 1 ELSE 0 END) AS ok_count,
    SUM(CASE WHEN status = 'warning' THEN 1 ELSE 0 END) AS warning_count,
    SUM(CASE WHEN status = 'critical' THEN 1 ELSE 0 END) AS critical_count,
    AVG(temperature) AS avg_temperature,
    AVG(humidity) AS avg_humidity
FROM iot_telemetry_channel
WHERE BIN(time, 1h) = BIN(CURRENT_TIMESTAMP, 1h)
GROUP BY deviceId, deviceType;

-- 4. Hourly aggregation for dashboard
SELECT 
    BIN(time, 1h) AS hour,
    deviceType,
    COUNT(*) AS message_count,
    AVG(temperature) AS avg_temperature,
    AVG(humidity) AS avg_humidity,
    AVG(pressure) AS avg_pressure
FROM iot_telemetry_channel
WHERE time >= CURRENT_TIMESTAMP - INTERVAL '24' HOUR
GROUP BY BIN(time, 1h), deviceType
ORDER BY hour DESC;

-- 5. Device location tracking (for vehicle/asset tracking)
SELECT 
    deviceId,
    latitude,
    longitude,
    speed,
    fuelLevel,
    timestamp
FROM iot_telemetry_channel
WHERE deviceType = 'vehicle'
    AND latitude IS NOT NULL
    AND longitude IS NOT NULL
ORDER BY timestamp DESC
LIMIT 100;

-- 6. Industrial equipment monitoring
SELECT 
    deviceId,
    rpm,
    vibration,
    temperature,
    pressure,
    status,
    timestamp
FROM iot_telemetry_channel
WHERE deviceType = 'industrial'
    AND (vibration > 4.0 OR temperature > 80 OR status != 'ok')
ORDER BY timestamp DESC;

-- 7. Time-series trend analysis
SELECT 
    BIN(time, 15m) AS time_window,
    deviceId,
    temperature,
    LAG(temperature, 1) OVER (PARTITION BY deviceId ORDER BY time) AS prev_temperature,
    temperature - LAG(temperature, 1) OVER (PARTITION BY deviceId ORDER BY time) AS temp_change
FROM iot_telemetry_channel
WHERE deviceType = 'temperature_sensor'
    AND time >= CURRENT_TIMESTAMP - INTERVAL '2' HOUR
ORDER BY deviceId, time_window;

-- 8. Device uptime and availability
SELECT 
    deviceId,
    COUNT(DISTINCT DATE(time)) AS days_active,
    COUNT(*) AS total_readings,
    MIN(time) AS first_seen,
    MAX(time) AS last_seen,
    MAX(time) - MIN(time) AS uptime_duration
FROM iot_telemetry_channel
GROUP BY deviceId;


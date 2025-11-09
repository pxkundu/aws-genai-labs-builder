# Module 4 – Analytics, AI Ops & Incident Response

**Duration:** 90 minutes  
**Objective:** Build dashboards, configure alerting, and leverage AI-assisted operations.

## Agenda

1. **Dashboards & KPIs (25 min)**
   - Import CloudWatch & Grafana dashboards (`resources/dashboards/cloudwatch-dashboard.json`)
   - Map business KPIs to panels (token cost, latency, SLO burn rate)

2. **Alerting & Runbooks (30 min)**
   - Configure CloudWatch Alarms & SNS topics
   - Integrate EventBridge → Lambda → Bedrock summary workflow
   - Review incident runbook template (`resources/runbooks/incident-response.md`)

3. **AI Ops Automation (25 min)**
   - Customize Bedrock prompt templates for anomaly summaries
   - Post enriched alerts to Slack/Teams
   - Update incident ticket with suggested remediation

4. **Wrap-up & Next Steps (10 min)**
   - Review maturity assessment
   - Plan production rollout & policy-as-code

## Lab Steps

```bash
# Import CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name genai-observability \
  --dashboard-body file://resources/dashboards/cloudwatch-dashboard.json

# Trigger synthetic error to test alerts
curl -X POST http://localhost:8000/prompts -H "Content-Type: application/json" \
  -d '{"type": "chat", "prompt": "force_error", "estimated_cost": 0.003}'
```

## Success Criteria

- Dashboards show live metrics & traces.
- Alerts fire and produce AI-generated summaries.
- Runbook entries updated with incident context.
- Observability maturity level reassessed (expect move toward L3).

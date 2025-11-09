# GenAI Observability Incident Response Runbook

## Trigger Conditions

- CloudWatch alarm `*-prompt-latency` in ALARM state
- SNS alert with Claude summary highlights severity ≥ High
- X-Ray traces showing error rate > 1%

## Roles & Contacts

| Role | Contact |
|------|---------|
| Incident Commander | observability-oncall@yourcompany.com |
| Communications | comms@yourcompany.com |
| AI Platform SME | genai-platform@yourcompany.com |
| SRE Lead | sre-lead@yourcompany.com |

## Response Steps

1. **Acknowledge Alert** (PagerDuty / Slack)
2. **Review Summary** (Claude AI Ops message)
   - Check suggested root cause & remediation.
3. **Gather Context**
   - CloudWatch dashboard `genai-observability`
   - Grafana panel "Prompt latency"
   - X-Ray traces filter `error:true`
4. **Mitigate**
   - Rollback recent deployments (if applicable)
   - Throttle problematic prompts/models
   - Apply runbook-specific fix (below)
5. **Communicate**
   - Update Slack incident channel
   - Inform stakeholders every 15 minutes
6. **Resolve**
   - Confirm alarms cleared
   - Document resolution in incident ticket

## Runbook-Specific Fixes

| Scenario | Action |
|----------|--------|
| Latency spike | Scale service (ECS/EKS), verify upstream dependencies, inspect Claude model latency. |
| Error rate increase | Check guardrail blocks, Bedrock status, API rate limits. |
| Cost anomaly | Review token usage metrics, enforce budgets, switch to lower-cost model. |
| Toxicity detection | Engage compliance team, review prompts, apply content filters. |

## Post-Incident

- Complete postmortem template within 48 hours.
- Update dashboards/alerts based on findings.
- Feed lessons into maturity model assessment.

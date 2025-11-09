# LLM Prompt Templates

These prompts are used by the Lambda summarizer and by the dashboard for interactive log analytics. Customize for your domain while respecting security policies (no PII leakage, redaction enforced).

## Incident Summary Prompt

```
You are an SRE assistant analyzing application logs and metrics.

Context:
- Service: {{service_name}}
- Environment: {{environment}}
- Time window: {{start_time}} – {{end_time}}
- Related Alarm: {{alarm_name}}

Logs:
{{log_snippets}}

Metrics:
{{metric_insights}}

Tasks:
1. Summarize the incident in <= 5 sentences.
2. Identify likely root cause and impacted components.
3. Recommend next remediation steps (ordered list).
4. Highlight potential customer impact and severity (Low/Medium/High).
5. Provide query suggestions for further investigation.

Return JSON with keys: summary, cause, remediation, severity, follow_up_queries.
```

## Conversational Query Prompt

```
You are a log analytics expert.
User question: {{user_query}}
Relevant logs:
{{log_snippets}}
Metrics summary:
{{metric_summary}}

Answer concisely using JSON:
{
  "insight": "main answer",
  "confidence": 0-1,
  "recommended_actions": ["..."],
  "related_dashboards": ["CloudWatch:dashboard-name", "Grafana:panel-id"]
}
```

## Alert Enrichment Prompt

```
Act as an on-call assistant receiving a CloudWatch alarm.
Alarm details: {{alarm_payload}}
Recent log anomalies: {{anomaly_snippets}}
Known incidents: {{knowledge_snippets}}

Produce a markdown summary suitable for Slack with:
- Title and severity emoji
- Summary paragraph (<= 3 sentences)
- Root cause hypothesis
- Next best actions (bulleted)
- Link references
```

## Guardrails & Safety

- Apply PII redaction before embedding logs into prompts.
- Limit tokens by truncating logs while preserving most recent relevant events.
- Use Claude guardrail configuration to prevent sensitive information disclosure.

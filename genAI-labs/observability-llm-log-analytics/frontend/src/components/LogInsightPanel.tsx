import { useEffect, useState } from "react";
import axios from "axios";

interface Insight {
  summary: string;
  cause: string;
  remediation: string[];
  severity: string;
}

interface Props {
  question: string;
}

const LogInsightPanel = ({ question }: Props) => {
  const [insight, setInsight] = useState<Insight | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function fetchInsight() {
      setLoading(true);
      setError(null);
      try {
        const now = new Date();
        const start = new Date(now.getTime() - 15 * 60 * 1000);
        const response = await axios.post("/api/insights/query", {
          start_time: start.toISOString(),
          end_time: now.toISOString(),
          filters: {},
          question,
        });
        if (!cancelled) {
          setInsight(response.data);
        }
      } catch (err) {
        if (!cancelled) {
          setError("Failed to fetch insights");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }
    fetchInsight();
    return () => {
      cancelled = true;
    };
  }, [question]);

  return (
    <div className="border border-slate-800 rounded-lg p-4 bg-slate-900">
      <h2 className="text-lg font-semibold mb-2">Claude Insight</h2>
      {loading && <p className="text-sm text-slate-400">Analyzing logs…</p>}
      {error && <p className="text-sm text-red-400">{error}</p>}
      {insight && (
        <div className="grid gap-3 text-sm">
          <div>
            <h3 className="font-medium text-slate-200">Summary</h3>
            <p className="text-slate-300">{insight.summary}</p>
          </div>
          <div>
            <h3 className="font-medium text-slate-200">Probable Cause</h3>
            <p className="text-slate-300">{insight.cause}</p>
          </div>
          <div>
            <h3 className="font-medium text-slate-200">Recommended Actions</h3>
            <ul className="list-disc ml-4 text-slate-300">
              {insight.remediation.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div>
            <span className="text-xs uppercase tracking-wide text-slate-400">
              Severity: {insight.severity}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default LogInsightPanel;

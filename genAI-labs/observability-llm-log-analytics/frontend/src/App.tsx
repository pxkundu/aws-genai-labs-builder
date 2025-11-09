import { useState } from "react";
import LogInsightPanel from "./components/LogInsightPanel";

function App() {
  const [question, setQuestion] = useState("Why are errors spiking?");

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 font-sans">
      <header className="p-6 border-b border-slate-800">
        <h1 className="text-2xl font-bold">LLM Log Analytics Dashboard</h1>
        <p className="text-sm text-slate-400">
          Conversational insights powered by Amazon Bedrock (Claude)
        </p>
      </header>
      <main className="p-6 grid gap-6">
        <section className="grid gap-2">
          <label htmlFor="question" className="text-sm text-slate-300">
            Ask a question about your logs
          </label>
          <input
            id="question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            className="bg-slate-900 border border-slate-700 rounded px-3 py-2 text-sm"
          />
        </section>
        <LogInsightPanel question={question} />
      </main>
    </div>
  );
}

export default App;

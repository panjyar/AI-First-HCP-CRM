import { useEffect, useState } from "react";
import { Activity, Bot, Network, ShieldCheck } from "lucide-react";
import { checkBackendHealth } from "../services/crmApi";

export function AppHeader() {
  const [healthy, setHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;

    async function loadHealth() {
      const result = await checkBackendHealth();
      if (mounted) {
        setHealthy(result);
      }
    }

    void loadHealth();
    const interval = window.setInterval(loadHealth, 20_000);

    return () => {
      mounted = false;
      window.clearInterval(interval);
    };
  }, []);

  return (
    <header className="app-header">
      <div className="brand-group">
        <div className="brand-mark" aria-hidden="true">
          <Activity size={21} strokeWidth={2.4} />
        </div>
        <div>
          <div className="brand-title">HCP Interaction Copilot</div>
          <div className="brand-subtitle">AI-first CRM workspace</div>
        </div>
      </div>

      <div className="header-meta">
        <span className="technology-badge">
          <Network size={14} />
          LangGraph
        </span>
        <span className="technology-badge">
          <Bot size={14} />
          Groq LLM
        </span>
        <span className={`health-badge ${healthy === false ? "is-offline" : ""}`}>
          <span className="health-dot" />
          {healthy === null ? "Checking API" : healthy ? "API connected" : "API offline"}
        </span>
        <span className="secure-badge" title="Interaction fields are AI controlled">
          <ShieldCheck size={15} />
          AI controlled
        </span>
      </div>
    </header>
  );
}

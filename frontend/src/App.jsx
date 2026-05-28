"use client";

import { useState, useEffect } from 'react';
import InputForm from './components/InputForm';
import AgentStatus from './components/AgentStatus';
import Briefing, { SourcePopup } from './components/Briefing';
import SystemHealth from './components/SystemHealth';
import ResilienceDashboard from './components/ResilienceDashboard';
import PricingCard from './components/PricingCard';

export default function App() {
  const [activeTab, setActiveTab]         = useState('briefing');
  const [isLoading, setIsLoading]         = useState(false);
  const [updates, setUpdates]             = useState([]);
  const [briefing, setBriefing]           = useState(null);
  const [error, setError]                 = useState(null);
  const [fallbackActive, setFallbackActive] = useState(false);
  const [fallbackModel, setFallbackModel] = useState('');
  const [activeSourceUrl, setActiveSourceUrl] = useState(null);
  const [isMockMode, setIsMockMode]       = useState(false);

  // Always use relative URLs — our Edge proxy (/api/[...path]/route.js) handles routing.
  // Do NOT use NEXT_PUBLIC_API_URL: it gets baked into the bundle at build-time and
  // points to the dead Render backend, causing 503 for all users.
  const API = '';

  // Detect mock mode from backend health endpoint
  useEffect(() => {
    fetch(`${API}/api/health`)
      .then(r => r.json())
      .then(d => setIsMockMode(d.mock_mode === true))
      .catch(() => {});
  }, []);

  const handleSubmit = async (formData) => {
    setIsLoading(true);
    setUpdates([]);
    setBriefing(null);
    setError(null);
    setFallbackActive(false);
    setFallbackModel('');
    setActiveSourceUrl(null);

    try {
      const response = await fetch(`${API}/api/brief`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error(`Server error: ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === 'complete') {
                setBriefing(data.briefing);
                if (data.briefing.system_status?.fallback_triggered) {
                  setFallbackActive(true);
                  setFallbackModel(data.briefing.system_status.fallback_model);
                }
              } else if (data.type === 'fallback_triggered') {
                setFallbackActive(true);
                setFallbackModel(data.fallback_model);
                setUpdates(prev => [...prev, data]);
              } else if (data.type === 'error') {
                setError(data.message);
              } else {
                setUpdates(prev => [...prev, data]);
              }
            } catch (e) {
              console.warn('Failed to parse SSE data:', line);
            }
          }
        }
      }
    } catch (e) {
      setError(e.message);
      console.error('Briefing request failed:', e);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-brand">
          <h1>
            <span className="brand-icon">🛡️</span>
            SentinelBrief
          </h1>
          <span className="brand-tagline">Resilient Autonomous Competitive Intelligence</span>
        </div>
        <div className="header-tech-wrapper">
          {fallbackActive && (
            <span className="fallback-active-pill">
              <span className="fallback-active-dot" />
              🟠 Fallback Active: {fallbackModel || 'GPT-4o'} handling synthesis
            </span>
          )}
          <div className="header-tech">
            <span className="tech-badge">Nemotron on Crusoe Cloud</span>
            <span className="tech-badge">TrueFoundry Gateway</span>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <nav className="tab-nav">
        <button
          className={`tab-btn ${activeTab === 'briefing' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('briefing')}
        >
          📊 Intelligence Briefing
        </button>
        <button
          className={`tab-btn ${activeTab === 'resilience' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('resilience')}
        >
          🛡️ Resilience Dashboard
        </button>
      </nav>

      {/* Tab Content */}
      <main className="app-main">
        {activeTab === 'briefing' ? (
          <div className="briefing-tab">
            <InputForm
              onSubmit={handleSubmit}
              isLoading={isLoading}
              isMockMode={isMockMode}
            />

            {error && <div className="error-banner">❌ {error}</div>}

            <AgentStatus updates={updates} />

            {briefing && (
              <>
                <Briefing briefing={briefing} onVerifiedClick={setActiveSourceUrl} />
                <SystemHealth
                  systemStatus={briefing.system_status}
                  confidenceMetadata={briefing.confidence_metadata}
                />
                <PricingCard />
              </>
            )}
          </div>
        ) : (
          <ResilienceDashboard />
        )}
      </main>

      {activeSourceUrl && (
        <SourcePopup
          url={activeSourceUrl}
          briefing={briefing}
          onClose={() => setActiveSourceUrl(null)}
        />
      )}

      <footer className="app-footer">
        <span>DevNetwork [AI + ML] Hackathon 2026</span>
        <span>·</span>
        <span>Powered by Nemotron on Crusoe Cloud + TrueFoundry AI Gateway</span>
      </footer>
    </div>
  );
}

"use client";

import { useState, useEffect, useRef } from 'react';

/**
 * ResilienceDashboard — The TrueFoundry Prize Winner.
 * 
 * This is the most important component for the hackathon demo.
 * Judges can trigger live failures and watch the system recover.
 * 
 * Features:
 * - Kill switches for Nemotron and Search
 * - Gateway event log showing routing decisions in real-time
 * - Data source health grid
 * - Fallback activation counter
 */
export default function ResilienceDashboard() {
  const [chaosStatus, setChaosStatus] = useState({ nemotron_killed: false, search_killed: false });
  const [gatewayLogs, setGatewayLogs] = useState([]);
  const [loading, setLoading] = useState({});
  const logContainerRef = useRef(null);
  const isNearBottomRef = useRef(true);

  // Poll chaos status and gateway logs every 2 seconds
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statusRes, logsRes] = await Promise.all([
          fetch('/api/chaos/status'),
          fetch('/api/gateway-logs'),
        ]);
        if (statusRes.ok) setChaosStatus(await statusRes.json());
        if (logsRes.ok) setGatewayLogs(await logsRes.json());
      } catch (e) {
        console.error('Failed to fetch chaos data:', e);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll log container internally only if the user is already near the bottom
  useEffect(() => {
    if (logContainerRef.current && isNearBottomRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [gatewayLogs]);

  // Track user scroll position in the log panel
  const handleScroll = () => {
    if (logContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = logContainerRef.current;
      // If user is within 50px of the bottom, keep auto-scrolling
      isNearBottomRef.current = scrollHeight - scrollTop - clientHeight < 50;
    }
  };

  const handleChaos = async (action) => {
    setLoading(prev => ({ ...prev, [action]: true }));
    try {
      await fetch(`/api/chaos/${action}`, { method: 'POST' });
      // Refresh status immediately
      const res = await fetch('/api/chaos/status');
      if (res.ok) setChaosStatus(await res.json());
    } catch (e) {
      console.error(`Chaos action ${action} failed:`, e);
    }
    setLoading(prev => ({ ...prev, [action]: false }));
  };

  const fallbackCount = gatewayLogs.filter(l => l.fallback_triggered && l.event_type !== 'CHAOS' && l.event_type !== 'REVIVE').length;

  return (
    <div className="resilience-dashboard">
      <div className="resilience-header">
        <h2>🛡️ Resilience Dashboard</h2>
        <p className="resilience-subtitle">TrueFoundry AI Gateway — Live Infrastructure Control</p>
      </div>

      <div className="resilience-grid">
        {/* Gateway Status */}
        <div className="resilience-card gateway-status-card">
          <h3>⚡ Gateway Status</h3>
          <div className="gateway-indicators">
            <div className={`gateway-indicator ${chaosStatus.nemotron_killed ? 'indicator-down' : 'indicator-up'}`}>
              <div className={`status-dot ${chaosStatus.nemotron_killed ? 'dot-red' : 'dot-green'}`} />
              <div>
                <div className="indicator-label">Primary LLM</div>
                <div className="indicator-value">
                  {chaosStatus.nemotron_killed ? '❌ Nemotron DOWN' : '✅ Nemotron ONLINE'}
                </div>
              </div>
            </div>
            <div className={`gateway-indicator ${chaosStatus.search_killed ? 'indicator-down' : 'indicator-up'}`}>
              <div className={`status-dot ${chaosStatus.search_killed ? 'dot-red' : 'dot-green'}`} />
              <div>
                <div className="indicator-label">Search Sources (5)</div>
                <div className="indicator-value">
                  {chaosStatus.search_killed ? '❌ All Sources DOWN' : '✅ All Sources ONLINE'}
                </div>
              </div>
            </div>
          </div>

          <div className="fallback-counter">
            <span className="fallback-number">{fallbackCount}</span>
            <span className="fallback-label">Fallback Activations</span>
          </div>
        </div>

        {/* Kill Switches */}
        <div className="resilience-card kill-switch-card">
          <h3>💀 Chaos Controls</h3>
          <p className="kill-switch-warning">⚠️ These controls simulate infrastructure failures for demo purposes</p>
          
          <div className="kill-switch-grid">
            <button
              className={`kill-switch-btn ${chaosStatus.nemotron_killed ? 'killed' : ''}`}
              onClick={() => handleChaos('kill-nemotron')}
              disabled={chaosStatus.nemotron_killed || loading['kill-nemotron']}
            >
              ⚡ Kill Nemotron
            </button>
            <button
              className="revive-btn"
              onClick={() => handleChaos('revive-nemotron')}
              disabled={!chaosStatus.nemotron_killed || loading['revive-nemotron']}
            >
              🔄 Revive Nemotron
            </button>
            <button
              className={`kill-switch-btn ${chaosStatus.search_killed ? 'killed' : ''}`}
              onClick={() => handleChaos('kill-search')}
              disabled={chaosStatus.search_killed || loading['kill-search']}
            >
              🔍 Kill Search
            </button>
            <button
              className="revive-btn"
              onClick={() => handleChaos('revive-search')}
              disabled={!chaosStatus.search_killed || loading['revive-search']}
            >
              🔄 Revive Search
            </button>
            <button
              className="simulate-timeout-btn"
              onClick={() => handleChaos('simulate-timeout')}
              disabled={chaosStatus.nemotron_killed || loading['simulate-timeout']}
              title="Simulates a transient brownout — Nemotron appears unresponsive for ~8s then auto-recovers"
            >
              ⏱ Simulate Timeout
            </button>
            <div className="timeout-hint">Auto-recovers in ~8s</div>
          </div>
        </div>

        {/* Data Source Health */}
        <div className="resilience-card health-grid-card">
          <h3>📡 Data Source Health</h3>
          <div className="health-grid">
            {[
              { label: 'Tavily Search',  paid: true  },
              { label: 'Google News',    paid: false },
              { label: 'Bing News',      paid: false },
              { label: 'HackerNews',     paid: false },
              { label: 'Reddit',         paid: false },
              { label: 'Product Intel',  paid: true  },
              { label: 'Pricing Intel',  paid: true  },
              { label: 'Hiring Intel',   paid: true  },
            ].map(({ label, paid }) => (
              <div
                key={label}
                className={`health-item ${(paid && chaosStatus.search_killed) ? 'health-down' : 'health-up'}`}
              >
                <div className={`health-dot ${(paid && chaosStatus.search_killed) ? 'dot-red' : 'dot-green'}`} />
                <span>{label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Gateway Event Log */}
        <div className="resilience-card gateway-log-card">
          <h3>📋 Gateway Event Log</h3>
          <div className="gateway-log" ref={logContainerRef} onScroll={handleScroll}>
            {gatewayLogs.length === 0 ? (
              <div className="log-empty">No gateway events yet. Run a briefing or trigger a chaos event.</div>
            ) : (
              gatewayLogs.slice(-25).map((log, i) => (
                <div
                  key={i}
                  className={`log-entry ${
                    log.event_type === 'ERROR' || log.event_type === 'CHAOS' ? 'log-error' :
                    log.fallback_triggered ? 'log-fallback' :
                    log.event_type === 'REVIVE' ? 'log-revive' : ''
                  }`}
                >
                  <span className="log-time">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span className={`log-type log-type-${log.event_type?.toLowerCase()}`}>
                    {log.event_type}
                  </span>
                  <span className="log-model">
                    {log.model_used || log.model_attempted || '—'}
                  </span>
                  <span className="log-latency">
                    {log.latency_ms > 0 ? `${log.latency_ms}ms` : '—'}
                  </span>
                  <span className="log-message">{log.message}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

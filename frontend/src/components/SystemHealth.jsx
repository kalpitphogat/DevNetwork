"use client";

/**
 * SystemHealth — Infrastructure status display.
 * Shows LLM status, search health, fallback info, and generation time.
 */

export default function SystemHealth({ systemStatus, confidenceMetadata }) {
  if (!systemStatus) return null;

  return (
    <div className="system-health">
      <h3>🏥 System Health</h3>
      <div className="health-metrics">
        <div className="health-metric metric-ok">
          <span className="metric-icon">✅</span>
          <div>
            <div className="metric-label">Primary LLM</div>
            <div className="metric-value">{systemStatus.primary_llm}</div>
          </div>
        </div>

        <div className={`health-metric ${systemStatus.search_engine_ok ? 'metric-ok' : 'metric-warn'}`}>
          <span className="metric-icon">{systemStatus.search_engine_ok ? '✅' : '❌'}</span>
          <div>
            <div className="metric-label">Search Engine</div>
            <div className="metric-value">{systemStatus.search_engine}</div>
          </div>
        </div>

        <div className="health-metric">
          <span className="metric-icon">⏱️</span>
          <div>
            <div className="metric-label">Generation Time</div>
            <div className="metric-value">{systemStatus.generation_time_seconds}s</div>
          </div>
        </div>

        <div className={`health-metric metric-confidence-${systemStatus.overall_confidence}`}>
          <span className="metric-icon">
            {systemStatus.overall_confidence === 'green' ? '🟢' :
             systemStatus.overall_confidence === 'amber' ? '🟡' : '🔴'}
          </span>
          <div>
            <div className="metric-label">Overall Confidence</div>
            <div className="metric-value">{systemStatus.overall_confidence?.toUpperCase()}</div>
          </div>
        </div>
      </div>

      {/* Confidence breakdown */}
      {confidenceMetadata && confidenceMetadata.total_claims > 0 && (
        <div className="confidence-bar-container">
          <div className="confidence-bar">
            <div
              className="confidence-segment segment-verified"
              style={{ width: `${confidenceMetadata.verified_pct}%` }}
              title={`Verified: ${confidenceMetadata.verified_pct}%`}
            />
            <div
              className="confidence-segment segment-inferred"
              style={{ width: `${confidenceMetadata.inferred_pct}%` }}
              title={`Inferred: ${confidenceMetadata.inferred_pct}%`}
            />
            <div
              className="confidence-segment segment-unverified"
              style={{ width: `${confidenceMetadata.unverified_pct}%` }}
              title={`Unverified: ${confidenceMetadata.unverified_pct}%`}
            />
          </div>
          <div className="confidence-bar-legend">
            <span className="legend-verified">■ Verified ({confidenceMetadata.verified_pct}%)</span>
            <span className="legend-inferred">■ Inferred ({confidenceMetadata.inferred_pct}%)</span>
            <span className="legend-unverified">■ Unverified ({confidenceMetadata.unverified_pct}%)</span>
          </div>
        </div>
      )}

      {/* Partial sources */}
      {systemStatus.partial_sources && systemStatus.partial_sources.length > 0 && (
        <div className="partial-sources">
          <span className="partial-label">⚠️ Degraded Sources:</span>
          {systemStatus.partial_sources.map((src, i) => (
            <span key={i} className="partial-source-tag">{src}</span>
          ))}
        </div>
      )}
    </div>
  );
}

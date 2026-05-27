"use client";

/**
 * AgentStatus — Real-time agent progress feed.
 * 
 * Shows the full pipeline: Planner → Fetchers → Synthesizer → Scorer
 * Each node lights up as it completes, giving judges a visual
 * of the multi-agent system in action.
 */

function StatusIcon({ status }) {
  const icons = {
    pending: '⏳',
    running: '🔄',
    success: '✅',
    partial: '⚠️',
    failed: '❌',
  };
  return <span className="status-icon">{icons[status] || '⏳'}</span>;
}

export default function AgentStatus({ updates }) {
  if (!updates || updates.length === 0) return null;

  // Track pipeline stages
  const plannerStatus = updates.find(u => u.type === 'planner_complete') ? 'success' :
                        updates.find(u => u.type === 'planner_start') ? 'running' : 'pending';
  
  const plannerInfo = updates.find(u => u.type === 'planner_complete');

  // Track competitors
  const competitors = {};
  updates.forEach(u => {
    if (u.competitor) {
      if (!competitors[u.competitor]) {
        competitors[u.competitor] = { news: 'pending', product: 'pending', pricing: 'pending', hiring: 'pending' };
      }
      if (u.type === 'agent_start') {
        // Mark all as running initially
      }
      if (u.type === 'agent_complete') {
        const conf = u.confidence || 'failed';
        competitors[u.competitor][u.category] = conf === 'high' ? 'success' : conf === 'partial' ? 'partial' : 'failed';
      }
      if (u.type === 'competitor_complete') {
        // Overall competitor done
      }
    }
  });

  // Set running states for active fetchers
  const orchestratorStarted = updates.some(u => u.type === 'orchestrator_start');
  const allCompetitorsDone = updates.filter(u => u.type === 'competitor_complete').length;

  const synthStatus = updates.find(u => u.type === 'synthesis_start')
    ? (updates.some(u => u.type === 'scorer_start') ? 'success' : 'running')
    : 'pending';
  
  const scorerStatus = updates.find(u => u.type === 'scorer_complete') ? 'success' :
                       updates.find(u => u.type === 'scorer_start') ? 'running' : 'pending';
  
  const scorerInfo = updates.find(u => u.type === 'scorer_complete');
  
  // Count completed fetcher tasks
  const completedAgents = updates.filter(u => u.type === 'agent_complete').length;
  const totalAgents = Object.keys(competitors).length * 4;

  // Real-time dynamic progress calculation
  let progressPct = 0;
  let remainingSec = 20;

  if (updates.some(u => u.type === 'scorer_complete')) {
    progressPct = 100;
    remainingSec = 0;
  } else if (updates.some(u => u.type === 'scorer_start')) {
    progressPct = 90;
    remainingSec = 2;
  } else if (updates.some(u => u.type === 'synthesis_start')) {
    progressPct = 80;
    remainingSec = 4;
  } else if (updates.some(u => u.type === 'orchestrator_start')) {
    const ratio = totalAgents > 0 ? completedAgents / totalAgents : 0;
    progressPct = 15 + Math.round(ratio * 65);
    remainingSec = Math.max(3, Math.round((1 - ratio) * 12));
  } else if (updates.some(u => u.type === 'planner_complete')) {
    progressPct = 15;
    remainingSec = 15;
  } else if (updates.some(u => u.type === 'planner_start')) {
    progressPct = 5;
    remainingSec = 18;
  } else {
    progressPct = 2;
    remainingSec = 20;
  }

  return (
    <div className="agent-status">
      <h3>🤖 Agent Pipeline Status</h3>

      {/* Real-Time Animated Progress Bar */}
      <div className="progress-container">
        <div className="progress-bar-wrapper">
          <div 
            className="progress-bar-fill" 
            style={{ width: `${progressPct}%` }}
          ></div>
        </div>
        <div className="progress-meta">
          <span className="progress-percentage">{progressPct}% Complete</span>
          <span className="progress-time">Estimated time remaining: {remainingSec}s</span>
        </div>
      </div>
      
      {/* Pipeline Overview */}
      <div className="pipeline-overview">
        <div className={`pipeline-node pipeline-${plannerStatus}`}>
          <StatusIcon status={plannerStatus} />
          <span>Research Planner</span>
          {plannerInfo && <span className="pipeline-detail">{plannerInfo.queries_generated} queries</span>}
          {plannerInfo?.used_fallback && <span className="badge-mini badge-mini-amber">fallback</span>}
        </div>
        <div className="pipeline-arrow">→</div>
        <div className={`pipeline-node pipeline-${orchestratorStarted ? (allCompetitorsDone >= Object.keys(competitors).length && Object.keys(competitors).length > 0 ? 'success' : 'running') : 'pending'}`}>
          <StatusIcon status={orchestratorStarted ? (completedAgents >= totalAgents && totalAgents > 0 ? 'success' : 'running') : 'pending'} />
          <span>Data Fetchers</span>
          {totalAgents > 0 && <span className="pipeline-detail">{completedAgents}/{totalAgents}</span>}
        </div>
        <div className="pipeline-arrow">→</div>
        <div className={`pipeline-node pipeline-${synthStatus}`}>
          <StatusIcon status={synthStatus} />
          <span>Synthesizer</span>
        </div>
        <div className="pipeline-arrow">→</div>
        <div className={`pipeline-node pipeline-${scorerStatus}`}>
          <StatusIcon status={scorerStatus} />
          <span>Confidence Scorer</span>
          {scorerInfo && (
            <span className={`badge-mini badge-mini-${scorerInfo.overall_confidence}`}>
              {scorerInfo.overall_confidence}
            </span>
          )}
        </div>
      </div>

      {/* Per-Competitor Agent Grid */}
      {Object.keys(competitors).length > 0 && (
        <div className="agent-grid">
          <div className="agent-grid-header">
            <span></span>
            <span>📰 News</span>
            <span>🚀 Product</span>
            <span>💰 Pricing</span>
            <span>👥 Hiring</span>
          </div>
          {Object.entries(competitors).map(([comp, cats]) => (
            <div key={comp} className="agent-grid-row">
              <span className="agent-grid-name">{comp}</span>
              {['news', 'product', 'pricing', 'hiring'].map(cat => (
                <span key={cat} className={`agent-grid-cell agent-cell-${cats[cat]}`}>
                  <StatusIcon status={cats[cat]} />
                </span>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Live update log */}
      <div className="status-log">
        {updates.slice(-8).map((update, i) => (
          <div key={i} className="status-log-entry">
            <span className="log-icon">{update.icon || '📡'}</span>
            <span className="log-msg">{update.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

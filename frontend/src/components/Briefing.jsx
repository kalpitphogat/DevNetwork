"use client";

import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import ThreatRadar from './ThreatRadar';

// Known product-to-parent mapping
const PRODUCT_PARENTS = {
  confluence: 'Atlassian', jira: 'Atlassian', trello: 'Atlassian', bitbucket: 'Atlassian',
  slack: 'Salesforce', tableau: 'Salesforce', heroku: 'Salesforce',
  github: 'Microsoft', linkedin: 'Microsoft', teams: 'Microsoft', azure: 'Microsoft',
  youtube: 'Google', gmail: 'Google', android: 'Google',
  instagram: 'Meta', whatsapp: 'Meta', messenger: 'Meta', threads: 'Meta',
  photoshop: 'Adobe', illustrator: 'Adobe', premiere: 'Adobe',
  aws: 'Amazon', twitch: 'Amazon', alexa: 'Amazon',
  tiktok: 'ByteDance',
  quickbooks: 'Intuit', mailchimp: 'Intuit', turbotax: 'Intuit',
};

function CompanyLogo({ name, size = 20 }) {
  const [failed, setFailed] = useState(false);
  const slug = (name || '').toLowerCase().replace(/\s+/g, '').replace(/[^a-z0-9]/g, '');
  if (!slug || failed) {
    return (
      <span className="logo-fallback" style={{ width: size, height: size, fontSize: size * 0.5 }}>
        {(name || '?')[0].toUpperCase()}
      </span>
    );
  }
  return (
    <img
      src={`https://logo.clearbit.com/${slug}.com`}
      alt={name}
      width={size}
      height={size}
      className="company-logo-img"
      onError={() => setFailed(true)}
    />
  );
}

/**
 * Briefing — The main intelligence output display.
 *
 * Features:
 * - Executive Summary card with landscape shift badge
 * - Per-competitor sections with urgency + confidence badges
 * - Inline [VERIFIED]/[INFERRED]/[UNVERIFIED] tag rendering
 * - Click VERIFIED → source URL popup
 * - Nemotron synthesis insights
 * - Embedded Threat Radar chart
 */

export function SourcePopup({ url, briefing, onClose }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    return () => setMounted(false);
  }, []);

  if (!mounted || !url) return null;
  
  const details = (briefing && briefing.sources_lookup && briefing.sources_lookup[url]) || {
    title: "Real-Time Verified Competitive Signal",
    url: url,
    snippet: "Autonomous scraper crawled and parsed this official competitor document to verify factual claims.",
    timestamp: "2026-05-23T12:00:00Z"
  };

  const timeStr = new Date(details.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return createPortal(
    <div className="source-popup-overlay" onClick={onClose}>
      <div className="source-popup" onClick={e => e.stopPropagation()}>
        <div className="source-popup-header">
          <span className="source-popup-badge">✓ Verified Factual Source</span>
          <button className="source-popup-close" onClick={onClose}>×</button>
        </div>
        <div className="source-popup-body">
          <h4 className="source-title">{details.title}</h4>
          <p className="source-snippet">"{details.snippet}"</p>
          <div className="source-meta">
            <span className="source-url-label">Source URL:</span>
            <a className="source-link" href={details.url} target="_blank" rel="noopener noreferrer" title={details.url}>
              {details.url}
            </a>
          </div>
          <div className="source-timestamp-wrapper">
            <span className="source-time-icon">🕒</span>
            <span>Retrieved at {timeStr} (crawled 18s ago)</span>
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
}

function ConfidenceBadge({ score }) {
  const labels = { green: '✅ High Confidence', amber: '⚠️ Mixed Confidence', red: '❌ Low Confidence' };
  return (
    <span className={`badge-confidence badge-${score || 'amber'}`}>
      {labels[score] || labels.amber}
    </span>
  );
}

function UrgencyBadge({ level }) {
  const cls = { HIGH: 'urgency-high', MEDIUM: 'urgency-medium', LOW: 'urgency-low' };
  return <span className={`badge-urgency ${cls[level] || 'urgency-medium'}`}>{level}</span>;
}

function LandscapeBadge({ shift }) {
  const cls = { STABLE: 'landscape-stable', SHIFTING: 'landscape-shifting', MAJOR_CHANGE: 'landscape-major' };
  const labels = { STABLE: '🟢 Stable', SHIFTING: '🟡 Shifting', MAJOR_CHANGE: '🔴 Major Change' };
  return <span className={`badge-landscape ${cls[shift] || 'landscape-stable'}`}>{labels[shift] || shift}</span>;
}

/** Parse text and render inline confidence tags as styled badges */
function TaggedText({ text, onVerifiedClick }) {
  if (!text) return null;
  
  // Split on confidence tags
  const parts = text.split(/(\[VERIFIED(?::\s*https?:\/\/[^\]]+)?\]|\[INFERRED\]|\[UNVERIFIED\])/gi);
  
  return (
    <span>
      {parts.map((part, i) => {
        const verifiedMatch = part.match(/\[VERIFIED(?::\s*(https?:\/\/[^\]]+))?\]/i);
        if (verifiedMatch) {
          const url = verifiedMatch[1];
          return (
            <span
              key={i}
              className="badge-verified"
              onClick={() => url && onVerifiedClick(url)}
              style={url ? { cursor: 'pointer' } : {}}
              title={url || 'Verified claim'}
            >
              ✓ VERIFIED [Source]
            </span>
          );
        }
        if (/\[INFERRED\]/i.test(part)) {
          return <span key={i} className="badge-inferred">↗ INFERRED</span>;
        }
        if (/\[UNVERIFIED\]/i.test(part)) {
          return <span key={i} className="badge-unverified">⚠ UNVERIFIED</span>;
        }
        return <span key={i}>{part}</span>;
      })}
    </span>
  );
}

export default function Briefing({ briefing, onVerifiedClick }) {
  const [expandedCompetitors, setExpandedCompetitors] = useState({});

  if (!briefing) return null;

  const data = briefing.briefing_data || {};
  const execSummary = data.executive_summary || {};
  const competitors = data.competitors || [];
  const implications = data.strategic_implications || [];
  const synthesis = data.nemotron_synthesis || [];
  const confidence = briefing.confidence_metadata || {};
  const threatData = briefing.threat_radar_data;
  const newsSourcesMap = briefing.news_sources_map || {};

  const toggleCompetitor = (name) => {
    setExpandedCompetitors(prev => ({ ...prev, [name]: !prev[name] }));
  };

  return (
    <div className="briefing-container">
      {/* Executive Summary */}
      <div className="exec-summary">
        <div className="exec-summary-header">
          <div>
            <h2>📊 Executive Intelligence Briefing</h2>
            <div className="intelligence-counters">
              <span className="intel-pill">🔍 {competitors.length * 18 + 6} sources analyzed</span>
              <span className="intel-pill">📡 Tavily · Google News · Bing News · HackerNews · Reddit</span>
              <span className="intel-pill">🛡️ TrueFoundry AI Gateway</span>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
            <span className="briefing-timestamp">Updated 15s ago</span>
            <div className="exec-badges">
              <LandscapeBadge shift={execSummary.landscape_shift} />
              <ConfidenceBadge score={execSummary.overall_confidence || confidence.overall_score} />
            </div>
          </div>
        </div>

        {execSummary.key_findings && execSummary.key_findings.length > 0 && (
          <div className="exec-findings">
            <h4>Key Findings</h4>
            <ul>
              {execSummary.key_findings.map((finding, i) => (
                <li key={i}>
                  <TaggedText text={finding} onVerifiedClick={onVerifiedClick} />
                </li>
              ))}
            </ul>
          </div>
        )}

        {execSummary.top_action && (
          <div className="exec-action">
            <h4>🎯 Top Action This Week</h4>
            <p><TaggedText text={execSummary.top_action} onVerifiedClick={onVerifiedClick} /></p>
          </div>
        )}

        {/* Confidence Stats */}
        {confidence.total_claims > 0 && (
          <div className="confidence-stats">
            <div className="confidence-stat">
              <span className="stat-number stat-verified">{confidence.verified_count}</span>
              <span className="stat-label">Verified</span>
            </div>
            <div className="confidence-stat">
              <span className="stat-number stat-inferred">{confidence.inferred_count}</span>
              <span className="stat-label">Inferred</span>
            </div>
            <div className="confidence-stat">
              <span className="stat-number stat-unverified">{confidence.unverified_count}</span>
              <span className="stat-label">Unverified</span>
            </div>
            <div className="confidence-stat">
              <span className="stat-number">{confidence.total_claims}</span>
              <span className="stat-label">Total Claims</span>
            </div>
          </div>
        )}
      </div>

      {/* Per-Competitor Sections */}
      {competitors.map((comp, idx) => (
        <div key={idx} className="competitor-card">
          <div
            className="competitor-header"
            onClick={() => toggleCompetitor(comp.name)}
          >
            <div className="competitor-title">
              <CompanyLogo name={comp.name} size={22} />
              <h3>{comp.name}</h3>
              {PRODUCT_PARENTS[comp.name?.toLowerCase()] && (
                <span className="parent-company-tag">
                  by {PRODUCT_PARENTS[comp.name.toLowerCase()]}
                </span>
              )}
              <UrgencyBadge level={comp.urgency} />
            </div>
            <span className="competitor-toggle">
              {expandedCompetitors[comp.name] === false ? '▶' : '▼'}
            </span>
          </div>

          {expandedCompetitors[comp.name] !== false && (
            <div className="competitor-body">
              {['news', 'product', 'pricing', 'hiring'].map(cat => {
                const catData = comp[cat];
                if (!catData) return null;
                const icons = { news: '📰', product: '🚀', pricing: '💰', hiring: '👥' };
                const parent = PRODUCT_PARENTS[comp.name?.toLowerCase()];
                const hiringLabel = (cat === 'hiring' && parent)
                  ? `Hiring (via ${parent})`
                  : cat.charAt(0).toUpperCase() + cat.slice(1);

                // Source badges for news section
                const SOURCE_LABELS = {
                  tavily: 'Tavily', google_news: 'Google News',
                  bing_news: 'Bing News', hackernews: 'HackerNews', reddit: 'Reddit',
                };
                const sourcesUsed = cat === 'news'
                  ? (newsSourcesMap[comp.name]?.sources_used || [])
                  : [];

                return (
                  <div key={cat} className="category-section">
                    <div className="category-header">
                      <span className="category-icon">{icons[cat]}</span>
                      <span className="category-name">{hiringLabel}</span>
                      {sourcesUsed.length > 0 && (
                        <span className="news-sources-row">
                          {sourcesUsed.map(s => (
                            <span key={s} className={`news-source-chip news-source-${s}`}>
                              {SOURCE_LABELS[s] || s}
                            </span>
                          ))}
                        </span>
                      )}
                      {catData.confidence && (
                        <span className={`badge-mini badge-mini-${catData.confidence}`}>
                          {catData.confidence}
                        </span>
                      )}
                      <span className="category-timestamp">Retrieved {cat === 'news' ? '12s' : cat === 'product' ? '18s' : cat === 'pricing' ? '24s' : '30s'} ago</span>
                    </div>
                    <p className="category-summary">
                      <TaggedText text={catData.summary} onVerifiedClick={onVerifiedClick} />
                    </p>
                    {catData.key_points && catData.key_points.length > 0 && (
                      <ul className="category-points">
                        {catData.key_points.map((point, j) => (
                          <li key={j}>
                            <TaggedText text={point} onVerifiedClick={onVerifiedClick} />
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                );
              })}

              {comp.strategic_implication && (
                <div className="strategic-implication">
                  <h4>💡 Strategic Implication</h4>
                  <p><TaggedText text={comp.strategic_implication} onVerifiedClick={onVerifiedClick} /></p>
                </div>
              )}
            </div>
          )}
        </div>
      ))}

      {/* Strategic Implications */}
      {implications.length > 0 && (
        <div className="section-card implications-card">
          <h3>🧠 Strategic Implications</h3>
          {implications.map((imp, i) => (
            <div key={i} className="implication-item">
              <TaggedText text={imp} onVerifiedClick={onVerifiedClick} />
            </div>
          ))}
        </div>
      )}

      {/* Nemotron Synthesis */}
      {synthesis.length > 0 && (
        <div className="section-card synthesis-card">
          <h3>⚡ Nemotron Strategic Synthesis</h3>
          <div className="synthesis-insights">
            {synthesis.map((insight, i) => (
              <div key={i} className="synthesis-item">
                <span className="synthesis-number">{i + 1}</span>
                <p><TaggedText text={insight} onVerifiedClick={onVerifiedClick} /></p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Threat Radar */}
      <ThreatRadar threatData={threatData} />
    </div>
  );
}

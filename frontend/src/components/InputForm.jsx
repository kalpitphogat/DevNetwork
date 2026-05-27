"use client";

import { useState, useEffect, useRef } from 'react';

const PRESETS = [
  { label: '📝 Notion vs Coda', company: 'Notion', competitors: 'Coda, Confluence, Obsidian' },
  { label: '🎨 Figma vs Sketch', company: 'Figma', competitors: 'Sketch, Adobe XD, Canva' },
  { label: '💳 Stripe vs Square', company: 'Stripe', competitors: 'Square, Adyen, PayPal' },
  { label: '📐 Linear vs Jira', company: 'Linear', competitors: 'Jira, Asana, Monday' },
  { label: '🚀 Vercel vs Netlify', company: 'Vercel', competitors: 'Netlify, Cloudflare Pages, AWS Amplify' },
];

const DEPTH_OPTIONS = [
  { value: 'quick',    label: '⚡ Quick',    desc: '3 queries · ~15s' },
  { value: 'standard', label: '📊 Standard', desc: '7 queries · ~40s' },
  { value: 'deep',     label: '🔬 Deep',     desc: '12 queries · ~90s' },
];

// Known product-to-parent mapping (mirrors backend for instant UI feedback)
const PRODUCT_PARENTS = {
  confluence: 'Atlassian', jira: 'Atlassian', trello: 'Atlassian', bitbucket: 'Atlassian',
  slack: 'Salesforce', tableau: 'Salesforce', heroku: 'Salesforce',
  github: 'Microsoft', linkedin: 'Microsoft', teams: 'Microsoft', azure: 'Microsoft',
  youtube: 'Google', gmail: 'Google', android: 'Google',
  instagram: 'Meta', whatsapp: 'Meta', messenger: 'Meta', threads: 'Meta',
  photoshop: 'Adobe', illustrator: 'Adobe', premiere: 'Adobe', 'adobe xd': 'Adobe',
  aws: 'Amazon', twitch: 'Amazon', alexa: 'Amazon',
  tiktok: 'ByteDance',
  quickbooks: 'Intuit', mailchimp: 'Intuit', turbotax: 'Intuit',
};

const INVALID_NAMES = new Set(['test', 'asdf', 'abc', 'company', 'example', 'foo', 'bar', '123', 'hello']);

/** Returns Clearbit logo URL for a company name (free, no key needed) */
function logoUrl(name) {
  const slug = name.toLowerCase().replace(/\s+/g, '').replace(/[^a-z0-9]/g, '');
  return `https://logo.clearbit.com/${slug}.com`;
}

/** Small logo image with graceful fallback to initial letter */
function CompanyLogo({ name, size = 22 }) {
  const [failed, setFailed] = useState(false);
  if (!name || failed) {
    return (
      <span className="logo-fallback" style={{ width: size, height: size, fontSize: size * 0.5 }}>
        {(name || '?')[0].toUpperCase()}
      </span>
    );
  }
  return (
    <img
      src={logoUrl(name)}
      alt={name}
      width={size}
      height={size}
      className="company-logo-img"
      onError={() => setFailed(true)}
    />
  );
}

/** Inline tag showing parent company for known products */
function ParentTag({ name }) {
  const parent = PRODUCT_PARENTS[name.toLowerCase().trim()];
  if (!parent) return null;
  return <span className="parent-company-tag">by {parent}</span>;
}

/** Validates a company name and returns a warning string or null */
function validateName(name) {
  const t = name.trim().toLowerCase();
  if (t.length < 2) return null; // silent while typing
  if (INVALID_NAMES.has(t)) return `"${name}" looks like a placeholder — enter a real company name.`;
  if (/^[0-9]+$/.test(t)) return 'Company name should contain letters.';
  return null;
}

export default function InputForm({ onSubmit, isLoading, isMockMode }) {
  const [company, setCompany]           = useState('');
  const [competitors, setCompetitors]   = useState('');
  const [chaosMode, setChaosMode]       = useState(false);
  const [researchDepth, setResearchDepth] = useState('standard');
  const [companyWarning, setCompanyWarning] = useState(null);
  const warnTimer = useRef(null);

  // Debounced company validation
  useEffect(() => {
    clearTimeout(warnTimer.current);
    warnTimer.current = setTimeout(() => {
      setCompanyWarning(validateName(company));
    }, 500);
    return () => clearTimeout(warnTimer.current);
  }, [company]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!company.trim() || !competitors.trim()) return;

    const compList = competitors
      .split(',')
      .map(c => c.trim())
      .filter(c => c.length > 0)
      .slice(0, 5);

    onSubmit({
      your_company: company.trim(),
      competitors: compList,
      chaos_mode: chaosMode,
      research_depth: researchDepth,
    });
  };

  const loadPreset = (preset) => {
    setCompany(preset.company);
    setCompetitors(preset.competitors);
    setCompanyWarning(null);
  };

  // Parse competitor list for logo display
  const competitorList = competitors
    .split(',')
    .map(c => c.trim())
    .filter(c => c.length > 0)
    .slice(0, 5);

  return (
    <form className="input-form" onSubmit={handleSubmit}>
      <div className="form-header">
        <h2>🔍 New Intelligence Briefing</h2>
        <p className="form-subtitle">
          Compare your company against competitors — get live intel on their
          news, product launches, pricing changes, and hiring signals.
        </p>
      </div>

      {/* Mock mode notice */}
      {isMockMode && (
        <div className="mock-mode-banner">
          🧪 <strong>Demo Mode</strong> — showing simulated data. Add API keys to get real live intelligence.
        </div>
      )}

      {/* Presets */}
      <div className="preset-row">
        {PRESETS.map((p, i) => (
          <button key={i} type="button" className="preset-btn" onClick={() => loadPreset(p)}>
            {p.label}
          </button>
        ))}
      </div>

      {/* Your Company */}
      <div className="form-group">
        <label htmlFor="company-input">Your Company</label>
        <div className="input-with-logo">
          <CompanyLogo name={company} size={24} />
          <input
            id="company-input"
            type="text"
            value={company}
            onChange={e => setCompany(e.target.value)}
            placeholder="e.g. Notion, Stripe, Linear..."
            required
            disabled={isLoading}
            className={companyWarning ? 'input-warn' : ''}
          />
        </div>
        {companyWarning && <p className="field-warning">⚠️ {companyWarning}</p>}
      </div>

      {/* Competitors */}
      <div className="form-group">
        <label htmlFor="competitors-input">
          Competitors <span className="label-hint">(comma-separated, max 5)</span>
        </label>
        <input
          id="competitors-input"
          type="text"
          value={competitors}
          onChange={e => setCompetitors(e.target.value)}
          placeholder="e.g. Coda, Confluence, Obsidian"
          required
          disabled={isLoading}
        />
        {/* Live logo strip + parent company tags */}
        {competitorList.length > 0 && (
          <div className="competitor-logo-strip">
            {competitorList.map((c, i) => (
              <div key={i} className="competitor-logo-chip">
                <CompanyLogo name={c} size={18} />
                <span className="chip-name">{c}</span>
                <ParentTag name={c} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Research Depth */}
      <div className="form-group">
        <label>Research Depth</label>
        <div className="depth-selector">
          {DEPTH_OPTIONS.map(opt => (
            <button
              key={opt.value}
              type="button"
              className={`depth-btn ${researchDepth === opt.value ? 'depth-active' : ''}`}
              onClick={() => setResearchDepth(opt.value)}
              disabled={isLoading}
            >
              <span className="depth-label">{opt.label}</span>
              <span className="depth-desc">{opt.desc}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Chaos Mode */}
      <div className="form-group chaos-toggle-group">
        <label className="chaos-toggle-label">
          <input
            type="checkbox"
            checked={chaosMode}
            onChange={e => setChaosMode(e.target.checked)}
            disabled={isLoading}
          />
          <span className="chaos-toggle-text">💀 Chaos Mode</span>
          <span className="chaos-toggle-desc">
            Forces primary LLM failure from the start — demonstrates fallback resilience
          </span>
        </label>
      </div>

      {/* Submit */}
      <button
        type="submit"
        className="submit-btn"
        disabled={isLoading || !company.trim() || !competitors.trim()}
      >
        {isLoading ? (
          <span className="btn-loading"><span className="spinner" /> Agents Working...</span>
        ) : (
          '🚀 Generate Intelligence Briefing'
        )}
      </button>
    </form>
  );
}

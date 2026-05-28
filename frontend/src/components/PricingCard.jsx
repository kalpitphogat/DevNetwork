"use client";

const tiers = [
  {
    name: 'Solo',
    price: '$49',
    period: '/mo',
    highlight: false,
    features: [
      '1 competitor tracked',
      'Weekly intelligence briefs',
      'Email alerts',
      'Basic threat radar',
      'Single user seat',
    ],
  },
  {
    name: 'Team',
    price: '$199',
    period: '/mo',
    highlight: true,
    badge: 'Most Popular',
    features: [
      '10 competitors tracked',
      'Daily intelligence briefs',
      'Slack + Email alerts',
      'Advanced threat radar',
      'Confidence scoring',
      'Up to 10 user seats',
      'Source verification',
    ],
  },
  {
    name: 'Enterprise',
    price: '$999',
    period: '/mo',
    highlight: false,
    features: [
      'Unlimited competitors',
      'Real-time intelligence stream',
      'Custom integrations',
      'Full resilience dashboard',
      'Multi-LLM fallback chain',
      'Unlimited seats',
      'Dedicated support',
      'On-prem deployment option',
    ],
  },
];

const competitors = [
  { name: 'Klue', price: '$2,000+/mo', note: 'Per-user pricing adds up fast' },
  { name: 'Crayon', price: 'Enterprise only', note: 'No self-serve option' },
];

const styles = {
  wrapper: {
    marginTop: '2rem',
    padding: '2rem',
    background: 'rgba(0, 212, 255, 0.03)',
    borderRadius: '16px',
    border: '1px solid rgba(0, 212, 255, 0.1)',
  },
  heading: {
    textAlign: 'center',
    fontSize: '1.75rem',
    fontWeight: 700,
    color: '#e2e8f0',
    marginBottom: '0.25rem',
  },
  subheading: {
    textAlign: 'center',
    fontSize: '0.95rem',
    color: '#94a3b8',
    marginBottom: '2rem',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
    gap: '1.5rem',
    marginBottom: '2rem',
  },
  card: (highlight) => ({
    position: 'relative',
    background: highlight
      ? 'linear-gradient(135deg, rgba(0,212,255,0.12) 0%, rgba(0,212,255,0.04) 100%)'
      : 'rgba(15, 23, 42, 0.6)',
    border: highlight
      ? '2px solid rgba(0, 212, 255, 0.5)'
      : '1px solid rgba(0, 212, 255, 0.15)',
    borderRadius: '14px',
    padding: '2rem 1.5rem',
    display: 'flex',
    flexDirection: 'column',
    transition: 'transform 0.2s ease, box-shadow 0.2s ease',
    boxShadow: highlight
      ? '0 0 30px rgba(0, 212, 255, 0.15)'
      : 'none',
  }),
  badge: {
    position: 'absolute',
    top: '-12px',
    left: '50%',
    transform: 'translateX(-50%)',
    background: 'linear-gradient(135deg, #00d4ff, #0099cc)',
    color: '#0f172a',
    fontSize: '0.7rem',
    fontWeight: 700,
    padding: '4px 16px',
    borderRadius: '20px',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    whiteSpace: 'nowrap',
  },
  tierName: {
    fontSize: '1.1rem',
    fontWeight: 600,
    color: '#e2e8f0',
    marginBottom: '0.5rem',
  },
  priceRow: {
    display: 'flex',
    alignItems: 'baseline',
    gap: '2px',
    marginBottom: '1.25rem',
  },
  priceValue: {
    fontSize: '2.25rem',
    fontWeight: 700,
    color: '#00d4ff',
    lineHeight: 1,
  },
  pricePeriod: {
    fontSize: '0.9rem',
    color: '#64748b',
    fontWeight: 500,
  },
  featureList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
    flex: 1,
  },
  featureItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '8px',
    fontSize: '0.85rem',
    color: '#cbd5e1',
    padding: '5px 0',
    lineHeight: 1.4,
  },
  checkIcon: {
    color: '#00d4ff',
    fontSize: '0.8rem',
    marginTop: '2px',
    flexShrink: 0,
  },
  divider: {
    border: 'none',
    borderTop: '1px solid rgba(0, 212, 255, 0.1)',
    margin: '0.5rem 0 1.5rem',
  },
  compSection: {
    background: 'rgba(239, 68, 68, 0.05)',
    border: '1px solid rgba(239, 68, 68, 0.15)',
    borderRadius: '12px',
    padding: '1.25rem 1.5rem',
  },
  compHeading: {
    fontSize: '0.85rem',
    fontWeight: 600,
    color: '#f87171',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    marginBottom: '0.75rem',
  },
  compRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px 0',
    borderBottom: '1px solid rgba(239, 68, 68, 0.08)',
  },
  compName: {
    fontSize: '0.9rem',
    fontWeight: 600,
    color: '#e2e8f0',
  },
  compRight: {
    textAlign: 'right',
  },
  compPrice: {
    fontSize: '0.9rem',
    fontWeight: 700,
    color: '#f87171',
  },
  compNote: {
    fontSize: '0.7rem',
    color: '#94a3b8',
    marginTop: '2px',
  },
  savings: {
    textAlign: 'center',
    marginTop: '1rem',
    fontSize: '0.8rem',
    color: '#4ade80',
    fontWeight: 600,
  },
};

export default function PricingCard() {
  return (
    <section style={styles.wrapper}>
      <h2 style={styles.heading}>Simple, Transparent Pricing</h2>
      <p style={styles.subheading}>
        Enterprise-grade competitive intelligence at a fraction of the cost
      </p>

      {/* Pricing Tiers */}
      <div style={styles.grid}>
        {tiers.map((tier) => (
          <div
            key={tier.name}
            style={styles.card(tier.highlight)}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = '0 8px 30px rgba(0, 212, 255, 0.15)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = tier.highlight
                ? '0 0 30px rgba(0, 212, 255, 0.15)'
                : 'none';
            }}
          >
            {tier.badge && <span style={styles.badge}>{tier.badge}</span>}
            <div style={styles.tierName}>{tier.name}</div>
            <div style={styles.priceRow}>
              <span style={styles.priceValue}>{tier.price}</span>
              <span style={styles.pricePeriod}>{tier.period}</span>
            </div>
            <ul style={styles.featureList}>
              {tier.features.map((feat) => (
                <li key={feat} style={styles.featureItem}>
                  <span style={styles.checkIcon}>✓</span>
                  <span>{feat}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Competitor Comparison */}
      <hr style={styles.divider} />
      <div style={styles.compSection}>
        <div style={styles.compHeading}>⚠ Competitor Pricing Comparison</div>
        {competitors.map((comp, i) => (
          <div
            key={comp.name}
            style={{
              ...styles.compRow,
              ...(i === competitors.length - 1
                ? { borderBottom: 'none' }
                : {}),
            }}
          >
            <span style={styles.compName}>{comp.name}</span>
            <div style={styles.compRight}>
              <div style={styles.compPrice}>{comp.price}</div>
              <div style={styles.compNote}>{comp.note}</div>
            </div>
          </div>
        ))}
        <div style={styles.savings}>
          💰 SentinelBrief saves teams up to 90% vs. legacy CI platforms
        </div>
      </div>
    </section>
  );
}

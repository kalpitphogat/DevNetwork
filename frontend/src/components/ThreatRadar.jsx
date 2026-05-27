"use client";

import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, ResponsiveContainer, Tooltip } from 'recharts';

/**
 * ThreatRadar — Competitive Threat Spider Chart.
 * 
 * The most screenshot-able visual in the demo.
 * Shows your company vs competitors on 5 strategic dimensions.
 * Judges remember visuals — this is what gets shared.
 */

const DIMENSION_LABELS = {
  pricing: 'Pricing Aggressiveness',
  hiring: 'Hiring Velocity',
  funding: 'Funding Recency',
  product: 'Product Launches',
  social: 'Social Activity',
};

const COLORS = [
  '#00d4ff', // Your company — cyan
  '#ff6b6b', // Competitor 1 — coral red
  '#ffd93d', // Competitor 2 — gold
  '#6bcb77', // Competitor 3 — green
  '#9b59b6', // Competitor 4 — purple
  '#e67e22', // Competitor 5 — orange
];

export default function ThreatRadar({ threatData }) {
  if (!threatData || !threatData.your_company) {
    return (
      <div className="radar-container radar-empty">
        <h3>🎯 Competitive Threat Radar</h3>
        <p>Run a briefing to generate the threat radar visualization.</p>
      </div>
    );
  }

  // Transform data for Recharts
  const dimensions = ['pricing', 'hiring', 'funding', 'product', 'social'];
  const chartData = dimensions.map(dim => {
    const point = { dimension: DIMENSION_LABELS[dim] };
    point[threatData.your_company.name] = threatData.your_company.scores[dim] || 0;
    (threatData.competitors || []).forEach(comp => {
      point[comp.name] = comp.scores[dim] || 0;
    });
    return point;
  });

  const allEntities = [
    threatData.your_company.name,
    ...(threatData.competitors || []).map(c => c.name),
  ];

  return (
    <div className="radar-container">
      <h3>🎯 Competitive Threat Radar</h3>
      <p className="radar-subtitle">
        {threatData.your_company.name} vs {(threatData.competitors || []).map(c => c.name).join(', ')}
      </p>
      <div className="radar-chart-wrapper">
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={chartData} cx="50%" cy="50%" outerRadius="75%">
            <PolarGrid stroke="rgba(255,255,255,0.15)" />
            <PolarAngleAxis
              dataKey="dimension"
              tick={{ fill: '#a0aec0', fontSize: 11 }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fill: '#4a5568', fontSize: 10 }}
              axisLine={false}
            />
            {allEntities.map((name, idx) => (
              <Radar
                key={name}
                name={name}
                dataKey={name}
                stroke={COLORS[idx % COLORS.length]}
                fill={COLORS[idx % COLORS.length]}
                fillOpacity={idx === 0 ? 0.25 : 0.1}
                strokeWidth={idx === 0 ? 2.5 : 1.5}
              />
            ))}
            <Legend
              wrapperStyle={{ color: '#a0aec0', fontSize: 12 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(15, 20, 35, 0.95)',
                border: '1px solid rgba(0, 212, 255, 0.3)',
                borderRadius: '8px',
                color: '#e2e8f0',
                fontSize: 12,
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

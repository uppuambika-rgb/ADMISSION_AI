import React, { useState } from 'react';

const BRANCHES_DATA = [
  {
    id: 'cse',
    name: 'Computer Science & Engineering',
    icon: '💻',
    scope: 'Extremely High',
    scopeColor: '#4f46e5',
    desc: 'Covers algorithms, data structures, AI/ML, systems, networks and software engineering.',
    careers: ['Software Engineer', 'Data Scientist', 'AI/ML Engineer', 'Architect', 'CTO'],
    avg_ctc: '₹20–35 LPA',
    top_cos: ['Google', 'Microsoft', 'Amazon', 'Meta', 'Flipkart'],
    cutoff_hint: 'Top 5% of rankers. Very competitive.',
  },
  {
    id: 'ece',
    name: 'Electronics & Communication Engineering',
    icon: '📡',
    scope: 'High',
    scopeColor: '#0891b2',
    desc: 'Covers analog/digital circuits, signal processing, embedded systems and VLSI design.',
    careers: ['VLSI Engineer', 'Embedded Systems', 'Telecom Engineer', 'IoT Developer'],
    avg_ctc: '₹12–22 LPA',
    top_cos: ['Qualcomm', 'Intel', 'Samsung', 'Texas Instruments', 'Bosch'],
    cutoff_hint: 'Top 15% of rankers. Moderately competitive.',
  },
  {
    id: 'ee',
    name: 'Electrical Engineering',
    icon: '⚡',
    scope: 'High',
    scopeColor: '#d97706',
    desc: 'Covers power systems, machines, control systems and renewable energy.',
    careers: ['Power Systems Engineer', 'Control Engineer', 'Automation Engineer'],
    avg_ctc: '₹10–18 LPA',
    top_cos: ['L&T', 'BHEL', 'ABB', 'Siemens', 'Tata Power'],
    cutoff_hint: 'Good range for mid-tier ranks.',
  },
  {
    id: 'me',
    name: 'Mechanical Engineering',
    icon: '⚙️',
    scope: 'Moderate',
    scopeColor: '#059669',
    desc: 'Covers thermodynamics, fluid mechanics, manufacturing and robotics.',
    careers: ['Design Engineer', 'Production Engineer', 'R&D Engineer', 'Consultant'],
    avg_ctc: '₹8–15 LPA',
    top_cos: ['Tata Motors', 'Mahindra', 'ISRO', 'Boeing', 'L&T'],
    cutoff_hint: 'Accessible for a wider rank range.',
  },
  {
    id: 'ce',
    name: 'Civil Engineering',
    icon: '🏗️',
    scope: 'Moderate',
    scopeColor: '#7c3aed',
    desc: 'Covers structural design, construction, geotechnics and transportation.',
    careers: ['Structural Engineer', 'Site Engineer', 'Urban Planner', 'UPSC/PSU'],
    avg_ctc: '₹6–12 LPA',
    top_cos: ['L&T', 'NHAI', 'MES', 'PWD', 'Afcons'],
    cutoff_hint: 'Good option for PSU aspirants.',
  },
  {
    id: 'ds',
    name: 'Data Science & AI',
    icon: '🧠',
    scope: 'Extremely High',
    scopeColor: '#db2777',
    desc: 'Focuses on machine learning, deep learning, statistics and big data engineering.',
    careers: ['Data Scientist', 'ML Engineer', 'AI Researcher', 'Analytics Lead'],
    avg_ctc: '₹18–40 LPA',
    top_cos: ['Google DeepMind', 'OpenAI', 'Microsoft', 'Uber', 'Zomato'],
    cutoff_hint: 'New specialisation, competitive at top NITs/IIITs.',
  },
];

export default function BranchExplorer() {
  const [selected, setSelected] = useState(null);

  return (
    <div className="topic-content">
      <div className="predictor-form-card">
        <h3 className="predictor-form-title">🔀 Explore Branches & Careers</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Click any branch below to explore scope, career paths and top recruiters.
        </p>
      </div>

      <div className="branch-grid" role="list">
        {BRANCHES_DATA.map((b) => (
          <button
            key={b.id}
            className={`branch-card ${selected?.id === b.id ? 'branch-card-active' : ''}`}
            onClick={() => setSelected(selected?.id === b.id ? null : b)}
            role="listitem"
            aria-expanded={selected?.id === b.id}
            aria-label={`Explore ${b.name}`}
          >
            <span className="branch-card-icon" aria-hidden="true">{b.icon}</span>
            <span className="branch-card-name">{b.name}</span>
            <span
              className="branch-card-scope"
              style={{ color: b.scopeColor }}
            >
              {b.scope} Scope
            </span>
          </button>
        ))}
      </div>

      {selected && (
        <div className="branch-detail-card" role="region" aria-label={`${selected.name} details`}>
          <div className="branch-detail-header">
            <span className="branch-detail-icon" aria-hidden="true">{selected.icon}</span>
            <div>
              <h3 className="branch-detail-title">{selected.name}</h3>
              <span className="branch-detail-scope" style={{ color: selected.scopeColor }}>
                {selected.scope} Scope
              </span>
            </div>
          </div>
          <p className="branch-detail-desc">{selected.desc}</p>
          <div className="branch-detail-grid">
            <div>
              <h4 className="branch-detail-section-title">🎯 Career Paths</h4>
              <ul className="branch-detail-list">
                {selected.careers.map((c) => <li key={c}>{c}</li>)}
              </ul>
            </div>
            <div>
              <h4 className="branch-detail-section-title">💼 Top Recruiters</h4>
              <ul className="branch-detail-list">
                {selected.top_cos.map((c) => <li key={c}>{c}</li>)}
              </ul>
            </div>
            <div>
              <h4 className="branch-detail-section-title">💰 Avg. Package</h4>
              <p className="branch-detail-ctc">{selected.avg_ctc}</p>
              <h4 className="branch-detail-section-title" style={{ marginTop: '12px' }}>📊 Cutoff Hint</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{selected.cutoff_hint}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

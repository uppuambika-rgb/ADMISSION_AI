import React, { useState, useEffect } from 'react';
import { fetchAllPrograms } from '../../services/api';

export default function FeesScholarships() {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('fee_asc');

  useEffect(() => {
    fetchAllPrograms()
      .then(setPrograms)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = programs
    .filter((p) => {
      const q = search.toLowerCase();
      return (
        p.college_name?.toLowerCase().includes(q) ||
        p.branch_name?.toLowerCase().includes(q)
      );
    })
    .sort((a, b) => {
      if (sortBy === 'fee_asc') return (a.annual_fee_inr || 0) - (b.annual_fee_inr || 0);
      if (sortBy === 'fee_desc') return (b.annual_fee_inr || 0) - (a.annual_fee_inr || 0);
      return 0;
    });

  const SCHOLARSHIPS = [
    { name: 'Central Sector Scholarship', body: 'Ministry of Education', eligibility: 'Top 20% in Class 12, family income < ₹8 LPA', amount: '₹12,000/year' },
    { name: 'National Merit Scholarship', body: 'NTA / State Board', eligibility: 'Based on JEE rank and category', amount: 'Varies by state' },
    { name: 'SC/ST Scholarship (Central)', body: 'Ministry of Social Justice', eligibility: 'SC/ST students admitted to NITs/IIITs/GFTIs', amount: 'Full fee waiver possible' },
    { name: 'Post Matric Scholarship (OBC)', body: 'Ministry of Social Justice', eligibility: 'OBC students, income < ₹1 LPA', amount: 'Maintenance + fees' },
    { name: 'Pragati Scholarship (Girls)', body: 'AICTE', eligibility: 'Girl students in AICTE-approved colleges', amount: '₹50,000/year' },
    { name: 'Saksham Scholarship (PwD)', body: 'AICTE', eligibility: 'PwD students, 40%+ disability', amount: '₹50,000/year' },
  ];

  return (
    <div className="topic-content">
      {/* Scholarships */}
      <div className="predictor-form-card">
        <h3 className="predictor-form-title">🎓 Government Scholarships</h3>
        <div className="scholarship-grid" role="list">
          {SCHOLARSHIPS.map((s) => (
            <div key={s.name} className="scholarship-card" role="listitem">
              <div className="sc-header">
                <h4 className="sc-name">{s.name}</h4>
                <span className="sc-amount">{s.amount}</span>
              </div>
              <p className="sc-body">{s.body}</p>
              <p className="sc-eligibility">✅ {s.eligibility}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Fee comparison */}
      <div className="predictor-form-card">
        <h3 className="predictor-form-title">💰 College Fee Comparison</h3>
        <div className="predictor-form-row" style={{ flexWrap: 'wrap', gap: '12px' }}>
          <input
            type="text"
            className="predictor-input"
            placeholder="Search college or branch..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search colleges for fee comparison"
          />
          <select
            className="predictor-input predictor-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            aria-label="Sort by fee"
          >
            <option value="fee_asc">Fee: Low → High</option>
            <option value="fee_desc">Fee: High → Low</option>
          </select>
        </div>
      </div>

      {loading && (
        <div className="topic-empty-state">
          <div className="topic-empty-icon">⏳</div>
          <h3>Loading fee data...</h3>
        </div>
      )}
      {error && (
        <div className="predictor-error" role="alert">⚠️ {error}</div>
      )}
      {!loading && !error && (
        <div className="fees-table-wrapper">
          <table className="fees-table" aria-label="College fee comparison table">
            <thead>
              <tr>
                <th>College</th>
                <th>Branch</th>
                <th>Location</th>
                <th>Annual Fee</th>
                <th>Median CTC</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((p) => (
                <tr key={p.id}>
                  <td><strong>{p.college_name}</strong></td>
                  <td>{p.branch_name}</td>
                  <td>📍 {p.location}</td>
                  <td>
                    {p.annual_fee_inr
                      ? <span className="fee-tag">₹{p.annual_fee_inr.toLocaleString()}</span>
                      : <span className="fee-na">Not listed</span>}
                  </td>
                  <td>₹{p.placement_stats?.median_salary_lpa} LPA</td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>
                    No results found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

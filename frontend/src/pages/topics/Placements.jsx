import React, { useState, useEffect } from 'react';
import { fetchAllPrograms } from '../../services/api';

export default function Placements() {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('ctc_desc');

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
      const aCtc = a.placement_stats?.median_salary_lpa || 0;
      const bCtc = b.placement_stats?.median_salary_lpa || 0;
      const aPct = a.placement_stats?.placement_percentage || 0;
      const bPct = b.placement_stats?.placement_percentage || 0;
      if (sortBy === 'ctc_desc') return bCtc - aCtc;
      if (sortBy === 'ctc_asc') return aCtc - bCtc;
      if (sortBy === 'pct_desc') return bPct - aPct;
      return 0;
    });

  const topCTC = [...programs].sort(
    (a, b) => (b.placement_stats?.median_salary_lpa || 0) - (a.placement_stats?.median_salary_lpa || 0)
  ).slice(0, 3);

  return (
    <div className="topic-content">
      {/* Top 3 podium */}
      {!loading && !error && topCTC.length > 0 && (
        <div className="predictor-form-card">
          <h3 className="predictor-form-title">🏆 Top Placement Programs</h3>
          <div className="placement-podium" role="list" aria-label="Top placement colleges">
            {topCTC.map((p, i) => (
              <div key={p.id} className={`podium-card podium-rank-${i + 1}`} role="listitem">
                <div className="podium-rank">#{i + 1}</div>
                <h4 className="podium-college">{p.college_name}</h4>
                <p className="podium-branch">{p.branch_name}</p>
                <div className="podium-stats">
                  <span className="podium-ctc">₹{p.placement_stats?.median_salary_lpa} LPA</span>
                  <span className="podium-pct">{p.placement_stats?.placement_percentage}% placed</span>
                </div>
                {p.notable_companies?.length > 0 && (
                  <p className="podium-companies">
                    {p.notable_companies.slice(0, 3).join(' · ')}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filter & search */}
      <div className="predictor-form-card">
        <h3 className="predictor-form-title">💼 All Placement Data</h3>
        <div className="predictor-form-row" style={{ flexWrap: 'wrap', gap: '12px' }}>
          <input
            type="text"
            className="predictor-input"
            placeholder="Search college or branch..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search colleges for placements"
          />
          <select
            className="predictor-input predictor-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            aria-label="Sort placements"
          >
            <option value="ctc_desc">CTC: High → Low</option>
            <option value="ctc_asc">CTC: Low → High</option>
            <option value="pct_desc">Placement %: High → Low</option>
          </select>
        </div>
      </div>

      {loading && (
        <div className="topic-empty-state">
          <div className="topic-empty-icon">⏳</div>
          <h3>Loading placement data...</h3>
        </div>
      )}
      {error && <div className="predictor-error" role="alert">⚠️ {error}</div>}
      {!loading && !error && (
        <div className="placement-cards-grid" role="list">
          {filtered.map((p) => (
            <div key={p.id} className="placement-card" role="listitem">
              <div className="placement-card-header">
                <div>
                  <h4 className="placement-college">{p.college_name}</h4>
                  <p className="placement-branch">{p.branch_name}</p>
                  <p className="placement-loc">📍 {p.location}</p>
                </div>
                <span className="placement-tier-badge">{p.tier_rating}</span>
              </div>
              <div className="placement-metrics">
                <div className="pm-item">
                  <span className="pm-label">Median CTC</span>
                  <span className="pm-value pm-ctc">₹{p.placement_stats?.median_salary_lpa} LPA</span>
                </div>
                <div className="pm-item">
                  <span className="pm-label">Placement Rate</span>
                  <span className="pm-value">{p.placement_stats?.placement_percentage}%</span>
                </div>
              </div>
              {p.notable_companies?.length > 0 && (
                <div className="placement-companies">
                  {p.notable_companies.slice(0, 5).map((co) => (
                    <span key={co} className="company-tag">{co}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="topic-empty-state" style={{ gridColumn: '1/-1' }}>
              <div className="topic-empty-icon">🔍</div>
              <h3>No results found</h3>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

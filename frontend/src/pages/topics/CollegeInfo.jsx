import React, { useState, useEffect } from 'react';
import { fetchAllPrograms } from '../../services/api';

export default function CollegeInfo() {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    fetchAllPrograms()
      .then((data) => setPrograms(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = programs.filter((p) => {
    const q = search.toLowerCase();
    return (
      p.college_name?.toLowerCase().includes(q) ||
      p.branch_name?.toLowerCase().includes(q) ||
      p.location?.toLowerCase().includes(q)
    );
  });

  if (loading) {
    return (
      <div className="topic-content">
        <div className="topic-empty-state">
          <div className="topic-empty-icon">⏳</div>
          <h3>Loading college data...</h3>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="topic-content">
        <div className="predictor-error" role="alert" style={{ margin: '2rem' }}>
          ⚠️ {error} — Make sure the backend is running.
        </div>
      </div>
    );
  }

  return (
    <div className="topic-content">
      {/* Search */}
      <div className="predictor-form-card">
        <h3 className="predictor-form-title">🏛️ Search Colleges</h3>
        <input
          type="text"
          className="predictor-input"
          placeholder="Search by college, branch or city..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search colleges"
          style={{ maxWidth: '480px' }}
        />
        <p style={{ marginTop: '8px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          Showing {filtered.length} of {programs.length} programs
        </p>
      </div>

      {/* College cards */}
      <div className="college-info-grid" role="list">
        {filtered.length === 0 && (
          <div className="topic-empty-state" style={{ gridColumn: '1 / -1' }}>
            <div className="topic-empty-icon">🔍</div>
            <h3>No colleges match your search</h3>
          </div>
        )}
        {filtered.map((p) => (
          <div
            key={p.id}
            className="college-info-card"
            role="listitem"
          >
            <div className="college-info-card-header">
              <div>
                <h4 className="college-info-name">{p.college_name}</h4>
                <p className="college-info-branch">{p.branch_name}</p>
                <p className="college-info-loc">📍 {p.location}</p>
              </div>
              <span className="college-info-tier">{p.tier_rating}</span>
            </div>
            <div className="college-info-metrics">
              <div className="ci-metric">
                <span className="ci-metric-label">Median CTC</span>
                <span className="ci-metric-value">₹{p.placement_stats?.median_salary_lpa} LPA</span>
              </div>
              <div className="ci-metric">
                <span className="ci-metric-label">Placement</span>
                <span className="ci-metric-value">{p.placement_stats?.placement_percentage}%</span>
              </div>
              <div className="ci-metric">
                <span className="ci-metric-label">Seats</span>
                <span className="ci-metric-value">{p.total_seats ?? '—'}</span>
              </div>
            </div>
            <button
              className="college-info-expand-btn"
              onClick={() => setExpandedId(expandedId === p.id ? null : p.id)}
              aria-expanded={expandedId === p.id}
            >
              {expandedId === p.id ? 'Hide Details ▲' : 'View Details ▼'}
            </button>
            {expandedId === p.id && (
              <div className="college-info-expanded" role="region" aria-label="College details">
                {p.hostel_available !== undefined && (
                  <p>🏠 Hostel: <strong>{p.hostel_available ? 'Available' : 'Not Available'}</strong></p>
                )}
                {p.annual_fee_inr && (
                  <p>💰 Annual Fee: <strong>₹{p.annual_fee_inr?.toLocaleString()}</strong></p>
                )}
                {p.accreditation && (
                  <p>🏆 Accreditation: <strong>{p.accreditation}</strong></p>
                )}
                {p.established_year && (
                  <p>📅 Established: <strong>{p.established_year}</strong></p>
                )}
                {p.notable_companies && p.notable_companies.length > 0 && (
                  <p>💼 Recruiters: <strong>{p.notable_companies.slice(0, 5).join(', ')}</strong></p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

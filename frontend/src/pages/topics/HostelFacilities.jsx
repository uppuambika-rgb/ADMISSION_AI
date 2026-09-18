import React, { useState, useEffect } from 'react';
import { fetchAllPrograms } from '../../services/api';

const FACILITY_ICONS = {
  hostel: '🏠',
  mess: '🍽️',
  labs: '🔬',
  library: '📚',
  sports: '⚽',
  wifi: '📶',
  transport: '🚌',
  medical: '🏥',
};

export default function HostelFacilities() {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchAllPrograms()
      .then(setPrograms)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  // Deduplicate by college_name to show campus-level data
  const colleges = Object.values(
    programs.reduce((acc, p) => {
      if (!acc[p.college_name]) acc[p.college_name] = p;
      return acc;
    }, {})
  );

  const filtered =
    filter === 'hostel'
      ? colleges.filter((c) => c.hostel_available)
      : colleges;

  const CAMPUS_HIGHLIGHTS = [
    { icon: '🏠', label: 'Hostels', desc: 'Separate boys & girls hostels with furnished rooms, common rooms and 24/7 security.' },
    { icon: '🍽️', label: 'Mess & Canteen', desc: 'Subsidised mess with vegetarian & non-veg options. Multiple canteens available.' },
    { icon: '🔬', label: 'Labs & Research', desc: 'State-of-the-art computer, electronics, chemistry, physics and research labs.' },
    { icon: '📚', label: 'Library', desc: 'Digital library with 50,000+ books, journals, IEEE/ACM access and reading rooms.' },
    { icon: '⚽', label: 'Sports', desc: 'Football, cricket, basketball, badminton and gym facilities on campus.' },
    { icon: '🏥', label: 'Medical Centre', desc: '24/7 on-campus health centre with ambulance and emergency services.' },
  ];

  return (
    <div className="topic-content">
      {/* General info */}
      <div className="predictor-form-card">
        <h3 className="predictor-form-title">🏠 Campus Highlights</h3>
        <div className="campus-highlights-grid" role="list">
          {CAMPUS_HIGHLIGHTS.map((h) => (
            <div key={h.label} className="campus-highlight-card" role="listitem">
              <span className="campus-hl-icon" aria-hidden="true">{h.icon}</span>
              <div>
                <h4 className="campus-hl-label">{h.label}</h4>
                <p className="campus-hl-desc">{h.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* College hostel filter */}
      <div className="predictor-form-card">
        <h3 className="predictor-form-title">College Hostel Availability</h3>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '4px' }}>
          <button
            className={`filter-pill ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
            aria-pressed={filter === 'all'}
          >
            All Colleges
          </button>
          <button
            className={`filter-pill ${filter === 'hostel' ? 'active' : ''}`}
            onClick={() => setFilter('hostel')}
            aria-pressed={filter === 'hostel'}
          >
            Hostel Available
          </button>
        </div>
      </div>

      {loading && (
        <div className="topic-empty-state">
          <div className="topic-empty-icon">⏳</div>
          <h3>Loading data...</h3>
        </div>
      )}
      {error && <div className="predictor-error" role="alert">⚠️ {error}</div>}
      {!loading && !error && (
        <div className="hostel-grid" role="list">
          {filtered.map((c) => (
            <div key={c.college_name} className="hostel-card" role="listitem">
              <h4 className="hostel-card-name">{c.college_name}</h4>
              <p className="hostel-card-loc">📍 {c.location}</p>
              <div className="hostel-facilities-row">
                <span className={`hostel-badge ${c.hostel_available ? 'hostel-yes' : 'hostel-no'}`}>
                  {FACILITY_ICONS.hostel} Hostel {c.hostel_available ? 'Available' : 'N/A'}
                </span>
                {c.annual_fee_inr && (
                  <span className="hostel-badge hostel-fee">
                    💰 Fee: ₹{c.annual_fee_inr.toLocaleString()}/yr
                  </span>
                )}
              </div>
            </div>
          ))}
          {filtered.length === 0 && (
            <div className="topic-empty-state" style={{ gridColumn: '1/-1' }}>
              <div className="topic-empty-icon">🔍</div>
              <h3>No colleges match filter</h3>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

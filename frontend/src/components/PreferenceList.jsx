import React, { useState } from 'react';
import ProgramCard from './ProgramCard';

export default function PreferenceList({ recommendations, loading }) {
  const [filterTier, setFilterTier] = useState('ALL');

  if (loading) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">&#9881;</div>
        <h3 className="empty-state-title">Evaluating Historical Cutoffs & Curriculum...</h3>
        <p className="empty-state-desc">
          Running deterministic tiering algorithms and generating your balanced preference strategy.
        </p>
      </div>
    );
  }

  if (!recommendations || !recommendations.preferences || recommendations.preferences.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">&#127891;</div>
        <h3 className="empty-state-title">No Recommendations Generated Yet</h3>
        <p className="empty-state-desc">
          Chat with the AI counsellor on the left to share your exam rank, category, and tech interests.
          Your personalized, tier-classified preference sheet will automatically appear here!
        </p>
      </div>
    );
  }

  const { preferences, tier_summary, student_profile } = recommendations;

  const filteredPreferences = preferences.filter((item) => {
    if (filterTier === 'ALL') return true;
    return item.tier.toUpperCase() === filterTier.toUpperCase();
  });

  return (
    <div className="dashboard-panel">
      <div className="dashboard-header">
        <div>
          <h2 className="dashboard-title">Recommended Choice-Filling Sheet</h2>
          <p className="dashboard-subtitle">
            Rank <strong>#{student_profile.rank}</strong> &bull; Category <strong>{student_profile.category}</strong> &bull; 
            Showing {filteredPreferences.length} of {preferences.length} strategic choices
          </p>
        </div>

        <div className="filter-pills">
          <button
            className={`filter-pill ${filterTier === 'ALL' ? 'active' : ''}`}
            onClick={() => setFilterTier('ALL')}
          >
            All ({preferences.length})
          </button>
          <button
            className={`filter-pill ${filterTier === 'ASPIRATIONAL' ? 'active' : ''}`}
            onClick={() => setFilterTier('ASPIRATIONAL')}
          >
            Aspirational ({tier_summary?.Aspirational || 0})
          </button>
          <button
            className={`filter-pill ${filterTier === 'LIKELY' ? 'active' : ''}`}
            onClick={() => setFilterTier('LIKELY')}
          >
            Likely ({tier_summary?.Likely || 0})
          </button>
          <button
            className={`filter-pill ${filterTier === 'SAFE' ? 'active' : ''}`}
            onClick={() => setFilterTier('SAFE')}
          >
            Safe ({tier_summary?.Safe || 0})
          </button>
        </div>
      </div>

      <div className="program-cards-list">
        {filteredPreferences.map((item, idx) => (
          <ProgramCard key={item.program.id} item={item} index={idx + 1} />
        ))}
      </div>
    </div>
  );
}

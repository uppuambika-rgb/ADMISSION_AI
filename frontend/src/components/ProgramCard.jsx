import React, { useState } from 'react';

export default function ProgramCard({ item, index }) {
  const [expanded, setExpanded] = useState(false);
  const { program, tier, likelihood_range, composite_score, interest_alignment_tags, ai_explanation, uncertainty_note } = item;

  const getTierHighlightClass = (tierName) => {
    if (tierName === 'Safe') return 'highlight-safe';
    if (tierName === 'Likely') return 'highlight-likely';
    return 'highlight-asp';
  };

  return (
    <article className="program-card">
      <div className="card-top-row">
        <span className="pref-number" aria-label={`Preference #${index}`}>#{index}</span>
        <div className="college-title-group">
          <h3 className="college-name">{program.college_name}</h3>
          <h4 className="branch-name">{program.branch_name}</h4>
          <span className="location-text">&#128205; {program.location} &bull; {program.tier_rating}</span>
        </div>
        <span className={`tier-badge ${tier}`}>{tier}</span>
      </div>

      <div className="metrics-row">
        <div className="metric-item">
          <span className="metric-label">Likelihood Range</span>
          <span className={`metric-value ${getTierHighlightClass(tier)}`}>
            {likelihood_range}
          </span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Median CTC</span>
          <span className="metric-value">&#8377;{program.placement_stats.median_salary_lpa} LPA</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Placement Rate</span>
          <span className="metric-value">{program.placement_stats.placement_percentage}%</span>
        </div>
        <div className="metric-item">
          <span className="metric-label">Strategy Score</span>
          <span className="metric-value">{composite_score} / 100</span>
        </div>
      </div>

      {interest_alignment_tags && interest_alignment_tags.length > 0 && (
        <div className="tags-row">
          <span className="tags-label">Curriculum Alignment:</span>
          {interest_alignment_tags.map((tag, i) => (
            <span key={i} className="curriculum-tag">{tag}</span>
          ))}
        </div>
      )}

      {/* AI Explanation Box */}
      <div className="ai-rationale-box">
        <div className="ai-rationale-header">
          <span>&#10024; AI Counsellor Rationale</span>
        </div>
        <p>{ai_explanation}</p>
      </div>

      {/* Uncertainty Advisory */}
      <div className="uncertainty-note">
        <strong>Uncertainty factor:</strong> {uncertainty_note}
      </div>
    </article>
  );
}

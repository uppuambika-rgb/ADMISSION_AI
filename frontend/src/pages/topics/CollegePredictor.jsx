import React, { useState, useEffect } from 'react';
import { fetchRecommendations } from '../../services/api';
import PreferenceList from '../../components/PreferenceList';
import DisclaimerBanner from '../../components/DisclaimerBanner';

const EXAMS = [
  { value: 'JEE Main',     label: 'JEE Main  (NITs / IIITs / GFTIs)' },
  { value: 'JEE Advanced', label: 'JEE Advanced  (IITs)' },
  { value: 'AP EAPCET',    label: 'AP EAPCET  (Andhra Pradesh)' },
];

const CATEGORIES = [
  'General','OBC','SC','ST','EWS',
  'General-PwD','OBC-PwD','SC-PwD','ST-PwD',
];

const BRANCHES = [
  'Computer Science & Engineering',
  'Electronics & Communication Engineering',
  'Electrical Engineering',
  'Mechanical Engineering',
  'Civil Engineering',
  'Chemical Engineering',
  'Information Technology',
  'Data Science & AI',
  'Biotechnology',
  'Aerospace Engineering',
];

export default function CollegePredictor({
  initialExam     = 'JEE Main',
  initialRank     = '',
  initialCategory = 'General',
  initialBranch   = 'Computer Science & Engineering',
}) {
  const [exam,     setExam]     = useState(initialExam);
  const [rank,     setRank]     = useState(initialRank);
  const [category, setCategory] = useState(initialCategory);
  const [branch,   setBranch]   = useState(initialBranch);
  const [recommendations, setRecommendations] = useState(null);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState(null);

  // Auto-predict when pre-filled from hero form
  useEffect(() => {
    if (initialRank && parseInt(initialRank) > 0) {
      handlePredict(initialExam, initialRank, initialCategory, initialBranch);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handlePredict = async (
    e = exam, r = rank, c = category, b = branch
  ) => {
    const parsedRank = parseInt(r);
    if (!parsedRank || parsedRank <= 0) {
      setError('Please enter a valid rank (positive number).');
      return;
    }
    setError(null);
    setLoading(true);
    setRecommendations(null);
    try {
      const profile = {
        entrance_exam:    e,
        rank:             parsedRank,
        category:         c,
        academic_strengths: [],
        interests:        [b],
        career_goals:     [],
        preferred_locations: [],
      };
      const data = await fetchRecommendations(profile);
      setRecommendations(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch recommendations. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="topic-content">
      {/* Input card */}
      <div className="predictor-form-card">
        <h3 className="predictor-form-title">✨ Predict Your Colleges</h3>

        {/* Exam info banner */}
        <div className="exam-info-banner" role="note">
          <span className="exam-info-icon">ℹ️</span>
          <span>
            <strong>JEE Main</strong> rank → NITs, IIITs, GFTIs &nbsp;|&nbsp;
            <strong>JEE Advanced</strong> rank → IITs
          </span>
        </div>

        <div className="predictor-form-row">
          {/* Exam */}
          <div className="predictor-field">
            <label htmlFor="pred-exam" className="predictor-label">Entrance Exam</label>
            <select
              id="pred-exam"
              className="predictor-input predictor-select"
              value={exam}
              onChange={(e) => setExam(e.target.value)}
              aria-label="Select entrance exam"
            >
              {EXAMS.map((ex) => (
                <option key={ex.value} value={ex.value}>{ex.label}</option>
              ))}
            </select>
          </div>

          {/* Rank */}
          <div className="predictor-field">
            <label htmlFor="pred-rank" className="predictor-label">Your Rank</label>
            <input
              id="pred-rank"
              type="number"
              className="predictor-input"
              placeholder="e.g. 2000"
              value={rank}
              onChange={(e) => setRank(e.target.value)}
              min="1"
              aria-label="Enter your rank"
            />
          </div>

          {/* Category */}
          <div className="predictor-field">
            <label htmlFor="pred-category" className="predictor-label">Category</label>
            <select
              id="pred-category"
              className="predictor-input predictor-select"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              aria-label="Select category"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* Branch */}
          <div className="predictor-field predictor-field-wide">
            <label htmlFor="pred-branch" className="predictor-label">Interested Branch</label>
            <select
              id="pred-branch"
              className="predictor-input predictor-select"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              aria-label="Select preferred branch"
            >
              {BRANCHES.map((b) => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          </div>

          <button
            className="predictor-btn"
            onClick={() => handlePredict()}
            disabled={loading}
            aria-label="Predict colleges"
          >
            {loading ? '⏳ Predicting...' : '✨ Predict Colleges'}
          </button>
        </div>

        {error && (
          <div className="predictor-error" role="alert">⚠️ {error}</div>
        )}
      </div>

      {/* Disclaimer */}
      {recommendations && (
        <DisclaimerBanner text={recommendations.disclaimer} />
      )}

      {/* Results */}
      <div className="predictor-results">
        <PreferenceList recommendations={recommendations} loading={loading} />
      </div>
    </div>
  );
}

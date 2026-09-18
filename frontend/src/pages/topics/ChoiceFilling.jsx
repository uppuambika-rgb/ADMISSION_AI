import React, { useState } from 'react';
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

const CHOICE_TIPS = [
  { icon: '🎯', tip: 'Always lock in 5+ Safe choices first — they guarantee you a seat.' },
  { icon: '📊', tip: 'Order choices strictly by preference, not by admission probability.' },
  { icon: '🏛️', tip: 'Do not skip NITs / IIITs in later rounds — cutoffs drop significantly.' },
  { icon: '🔀', tip: 'Consider alternative branches at top institutes over CSE at lower-ranked ones.' },
  { icon: '⚡', tip: 'Always verify cutoffs on the official JoSAA portal before final submission.' },
  { icon: '📅', tip: 'Do not wait until the last hour — JoSAA portals experience heavy traffic.' },
];

export default function ChoiceFilling() {
  const [exam,     setExam]     = useState('JEE Main');
  const [rank,     setRank]     = useState('');
  const [category, setCategory] = useState('General');
  const [branch,   setBranch]   = useState('Computer Science & Engineering');
  const [recommendations, setRecommendations] = useState(null);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState(null);

  const handleGenerate = async () => {
    const parsedRank = parseInt(rank);
    if (!parsedRank || parsedRank <= 0) {
      setError('Please enter a valid rank.');
      return;
    }
    setError(null);
    setLoading(true);
    setRecommendations(null);
    try {
      const profile = {
        entrance_exam:       exam,
        rank:                parsedRank,
        category,
        academic_strengths:  [],
        interests:           [branch],
        career_goals:        [],
        preferred_locations: [],
      };
      const data = await fetchRecommendations(profile);
      setRecommendations(data);
    } catch (err) {
      setError(err.message || 'Failed to generate choice list. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="topic-content">
      {/* Tips */}
      <div className="predictor-form-card">
        <h3 className="predictor-form-title">📋 Choice Filling Tips</h3>
        <div className="choice-tips-grid" role="list">
          {CHOICE_TIPS.map((t) => (
            <div key={t.tip} className="choice-tip-card" role="listitem">
              <span className="choice-tip-icon" aria-hidden="true">{t.icon}</span>
              <p className="choice-tip-text">{t.tip}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Generate list */}
      <div className="predictor-form-card">
        <h3 className="predictor-form-title">✨ Generate Your Preference List</h3>

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
            <label htmlFor="cf-exam" className="predictor-label">Entrance Exam</label>
            <select
              id="cf-exam"
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
            <label htmlFor="cf-rank" className="predictor-label">Your Rank</label>
            <input
              id="cf-rank"
              type="number"
              className="predictor-input"
              placeholder="e.g. 3000"
              value={rank}
              onChange={(e) => setRank(e.target.value)}
              min="1"
              aria-label="Enter your rank"
            />
          </div>

          {/* Category */}
          <div className="predictor-field">
            <label htmlFor="cf-category" className="predictor-label">Category</label>
            <select
              id="cf-category"
              className="predictor-input predictor-select"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              aria-label="Select category"
            >
              {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          {/* Branch */}
          <div className="predictor-field predictor-field-wide">
            <label htmlFor="cf-branch" className="predictor-label">Priority Branch</label>
            <select
              id="cf-branch"
              className="predictor-input predictor-select"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              aria-label="Select preferred branch"
            >
              {BRANCHES.map((b) => <option key={b} value={b}>{b}</option>)}
            </select>
          </div>

          <button
            className="predictor-btn"
            onClick={handleGenerate}
            disabled={loading}
            aria-label="Generate choice list"
          >
            {loading ? '⏳ Generating...' : '📋 Generate List'}
          </button>
        </div>
        {error && <div className="predictor-error" role="alert">⚠️ {error}</div>}
      </div>

      {recommendations && (
        <DisclaimerBanner text={recommendations.disclaimer} />
      )}

      <div className="predictor-results">
        <PreferenceList recommendations={recommendations} loading={loading} />
      </div>
    </div>
  );
}

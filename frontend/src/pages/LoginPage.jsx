import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const { login } = useAuth();
  const navigate  = useNavigate();
  const location  = useLocation();
  const from      = location.state?.from || '/';

  const [email,    setEmail]    = useState('');
  const [password, setPassword] = useState('');
  const [error,    setError]    = useState('');
  const [loading,  setLoading]  = useState(false);
  const [showPwd,  setShowPwd]  = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) { setError('Please fill in all fields.'); return; }
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      {/* Left decorative panel */}
      <div className="auth-panel-left" aria-hidden="true">
        <div className="auth-panel-grid"></div>
        <div className="auth-panel-blob"></div>
        <div className="auth-panel-content">
          <div className="auth-panel-logo">🎓</div>
          <h2 className="auth-panel-title">AdmissionAI</h2>
          <p className="auth-panel-subtitle">Your AI-powered college admission counsellor</p>
          <ul className="auth-panel-features">
            <li>📊 Rank &amp; eligibility analysis</li>
            <li>🎓 Personalised college recommendations</li>
            <li>🤖 AI counsellor chat, 24 × 7</li>
            <li>📋 Smart choice-filling strategy</li>
          </ul>
        </div>
      </div>

      {/* Right form panel */}
      <div className="auth-panel-right">
        <div className="auth-form-card">
          {/* Header */}
          <div className="auth-form-header">
            <div className="auth-form-icon">👤</div>
            <h1 className="auth-form-title">Welcome back</h1>
            <p className="auth-form-subtitle">Sign in to your AdmissionAI account</p>
          </div>

          {/* Error */}
          {error && (
            <div className="auth-error" role="alert">
              <span>⚠️</span> {error}
            </div>
          )}

          {/* Form */}
          <form className="auth-form" onSubmit={handleSubmit} noValidate>
            <div className="auth-field">
              <label htmlFor="login-email" className="auth-label">Email address</label>
              <input
                id="login-email"
                type="email"
                className="auth-input"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>

            <div className="auth-field">
              <div className="auth-label-row">
                <label htmlFor="login-password" className="auth-label">Password</label>
              </div>
              <div className="auth-input-wrap">
                <input
                  id="login-password"
                  type={showPwd ? 'text' : 'password'}
                  className="auth-input"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  className="auth-toggle-pwd"
                  onClick={() => setShowPwd((p) => !p)}
                  aria-label={showPwd ? 'Hide password' : 'Show password'}
                >
                  {showPwd ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="auth-submit-btn"
              disabled={loading}
            >
              {loading ? (
                <span className="auth-spinner" aria-hidden="true"></span>
              ) : null}
              {loading ? 'Signing in…' : 'Sign In →'}
            </button>
          </form>

          {/* Divider */}
          <div className="auth-divider"><span>New to AdmissionAI?</span></div>

          {/* Switch to register */}
          <Link to="/register" className="auth-switch-btn">
            Create a free account
          </Link>

          <p className="auth-terms">
            By signing in you agree to our{' '}
            <span className="auth-link">Terms of Service</span> and{' '}
            <span className="auth-link">Privacy Policy</span>.
          </p>
        </div>
      </div>
    </div>
  );
}

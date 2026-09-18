import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate     = useNavigate();

  const [name,     setName]     = useState('');
  const [email,    setEmail]    = useState('');
  const [password, setPassword] = useState('');
  const [confirm,  setConfirm]  = useState('');
  const [error,    setError]    = useState('');
  const [loading,  setLoading]  = useState(false);
  const [showPwd,  setShowPwd]  = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !email || !password || !confirm) {
      setError('Please fill in all fields.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await register(name, email, password);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const strength = (() => {
    if (!password) return 0;
    let s = 0;
    if (password.length >= 6)  s++;
    if (password.length >= 10) s++;
    if (/[A-Z]/.test(password)) s++;
    if (/[0-9]/.test(password)) s++;
    if (/[^A-Za-z0-9]/.test(password)) s++;
    return s;
  })();

  const strengthLabel = ['', 'Weak', 'Fair', 'Good', 'Strong', 'Very strong'][strength];
  const strengthColor = ['', '#ef4444', '#f97316', '#eab308', '#22c55e', '#16a34a'][strength];

  return (
    <div className="auth-page">
      {/* Left decorative panel */}
      <div className="auth-panel-left" aria-hidden="true">
        <div className="auth-panel-grid"></div>
        <div className="auth-panel-blob"></div>
        <div className="auth-panel-content">
          <div className="auth-panel-logo">🎓</div>
          <h2 className="auth-panel-title">Join AdmissionAI</h2>
          <p className="auth-panel-subtitle">Create your free account and start your smarter admission journey today.</p>
          <ul className="auth-panel-features">
            <li>✅ 100% free to use</li>
            <li>🔒 Your data stays private</li>
            <li>⚡ Instant AI recommendations</li>
            <li>📱 Works on all devices</li>
          </ul>
        </div>
      </div>

      {/* Right form panel */}
      <div className="auth-panel-right">
        <div className="auth-form-card">
          {/* Header */}
          <div className="auth-form-header">
            <div className="auth-form-icon">🚀</div>
            <h1 className="auth-form-title">Create your account</h1>
            <p className="auth-form-subtitle">Free forever • No credit card required</p>
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
              <label htmlFor="reg-name" className="auth-label">Full name</label>
              <input
                id="reg-name"
                type="text"
                className="auth-input"
                placeholder="Your full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoComplete="name"
                required
              />
            </div>

            <div className="auth-field">
              <label htmlFor="reg-email" className="auth-label">Email address</label>
              <input
                id="reg-email"
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
              <label htmlFor="reg-password" className="auth-label">Password</label>
              <div className="auth-input-wrap">
                <input
                  id="reg-password"
                  type={showPwd ? 'text' : 'password'}
                  className="auth-input"
                  placeholder="Min. 6 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="new-password"
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
              {/* Strength bar */}
              {password && (
                <div className="auth-strength">
                  <div className="auth-strength-bars">
                    {[1,2,3,4,5].map((i) => (
                      <div
                        key={i}
                        className="auth-strength-bar"
                        style={{ background: i <= strength ? strengthColor : '#e2e8f0' }}
                      />
                    ))}
                  </div>
                  <span className="auth-strength-label" style={{ color: strengthColor }}>
                    {strengthLabel}
                  </span>
                </div>
              )}
            </div>

            <div className="auth-field">
              <label htmlFor="reg-confirm" className="auth-label">Confirm password</label>
              <input
                id="reg-confirm"
                type={showPwd ? 'text' : 'password'}
                className={`auth-input ${confirm && confirm !== password ? 'auth-input-error' : ''}`}
                placeholder="Re-enter your password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                autoComplete="new-password"
                required
              />
              {confirm && confirm !== password && (
                <p className="auth-field-error">Passwords do not match</p>
              )}
            </div>

            <button
              type="submit"
              className="auth-submit-btn"
              disabled={loading}
            >
              {loading ? <span className="auth-spinner" aria-hidden="true"></span> : null}
              {loading ? 'Creating account…' : 'Create Account →'}
            </button>
          </form>

          <div className="auth-divider"><span>Already have an account?</span></div>

          <Link to="/login" className="auth-switch-btn">
            Sign in instead
          </Link>

          <p className="auth-terms">
            By creating an account you agree to our{' '}
            <span className="auth-link">Terms of Service</span> and{' '}
            <span className="auth-link">Privacy Policy</span>.
          </p>
        </div>
      </div>
    </div>
  );
}

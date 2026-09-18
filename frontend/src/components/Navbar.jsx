import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const [menuOpen,    setMenuOpen]    = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate  = useNavigate();
  const location  = useLocation();

  const navLinks = [
    { label: 'Home',          href: '/' },
    { label: 'About',         href: '/#about' },
    { label: 'Colleges',      href: '/topic/college-info' },
    { label: 'AI Counsellor', href: '/topic/ai-counsellor' },
    { label: 'Help',          href: '/#features' },
  ];

  const handleNavClick = (e, href) => {
    if (href.startsWith('/#')) {
      e.preventDefault();
      const id = href.replace('/#', '');
      if (location.pathname !== '/') {
        navigate('/');
        setTimeout(() => {
          document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      } else {
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
      }
      setMenuOpen(false);
    }
  };

  const handleLogout = async () => {
    setProfileOpen(false);
    await logout();
    navigate('/');
  };

  const initials = user?.name
    ? user.name.split(' ').map((w) => w[0]).join('').toUpperCase().slice(0, 2)
    : '';

  return (
    <nav className="site-navbar" role="navigation" aria-label="Main navigation">
      <div className="navbar-inner">
        {/* Brand */}
        <Link to="/" className="nav-brand" aria-label="AdmissionAI Home">
          <div className="nav-brand-icon" aria-hidden="true">🎓</div>
          <span className="nav-brand-name">AdmissionAI</span>
        </Link>

        {/* Desktop links */}
        <ul className="nav-links" role="list">
          {navLinks.map((link) => (
            <li key={link.label}>
              <Link
                to={link.href.startsWith('/#') ? location.pathname : link.href}
                className={`nav-link ${location.pathname === link.href ? 'nav-link-active' : ''}`}
                onClick={(e) => handleNavClick(e, link.href)}
              >
                {link.label}
              </Link>
            </li>
          ))}
        </ul>

        {/* Right side */}
        <div className="nav-right">
          <span className="nav-online-badge" aria-label="System status: online">
            <span className="nav-online-dot" aria-hidden="true"></span>
            System Online
          </span>

          {user ? (
            /* ── Logged-in user avatar + dropdown ── */
            <div className="nav-user-wrap">
              <button
                className="nav-avatar-btn"
                onClick={() => setProfileOpen((o) => !o)}
                aria-label="User menu"
                aria-expanded={profileOpen}
              >
                <span className="nav-avatar-initials">{initials}</span>
              </button>

              {profileOpen && (
                <div className="nav-dropdown" role="menu">
                  <div className="nav-dropdown-header">
                    <p className="nav-dropdown-name">{user.name}</p>
                    <p className="nav-dropdown-email">{user.email}</p>
                  </div>
                  <hr className="nav-dropdown-divider" />
                  <button
                    className="nav-dropdown-item"
                    role="menuitem"
                    onClick={handleLogout}
                  >
                    🚪 Sign out
                  </button>
                </div>
              )}
            </div>
          ) : (
            /* ── Guest: Login / Register buttons ── */
            <div className="nav-auth-btns">
              <Link to="/login"    className="nav-login-btn">Sign In</Link>
              <Link to="/register" className="nav-register-btn">Get Started</Link>
            </div>
          )}

          {/* Mobile hamburger */}
          <button
            className="nav-hamburger"
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((o) => !o)}
          >
            <span className="hamburger-bar"></span>
            <span className="hamburger-bar"></span>
            <span className="hamburger-bar"></span>
          </button>
        </div>
      </div>

      {/* Mobile drawer */}
      {menuOpen && (
        <div className="nav-mobile-drawer" role="menu">
          {navLinks.map((link) => (
            <Link
              key={link.label}
              to={link.href.startsWith('/#') ? location.pathname : link.href}
              className="nav-mobile-link"
              role="menuitem"
              onClick={(e) => { handleNavClick(e, link.href); setMenuOpen(false); }}
            >
              {link.label}
            </Link>
          ))}
          <hr style={{ border: 'none', borderTop: '1px solid #d1e3f8', margin: '8px 0' }} />
          {user ? (
            <button
              className="nav-mobile-link"
              style={{ textAlign: 'left', background: 'none', border: 'none', cursor: 'pointer', color: '#ef4444' }}
              onClick={handleLogout}
            >
              🚪 Sign out ({user.name})
            </button>
          ) : (
            <>
              <Link to="/login"    className="nav-mobile-link" onClick={() => setMenuOpen(false)}>Sign In</Link>
              <Link to="/register" className="nav-mobile-link" onClick={() => setMenuOpen(false)}>Create Account</Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
}

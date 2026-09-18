import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { IMAGES } from '../assets/images';

/* ─────────────────────────────────────────────────────────────────
   WORKFLOW — represents the ACTUAL system pipeline exactly
───────────────────────────────────────────────────────────────── */
const WORKFLOW_STEPS = [
  { id: 'student-in',  icon: '🎓', label: 'Student',                    sub: 'You start here',                                          type: 'endpoint' },
  { id: 'input',       icon: '📝', label: 'User Input',                  sub: 'Rank · Category · Branch · Goals',                        type: 'input'    },
  { id: 'agent',       icon: '🤖', label: 'AdmissionAI Agent',           sub: 'LLM-powered counsellor processes your query in real time', type: 'agent'    },
  { id: 'rank',        icon: '📊', label: 'Rank & Eligibility Analysis',  sub: 'Historical JoSAA/CSAB cutoff benchmarking across rounds',  type: 'process'  },
  { id: 'match',       icon: '🔍', label: 'College & Branch Matching',    sub: 'Programme-level filtering by category & branch interest',  type: 'process'  },
  { id: 'engine',      icon: '⚙️', label: 'Recommendation Engine',        sub: 'Composite scoring: placement · curriculum · location',    type: 'process'  },
  { id: 'tiers',       icon: '🏅', label: 'Aspirational | Likely | Safe', sub: 'Deterministic tier classification with AI rationale',     type: 'tiers'    },
  { id: 'choice',      icon: '📋', label: 'Choice Filling Strategy',      sub: 'Optimised preference list ready for JoSAA / CSAB',        type: 'process'  },
  { id: 'student-out', icon: '🏆', label: 'Student Gets Admitted',        sub: 'Informed decision. Better outcome.',                      type: 'endpoint' },
];

const TIER_COLORS = {
  Aspirational: { bg: '#faf5ff', border: '#c4b5fd', text: '#6b21a8' },
  Likely:       { bg: '#eff6ff', border: '#93c5fd', text: '#1e40af' },
  Safe:         { bg: '#ecfdf5', border: '#6ee7b7', text: '#065f46' },
};

const TECH_CARDS = [
  { icon: '🧠', title: 'LLM Reasoning',         desc: 'Natural language understanding extracts rank, category and goals from free-form chat — no rigid forms needed.' },
  { icon: '📐', title: 'Deterministic Cutoffs',  desc: 'Rule-based engine applies historical JoSAA/CSAB round-wise cutoff data — zero hallucination, pure facts.' },
  { icon: '🎯', title: 'Composite Scoring',      desc: 'Placement stats, curriculum alignment and location preference combined into one transparent strategy score.' },
  { icon: '🔄', title: 'Real-time Feedback',     desc: 'Every follow-up question refines the student profile and instantly updates all recommendations.' },
];

const FEATURES = [
  { id: 'rank-analysis',   icon: '📊', title: 'Rank Analysis',        desc: 'Know your chances in top colleges based on your rank and category.',    color: 'card-blue'   },
  { id: 'college-predictor',icon:'🎓', title: 'College Predictor',     desc: 'Get personalized college recommendations tailored to your profile.',    color: 'card-purple' },
  { id: 'college-info',    icon: '🏛️', title: 'College Information',   desc: 'Detailed info about colleges, courses, cutoffs and campus life.',       color: 'card-indigo' },
  { id: 'branch-explorer', icon: '🔀', title: 'Branch Explorer',       desc: 'Explore branches, scope, curriculum and career options.',               color: 'card-teal'   },
  { id: 'fees',            icon: '💰', title: 'Fees & Scholarships',   desc: 'Compare fees, discover scholarships and financial aid options.',         color: 'card-green'  },
  { id: 'hostel',          icon: '🏠', title: 'Hostel & Facilities',   desc: 'Check hostel, mess, labs, transport and campus life details.',           color: 'card-orange' },
  { id: 'placements',      icon: '💼', title: 'Placements',            desc: 'View placement stats, median CTCs and top recruiters.',                 color: 'card-rose'   },
  { id: 'choice-filling',  icon: '📋', title: 'Choice Filling',        desc: 'Get expert help in creating your optimised preference list.',           color: 'card-amber'  },
  { id: 'ai-counsellor',   icon: '🤖', title: 'AI Counsellor',         desc: 'Ask anything — get instant, personalised admission guidance.',          color: 'card-violet' },
];

const CATEGORIES = ['General','OBC','SC','ST','EWS','General-PwD','OBC-PwD','SC-PwD','ST-PwD'];
const BRANCHES   = [
  'Computer Science & Engineering','Electronics & Communication Engineering',
  'Electrical Engineering','Mechanical Engineering','Civil Engineering',
  'Chemical Engineering','Information Technology','Data Science & AI',
  'Biotechnology','Aerospace Engineering',
];
const EXAMS = [
  { value: 'JEE Main',     label: 'JEE Main (NITs / IIITs / GFTIs)' },
  { value: 'JEE Advanced', label: 'JEE Advanced (IITs)' },
  { value: 'AP EAPCET',    label: 'AP EAPCET (Andhra Pradesh)' },
];

const FOOTER_STATS = [
  { icon: '✅', label: 'Trusted Information', sub: 'From official sources' },
  { icon: '🤖', label: 'AI Powered',          sub: 'Smart recommendations'  },
  { icon: '🏆', label: 'Your Success',        sub: 'Our Priority'            },
];

/* ─── Agent Workflow Section ─────────────────────────────────── */
function AgentWorkflow() {
  return (
    <section className="wf-section" id="how-it-works" aria-labelledby="wf-heading">
      <div className="wf-grid-bg" aria-hidden="true"></div>
      <div className="wf-blob"    aria-hidden="true"></div>
      <div className="section-container" style={{ position: 'relative', zIndex: 1 }}>

        {/* Header */}
        <div className="section-header">
          <span className="section-eyebrow">⚡ Agentic AI Pipeline</span>
          <h2 className="section-title" id="wf-heading" style={{ color: '#fff' }}>
            How AdmissionAI Agent Works
          </h2>
          <p className="section-subtitle" style={{ color: 'rgba(255,255,255,0.6)' }}>
            A single intelligent agent orchestrates your entire admission journey —
            from rank analysis to finalised college choices.
          </p>
        </div>

        {/* Two-column layout: pipeline left, tech cards right */}
        <div className="wf-body">

          {/* LEFT — vertical pipeline */}
          <ol className="wf-pipeline" aria-label="Admission AI workflow steps">
            {WORKFLOW_STEPS.map((step, i) => (
              <li key={step.id} className={`wf-step wf-step--${step.type}`}>

                {/* Icon circle */}
                <div className="wf-step-icon" aria-hidden="true">
                  {step.type === 'agent' && (
                    <>
                      <span className="wf-ring wf-ring-1" aria-hidden="true"></span>
                      <span className="wf-ring wf-ring-2" aria-hidden="true"></span>
                    </>
                  )}
                  <span className="wf-step-emoji">{step.icon}</span>
                </div>

                {/* Connector line */}
                {i < WORKFLOW_STEPS.length - 1 && (
                  <span className="wf-connector" aria-hidden="true">
                    <span className="wf-connector-line"></span>
                    <span className="wf-connector-arrow">▼</span>
                  </span>
                )}

                {/* Body card */}
                <div className="wf-step-card">
                  <p className="wf-step-label">{step.label}</p>
                  <p className="wf-step-sub">{step.sub}</p>
                  {step.type === 'tiers' && (
                    <div className="wf-tier-chips" role="list" aria-label="Tier levels">
                      {Object.entries(TIER_COLORS).map(([tier, c]) => (
                        <span
                          key={tier}
                          className="wf-tier-chip"
                          role="listitem"
                          style={{ background: c.bg, borderColor: c.border, color: c.text }}
                        >
                          {tier}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ol>

          {/* RIGHT — sticky tech cards */}
          <div className="wf-side" aria-label="Technology highlights">
            <p className="wf-side-title">Under the hood</p>
            {TECH_CARDS.map((t) => (
              <div key={t.title} className="wf-tech-card">
                <span className="wf-tech-icon" aria-hidden="true">{t.icon}</span>
                <div>
                  <p className="wf-tech-title">{t.title}</p>
                  <p className="wf-tech-desc">{t.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

/* ─── Home Page ──────────────────────────────────────────────── */
export default function HomePage() {
  const navigate = useNavigate();
  const [exam,     setExam]     = useState('JEE Main');
  const [rank,     setRank]     = useState('');
  const [category, setCategory] = useState('General');
  const [branch,   setBranch]   = useState('Computer Science & Engineering');

  const handleGetStarted = () => {
    const params = new URLSearchParams({ exam, rank, category, branch });
    navigate(`/topic/college-predictor?${params.toString()}`);
  };

  return (
    <div className="home-page">

      {/* ══════════════ HERO ══════════════════════════════════════ */}
      <section
        className="hero-section"
        aria-label="Hero section"
      >
        {/* Overlay layers */}
        <div className="hero-overlay" aria-hidden="true"></div>

        {/* Decorative neural network dots */}
        <div className="hero-dots" aria-hidden="true">
          {[...Array(6)].map((_, i) => <span key={i} className="hero-dot"></span>)}
        </div>

        {/* Glowing blobs */}
        <div className="hero-glow-1" aria-hidden="true"></div>
        <div className="hero-glow-2" aria-hidden="true"></div>

        <div className="hero-inner">
          {/* ── Left text column ── */}
          <div className="hero-text-col">
            <div className="hero-badge">
              <span className="hero-badge-dot" aria-hidden="true"></span>
              AI-Powered Admission Guidance
            </div>

            <p className="hero-eyebrow">AI-POWERED ADMISSION COUNSELLING</p>

            <h1 className="hero-heading">
              Find Your Best College
              <span className="hero-heading-accent">with AI Guidance</span>
            </h1>

            <p className="hero-subtext">
              Get personalised college recommendations, rank analysis,
              fee details, hostel information, placements and more — all in one place.
            </p>

            {/* Search form — all existing state + handler preserved */}
            <div className="hero-form" role="search" aria-label="College search form">
              <div className="hero-input-group">
                <label htmlFor="hero-exam" className="hero-input-label">Entrance Exam</label>
                <select
                  id="hero-exam"
                  className="hero-input hero-select"
                  value={exam}
                  onChange={(e) => setExam(e.target.value)}
                  aria-label="Select entrance exam"
                >
                  {EXAMS.map((e) => (
                    <option key={e.value} value={e.value}>{e.label}</option>
                  ))}
                </select>
              </div>

              <div className="hero-input-group">
                <label htmlFor="hero-rank" className="hero-input-label">Your Rank</label>
                <input
                  id="hero-rank"
                  type="number"
                  className="hero-input"
                  placeholder="e.g. 2000"
                  value={rank}
                  onChange={(e) => setRank(e.target.value)}
                  min="1"
                  aria-label="Enter your rank"
                />
              </div>

              <div className="hero-input-group">
                <label htmlFor="hero-category" className="hero-input-label">Category</label>
                <select
                  id="hero-category"
                  className="hero-input hero-select"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  aria-label="Select category"
                >
                  {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              <div className="hero-input-group">
                <label htmlFor="hero-branch" className="hero-input-label">Interested Branch</label>
                <select
                  id="hero-branch"
                  className="hero-input hero-select hero-select-wide"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  aria-label="Select preferred branch"
                >
                  {BRANCHES.map((b) => <option key={b} value={b}>{b}</option>)}
                </select>
              </div>

              <button
                className="hero-cta-btn"
                onClick={handleGetStarted}
                aria-label="Get started with college prediction"
              >
                Get Started →
              </button>
            </div>

            {/* Trust stats */}
            <div className="hero-trust-row" aria-label="Quick statistics">
              <div className="hero-trust-item">
                <span className="hero-trust-num">500+</span>
                <span className="hero-trust-label">Colleges</span>
              </div>
              <div className="hero-trust-divider" aria-hidden="true"></div>
              <div className="hero-trust-item">
                <span className="hero-trust-num">50+</span>
                <span className="hero-trust-label">Branches</span>
              </div>
              <div className="hero-trust-divider" aria-hidden="true"></div>
              <div className="hero-trust-item">
                <span className="hero-trust-num">AI</span>
                <span className="hero-trust-label">Powered</span>
              </div>
            </div>
          </div>

          {/* ── Right AI orb visual ── */}
          <div className="hero-ai-visual" aria-hidden="true">
            <div className="hero-ai-orb">
              <span className="hero-ai-orb-inner">🤖</span>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════ FEATURES ══════════════════════════════════ */}
      <section className="features-section" id="features" aria-labelledby="features-heading">
        <div className="section-container">
          <div className="section-header">
            <span className="section-eyebrow">🎓 What We Offer</span>
            <h2 className="section-title" id="features-heading">Explore Our Features</h2>
            <p className="section-subtitle">Everything you need for a smarter admission decision</p>
          </div>

          <div className="features-grid" role="list">
            {FEATURES.map((feat) => (
              <button
                key={feat.id}
                className={`feature-card ${feat.color}`}
                role="listitem"
                onClick={() => navigate(`/topic/${feat.id}`)}
                aria-label={`Explore ${feat.title}`}
              >
                <div className="feature-card-icon" aria-hidden="true">{feat.icon}</div>
                <h3 className="feature-card-title">{feat.title}</h3>
                <p className="feature-card-desc">{feat.desc}</p>
                <span className="feature-card-arrow" aria-hidden="true">→</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════ ABOUT ════════════════════════════════════ */}
      <section id="about" className="about-section" aria-labelledby="about-heading">
        <div className="section-container">
          <div className="section-header">
            <span className="section-eyebrow">🎓 About AdmissionAI</span>
            <h2 className="section-title" id="about-heading">Built for Indian Engineering Students</h2>
            <p className="section-subtitle">
              AdmissionAI is an agentic AI counselling platform that helps JEE students
              make smarter admission decisions using historical cutoff data, AI reasoning and placement insights.
            </p>
          </div>
          <div className="about-grid">
            <div className="about-card">
              <span className="about-card-icon">🎯</span>
              <h3 className="about-card-title">Our Mission</h3>
              <p className="about-card-desc">
                To give every student — regardless of background or access to coaching — a data-driven,
                personalised admission strategy that maximises their chances of getting into the right college.
              </p>
            </div>
            <div className="about-card">
              <span className="about-card-icon">🤖</span>
              <h3 className="about-card-title">Agentic AI</h3>
              <p className="about-card-desc">
                Our AI agent combines a large language model with a deterministic cutoff engine.
                It reasons about your rank, category and interests to produce explainable, accurate recommendations.
              </p>
            </div>
            <div className="about-card">
              <span className="about-card-icon">📊</span>
              <h3 className="about-card-title">Data-Driven</h3>
              <p className="about-card-desc">
                Powered by historical JoSAA and CSAB round-wise cutoff data.
                Every recommendation comes with a likelihood range, tier classification and AI rationale.
              </p>
            </div>
            <div className="about-card">
              <span className="about-card-icon">🏆</span>
              <h3 className="about-card-title">Student First</h3>
              <p className="about-card-desc">
                Covers 500+ programmes across NITs, IIITs, GFTIs and top private colleges
                with placement stats, fee details, hostel info and branch career guides.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════ AGENT WORKFLOW ════════════════════════════ */}
      <AgentWorkflow />

      {/* ══════════════ AI COUNSELLOR BANNER ══════════════════════ */}
      <section
        className="ai-banner-section"
        style={{ backgroundImage: `url(${IMAGES.aiBanner})` }}
        aria-label="AI Counsellor promotional banner"
      >
        <div className="ai-banner-overlay" aria-hidden="true"></div>
        <div className="ai-banner-content">
          <div className="ai-banner-badge">🤖 Powered by AI</div>
          <h2 className="ai-banner-heading">Need Personalised Guidance?</h2>
          <p className="ai-banner-subtext">
            Chat with our AI Counsellor for instant answers<br />
            to all your admission queries.
          </p>
          <button
            className="ai-banner-btn"
            onClick={() => navigate('/topic/ai-counsellor')}
            aria-label="Start chatting with AI Counsellor"
          >
            Start Chatting →
          </button>
        </div>
      </section>

      {/* ══════════════ FOOTER ════════════════════════════════════ */}
      <footer className="site-footer" role="contentinfo">
        <div className="footer-inner">
          <div className="footer-stats" aria-label="Key platform features">
            {FOOTER_STATS.map((s) => (
              <div key={s.label} className="footer-stat-item">
                <span className="footer-stat-icon" aria-hidden="true">{s.icon}</span>
                <div>
                  <div className="footer-stat-label">{s.label}</div>
                  <div className="footer-stat-sub">{s.sub}</div>
                </div>
              </div>
            ))}
          </div>
          <div className="footer-brand-row">
            <div className="footer-brand">
              <span className="footer-brand-icon" aria-hidden="true">🎓</span>
              <div>
                <div className="footer-brand-name">AdmissionAI</div>
                <div className="footer-brand-tagline">Better Guidance • Brighter Future</div>
              </div>
            </div>
            <p className="footer-copy">© 2026 AdmissionAI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

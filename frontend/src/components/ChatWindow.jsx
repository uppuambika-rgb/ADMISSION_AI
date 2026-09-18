import React, { useState, useRef, useEffect } from 'react';

const QUICK_STARTERS = [
  "My rank is 4800 (General). I love AI, Machine Learning, and Software Engineering.",
  "Can I get into an NIT?",
  "Which are my safest options?",
  "Which programme is best for AI?",
  "Which has better placements?",
  "What are the fees?",
  "Is hostel available?",
  "Why did you rank this programme first?",
  "Can I get CSE?",
];

function RenderStructuredTable({ data }) {
  if (!data || !data.rows || data.rows.length === 0) return null;

  const { title, columns, rows, disclaimer, mismatch_warning } = data;

  const renderCell = (colName, val) => {
    if (val === undefined || val === null || val === '') return 'Not available';
    
    // Tier badge formatting
    if (colName.toLowerCase() === 'tier') {
      const tierClass = 
        val === 'Safe' ? 'badge-safe' :
        val === 'Likely' ? 'badge-likely' :
        val === 'Aspirational' ? 'badge-asp' : 'badge-reach';
      return <span className={`table-badge ${tierClass}`}>{val}</span>;
    }

    // Likelihood range badge
    if (colName.toLowerCase() === 'likelihood range') {
      return <span style={{ fontWeight: 700, color: '#2563eb' }}>{val}</span>;
    }

    // Rank difference highlighting
    if (colName.toLowerCase() === 'rank difference') {
      const isPositive = String(val).startsWith('+');
      return (
        <span style={{ fontWeight: 600, color: isPositive ? '#059669' : '#dc2626' }}>
          {val}
        </span>
      );
    }

    return String(val);
  };

  return (
    <div className="chat-structured-card">
      <div className="structured-card-header">
        <span className="structured-card-icon">&#128202;</span>
        <h4 className="structured-card-title">{title}</h4>
      </div>

      {mismatch_warning && (
        <div className="chat-mismatch-banner">
          <span className="mismatch-icon">&#9888;</span>
          <span>{mismatch_warning}</span>
        </div>
      )}

      <div className="chat-table-wrapper">
        <table className="chat-table">
          <thead>
            <tr>
              {columns.map((col, idx) => (
                <th key={idx}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, rIdx) => (
              <tr key={rIdx}>
                {columns.map((col, cIdx) => (
                  <td key={cIdx}>{renderCell(col, row[col])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {disclaimer && (
        <div className="structured-card-footer">
          <span>* {disclaimer}</span>
        </div>
      )}
    </div>
  );
}

export default function ChatWindow({
  messages,
  currentProfile,
  onSendMessage,
  loading,
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = (e) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleQuickStarter = (text) => {
    onSendMessage(text);
  };

  return (
    <div className="chat-panel">
      {/* Vignan's Logo */}
      <div className="chat-logo-container">
        <img 
          src="/vignans-logo.svg" 
          alt="Vignan's Foundation for Science, Technology & Research" 
          className="chat-logo"
        />
      </div>

      <div className="chat-header">
        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>
          Counsellor Dialogue
        </h3>
        <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          Ask any follow-up: NIT/IIT chances, fees, hostels, placements, AI fit, or specific branches.
        </p>

        {/* Live Profile Chips */}
        <div className="profile-chips">
          <span className="profile-chip">
            Rank: <strong>{currentProfile?.rank ? `#${currentProfile.rank.toLocaleString()}` : 'Not set'}</strong>
          </span>
          <span className="profile-chip">
            Category: <strong>{currentProfile?.category || 'General'}</strong>
          </span>
          {currentProfile?.interests?.length > 0 && (
            <span className="profile-chip">
              Interests: <strong>{currentProfile.interests.join(', ')}</strong>
            </span>
          )}
          {currentProfile?.career_goals?.length > 0 && (
            <span className="profile-chip">
              Goal: <strong>{currentProfile.career_goals.join(', ')}</strong>
            </span>
          )}
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-bubble-container ${msg.role}`}>
            <div className="chat-bubble">
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
              {msg.structured_data && (
                <RenderStructuredTable data={msg.structured_data} />
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="chat-bubble-container assistant">
            <div className="chat-bubble" style={{ color: 'var(--text-muted)' }}>
              <em>AI Counsellor is evaluating cutoffs & factual data...</em>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Starter Pills for instant testing */}
      <div className="quick-prompts">
        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', alignSelf: 'center', marginRight: '4px' }}>
          Ask:
        </span>
        {QUICK_STARTERS.map((text, i) => (
          <button
            key={i}
            className="quick-btn"
            onClick={() => handleQuickStarter(text)}
            disabled={loading}
          >
            {text}
          </button>
        ))}
      </div>

      <form className="chat-input-box" onSubmit={handleSend}>
        <input
          type="text"
          className="chat-input"
          placeholder="Ask a question (e.g. Can I get an NIT? What are the fees? Which is best for AI?)"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="send-btn" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

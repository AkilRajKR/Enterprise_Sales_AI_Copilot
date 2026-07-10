import React, { useState } from 'react';
import { Search, Send, Loader, Plus, GitBranch, X, AlertTriangle, ChevronRight } from 'lucide-react';

interface UserPanelProps {
  input: string;
  onInputChange: (v: string) => void;
  onSubmit: () => void;
  onNewQuery: (initialText?: string) => void;
  onFollowUp: () => void;
  onClear: () => void;
  isLoading: boolean;
  queryMode: 'new' | 'followup';
  activeQuery: string;
  hasResult: boolean;
}

const PII_KEYWORDS = [
  'customer name', 'client name', 'full name', 'first name', 'last name',
  'date of birth', 'dob', 'birthdate', 'salary', 'income', 'earnings',
  'home address', 'phone number', 'email address', 'contact detail', 'contact info',
  'ssn', 'social security', 'passport', 'national id', 'driver license',
  'credit card', 'bank account', 'account number',
];

function detectPII(text: string): boolean {
  const lower = text.toLowerCase();
  return PII_KEYWORDS.some(kw => lower.includes(kw));
}

function getRelevantQueries(activeQuery: string): string[] {
  if (!activeQuery) {
    return [
      'Which brand has the most customers?',
      'Which dealer sold the most vehicles?',
      'How many total vehicles are in the database?',
      'Which model has the highest sales volume?',
      'Show the top 5 manufacturing plants by output.',
      'What are the most popular car options?',
    ];
  }

  const query = activeQuery.toLowerCase();
  const suggestions: string[] = [];

  if (query.includes('brand') || query.includes('make') || query.includes('audi') || query.includes('bmw') || query.includes('toyota') || query.includes('ford')) {
    suggestions.push(
      'What are the top-selling models for the most popular brand?',
      'Which dealers sell the highest volume of that brand?',
      'What is the total customer count for each brand?',
      'Compare the sales volume of the top 3 brands.'
    );
  } else if (query.includes('dealer') || query.includes('store') || query.includes('shop') || query.includes('sales')) {
    suggestions.push(
      'Which specific vehicle models are sold the most at the top dealer?',
      'What are the top 5 dealers by total revenue?',
      'List the brands available at the top-performing dealer.',
      'Show dealers that have sold more than 50 vehicles.'
    );
  } else if (query.includes('plant') || query.includes('manufactur') || query.includes('factor') || query.includes('built') || query.includes('produce')) {
    suggestions.push(
      'Which models are manufactured at the top plant?',
      'What is the total count of parts used in manufacturing?',
      'Show the monthly manufacturing output per plant.',
      'Compare manufactured counts vs sold counts for this year.'
    );
  } else if (query.includes('model') || query.includes('car') || query.includes('vehicle')) {
    suggestions.push(
      'Which brand produced the most popular model?',
      'What are the most popular options selected for that model?',
      'Which dealer has sold the most of that model?',
      'What is the average price or option cost for that vehicle?'
    );
  } else if (query.includes('option') || query.includes('part') || query.includes('color') || query.includes('wheel') || query.includes('engine')) {
    suggestions.push(
      'Which option package is selected the most?',
      'Show the top 5 most expensive car parts in inventory.',
      'Which models are configured with custom options?',
      'Find the total cost of parts for each manufactured brand.'
    );
  } else {
    suggestions.push(
      'Show the top 5 manufacturing plants by output.',
      'Which dealer sold the most vehicles?',
      'What are the most popular car options?',
      'Which brand has the most customers?'
    );
  }

  return Array.from(new Set(suggestions)).slice(0, 5);
}

const UserPanel: React.FC<UserPanelProps> = ({
  input, onInputChange, onSubmit, onNewQuery, onFollowUp, onClear,
  isLoading, queryMode, activeQuery, hasResult,
}) => {
  const [showPIIWarning, setShowPIIWarning] = useState(false);
  const [PIIConfirmed, setPIIConfirmed] = useState(false);

  const isPII = detectPII(input);

  const handleInputChange = (v: string) => {
    onInputChange(v);
    if (!detectPII(v)) { setShowPIIWarning(false); setPIIConfirmed(false); }
  };

  const handleSend = () => {
    if (!input.trim() || isLoading) return;
    if (isPII && !PIIConfirmed) { setShowPIIWarning(true); return; }
    setShowPIIWarning(false); setPIIConfirmed(false);
    onSubmit();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const handleConfirmPII = () => { setPIIConfirmed(true); setShowPIIWarning(false); };

  const handleQuickQuery = (q: string) => { onNewQuery(q); };

  return (
    <div style={{ width: 288, background: 'var(--bg-panel)', borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column', flexShrink: 0, overflowY: 'auto' }}>

      {/* User Identity */}
      <div style={{ padding: '16px 14px', borderBottom: '1px solid var(--border)' }}>
        <div className="panel-header" style={{ padding: '0 0 12px 0', borderBottom: 'none', background: 'transparent', marginBottom: 12 }}>
          <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
            User Identity
          </span>
          <span className="badge badge-cyan" style={{ marginLeft: 'auto', fontSize: 10 }}>Analyst</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div>
            <label style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 600, display: 'block', marginBottom: 5, letterSpacing: '0.5px', textTransform: 'uppercase' }}>Email</label>
            <input
              className="dark-input"
              defaultValue="analyst@kinetix.com"
              style={{ fontSize: 12 }}
            />
          </div>
          <div>
            <label style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 600, display: 'block', marginBottom: 5, letterSpacing: '0.5px', textTransform: 'uppercase' }}>Role</label>
            <select className="dark-select" style={{ fontSize: 12 }}>
              <option>Sales Analyst</option>
              <option>Manager</option>
              <option>Executive</option>
              <option>Data Scientist</option>
            </select>
          </div>
        </div>
      </div>

      {/* User Query */}
      <div style={{ padding: '14px', borderBottom: '1px solid var(--border)', flex: 1, display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Search size={13} color="var(--accent-cyan)" />
          <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>User Query</span>
          {/* live status dot */}
          <span className="status-dot healthy" style={{ marginLeft: 'auto' }} />
        </div>

        {/* Active query context */}
        {activeQuery && (
          <div style={{ background: 'rgba(0,212,255,0.05)', border: '1px solid rgba(0,212,255,0.2)', borderRadius: 8, padding: '8px 10px' }}>
            <div className="active-query-label">
              {queryMode === 'followup' ? '⤷ Follow-up on' : 'Active Query'}
            </div>
            <div className="active-query-text">{activeQuery}</div>
          </div>
        )}

        {/* PII Warning */}
        {showPIIWarning && (
          <div className="privacy-warning animate-fadeInUp">
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
              <AlertTriangle size={15} color="var(--warning)" style={{ flexShrink: 0, marginTop: 1 }} />
              <div>
                <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--warning)', marginBottom: 4 }}>
                  Privacy Warning
                </p>
                <p style={{ fontSize: 11, color: 'var(--text-primary)', lineHeight: 1.5, marginBottom: 10 }}>
                  This query may request personal customer data (names, DOB, contact, financial info).
                  Such data is <strong>protected</strong> under our privacy policy.
                </p>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button className="btn btn-danger" style={{ fontSize: 11, padding: '5px 10px' }} onClick={() => setShowPIIWarning(false)}>Cancel</button>
                  <button className="btn btn-ghost" style={{ fontSize: 11, padding: '5px 10px', border: '1px solid var(--border)' }} onClick={handleConfirmPII}>
                    Send Anyway
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Textarea */}
        <textarea
          className="dark-input"
          value={input}
          onChange={e => handleInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your sales data..."
          disabled={isLoading}
          rows={5}
          style={{ resize: 'none', lineHeight: 1.6, fontSize: 13 }}
        />

        <p style={{ fontSize: 10, color: 'var(--text-muted)' }}>
          Enter to send · Shift+Enter for new line
        </p>

        {/* Action buttons row 1 */}
        <div style={{ display: 'flex', gap: 6 }}>
          <button
            className={`btn btn-secondary ${queryMode === 'new' && !hasResult ? 'active' : ''}`}
            style={{ flex: 1, fontSize: 11, padding: '7px 8px' }}
            onClick={() => onNewQuery()}
            disabled={isLoading}
            title="Start a fresh query (clears context)"
          >
            <Plus size={12} />
            New Query
          </button>
          <button
            className={`btn btn-secondary ${queryMode === 'followup' ? 'active' : ''}`}
            style={{ flex: 1, fontSize: 11, padding: '7px 8px' }}
            onClick={onFollowUp}
            disabled={isLoading || !activeQuery}
            title="Ask a follow-up using previous context"
          >
            <GitBranch size={12} />
            Follow-up
          </button>
        </div>

        {/* Action buttons row 2 */}
        <div style={{ display: 'flex', gap: 6 }}>
          <button
            className="btn btn-ghost"
            style={{ flex: 1, fontSize: 11, padding: '7px 8px', border: '1px solid var(--border)' }}
            onClick={onClear}
            disabled={isLoading || !input}
          >
            <X size={12} />
            Clear
          </button>
          <button
            className="btn btn-send"
            style={{ flex: 2, fontSize: 12 }}
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
          >
            {isLoading ? (
              <><Loader size={13} className="animate-spin" />Analyzing…</>
            ) : (
              <><Send size={13} />Send</>
            )}
          </button>
        </div>
      </div>

      {/* Quick queries */}
      <div style={{ padding: '14px', flex: 1 }}>
        <p style={{ fontSize: 10, fontWeight: 700, letterSpacing: '1px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 10 }}>
          Quick Queries
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {getRelevantQueries(activeQuery).map((q, i) => (
            <button
              key={i}
              onClick={() => handleQuickQuery(q)}
              style={{
                background: 'var(--bg-card)', border: '1px solid var(--border)',
                borderRadius: 8, padding: '8px 10px',
                textAlign: 'left', cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: 6,
                transition: 'all 0.2s', color: 'var(--text-primary)',
                fontSize: 11, lineHeight: 1.4,
              }}
              onMouseEnter={e => {
                (e.currentTarget as HTMLElement).style.borderColor = 'var(--accent-cyan)';
                (e.currentTarget as HTMLElement).style.background = 'var(--bg-card-hover)';
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLElement).style.borderColor = 'var(--border)';
                (e.currentTarget as HTMLElement).style.background = 'var(--bg-card)';
              }}
            >
              <ChevronRight size={10} color="var(--accent-cyan)" style={{ flexShrink: 0 }} />
              {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default UserPanel;

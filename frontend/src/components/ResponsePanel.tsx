import React from 'react';
import { MessageSquare, Shield, Info, AlertCircle, Clock, Wifi, Key, Zap, RefreshCw, HelpCircle } from 'lucide-react';
import { QueryResponse } from '../services/api';

interface ResponsePanelProps {
  response: QueryResponse | null;
  isLoading: boolean;
  question: string;
}

// ── Error / special-status types returned by backend ─────────────────────────
const ERROR_STATUSES = new Set([
  'quota_exceeded', 'timeout', 'connection_error',
  'auth_error', 'sql_error', 'system_error',
  'needs_clarification',
]);

function getErrorConfig(vstatus: string) {
  switch (vstatus) {
    case 'needs_clarification':
      return {
        icon: <HelpCircle size={20} color="#00d4ff" />,
        title: 'Clarification Needed',
        color: '#00d4ff',
        bg: 'rgba(0,212,255,0.06)',
        border: 'rgba(0,212,255,0.25)',
        badge: '💬 Need More Info',
        badgeClass: 'badge-cyan',
      };
    case 'quota_exceeded':
      return {
        icon: <Clock size={20} color="#f59e0b" />,
        title: 'AI Quota Reached',
        color: '#f59e0b',
        bg: 'rgba(245,158,11,0.08)',
        border: 'rgba(245,158,11,0.3)',
        badge: '⏳ Quota Limit',
        badgeClass: 'badge-yellow',
      };
    case 'timeout':
      return {
        icon: <Clock size={20} color="#f59e0b" />,
        title: 'Request Timed Out',
        color: '#f59e0b',
        bg: 'rgba(245,158,11,0.08)',
        border: 'rgba(245,158,11,0.3)',
        badge: '⌛ Timeout',
        badgeClass: 'badge-yellow',
      };
    case 'connection_error':
      return {
        icon: <Wifi size={20} color="#ef4444" />,
        title: 'Connection Error',
        color: '#ef4444',
        bg: 'rgba(239,68,68,0.08)',
        border: 'rgba(239,68,68,0.3)',
        badge: '🔌 Offline',
        badgeClass: 'badge-red',
      };
    case 'auth_error':
      return {
        icon: <Key size={20} color="#ef4444" />,
        title: 'Authentication Error',
        color: '#ef4444',
        bg: 'rgba(239,68,68,0.08)',
        border: 'rgba(239,68,68,0.3)',
        badge: '🔑 Auth Failed',
        badgeClass: 'badge-red',
      };
    case 'sql_error':
      return {
        icon: <AlertCircle size={20} color="#f59e0b" />,
        title: 'Query Could Not Run',
        color: '#f59e0b',
        bg: 'rgba(245,158,11,0.08)',
        border: 'rgba(245,158,11,0.3)',
        badge: '⚠ SQL Error',
        badgeClass: 'badge-yellow',
      };
    default:
      return {
        icon: <AlertCircle size={20} color="#64748b" />,
        title: 'Something Went Wrong',
        color: '#64748b',
        bg: 'rgba(100,116,139,0.08)',
        border: 'rgba(100,116,139,0.3)',
        badge: '⚠ Error',
        badgeClass: 'badge-blue',
      };
  }
}

const LoadingSkeleton: React.FC = () => (
  <div style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 14 }}>
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
        <div className="skeleton" style={{ height: 12, width: 90 }} />
        <div className="skeleton" style={{ height: 12, width: 40 }} />
      </div>
      <div className="skeleton" style={{ height: 8, width: '100%' }} />
    </div>
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
      {[100, 85, 95, 70, 80, 60].map((w, i) => (
        <div key={i} className="skeleton" style={{ height: 14, width: `${w}%` }} />
      ))}
    </div>
  </div>
);

const ResponsePanel: React.FC<ResponsePanelProps> = ({ response, isLoading, question }) => {
  const isError = response && ERROR_STATUSES.has(response.validation_status);
  const isPrivacyBlocked = response?.privacy_blocked;

  /* ── Empty state ── */
  if (!response && !isLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div className="panel-header">
          <MessageSquare size={16} color="var(--accent-cyan)" />
          <span className="panel-header-title">AI Response</span>
        </div>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
          <div className="empty-icon">
            <MessageSquare size={22} />
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: 13, textAlign: 'center', lineHeight: 1.7 }}>
            The AI-generated response will appear here after your query.
          </p>
        </div>
      </div>
    );
  }

  /* ── Loading state ── */
  if (isLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div className="panel-header">
          <MessageSquare size={16} color="var(--accent-cyan)" />
          <span className="panel-header-title">AI Response</span>
          <div style={{ display: 'flex', gap: 5, marginLeft: 'auto' }}>
            <span className="dot-bounce" />
            <span className="dot-bounce" />
            <span className="dot-bounce" />
          </div>
        </div>
        <LoadingSkeleton />
      </div>
    );
  }

  /* ── Error state ── */
  if (isError) {
    const cfg = getErrorConfig(response!.validation_status);
    const lines = response!.answer.split('\n').filter(Boolean);
    const heading = lines[0] || cfg.title;
    const body = lines.slice(1).join('\n').trim();

    return (
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div className="panel-header">
          <MessageSquare size={16} color="var(--accent-cyan)" />
          <span className="panel-header-title">AI Response</span>
          <span className={`badge ${cfg.badgeClass}`} style={{ marginLeft: 'auto', fontSize: 10 }}>
            {cfg.badge}
          </span>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 14 }}
          className="animate-fadeInUp">

          {/* Error card */}
          <div style={{
            background: cfg.bg,
            border: `1px solid ${cfg.border}`,
            borderRadius: 12, padding: 18,
          }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
              {cfg.icon}
              <span style={{ fontSize: 14, fontWeight: 700, color: cfg.color }}>
                {heading}
              </span>
            </div>

            {/* Body lines */}
            {body && (
              <div style={{ fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.8 }}>
                {body.split('\n').map((line, i) => {
                  const isBullet = line.startsWith('•');
                  const isHeader = line.endsWith(':') && !isBullet;
                  return (
                    <p key={i} style={{
                      marginBottom: isBullet ? 4 : isHeader ? 10 : 8,
                      paddingLeft: isBullet ? 4 : 0,
                      color: isHeader ? 'var(--text-muted)' : 'var(--text-primary)',
                      fontWeight: isHeader ? 600 : 400,
                      fontSize: isHeader ? 11 : 13,
                      textTransform: isHeader ? 'uppercase' as const : 'none' as const,
                      letterSpacing: isHeader ? '0.5px' : 'normal',
                    }}>
                      {line}
                    </p>
                  );
                })}
              </div>
            )}
          </div>

          {/* Suggestion to retry */}
          {response!.validation_status === 'quota_exceeded' && (
            <div style={{
              background: 'rgba(0,212,255,0.04)',
              border: '1px solid rgba(0,212,255,0.15)',
              borderRadius: 10, padding: '10px 14px',
              display: 'flex', alignItems: 'center', gap: 10,
            }}>
              <Zap size={14} color="var(--accent-cyan)" />
              <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5 }}>
                💡 <strong style={{ color: 'var(--text-primary)' }}>Tip:</strong> Try switching to a cached question from the Quick Queries list.
                Cached results don't use AI quota.
              </p>
            </div>
          )}

          {response!.execution_time_ms > 0 && (
            <span className="badge badge-blue" style={{ alignSelf: 'flex-start', fontSize: 10 }}>
              ⏱ {Math.round(response!.execution_time_ms)}ms
            </span>
          )}
        </div>
      </div>
    );
  }

  /* ── Normal result state ── */
  const pct = Math.round((response!.confidence || 0) * 100);
  const confClass = pct >= 80 ? 'high' : pct >= 50 ? 'medium' : 'low';
  const confLabel = pct >= 80 ? 'High' : pct >= 50 ? 'Medium' : 'Low';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>

      {/* Panel header */}
      <div className="panel-header">
        <MessageSquare size={16} color="var(--accent-cyan)" />
        <span className="panel-header-title">AI Response</span>
        {isPrivacyBlocked && (
          <span className="badge badge-yellow" style={{ marginLeft: 'auto', fontSize: 10 }}>🔒 Privacy</span>
        )}
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 16 }}
        className="animate-slideInRight">

        {/* Privacy blocked notice */}
        {isPrivacyBlocked && (
          <div style={{
            background: 'rgba(245,158,11,0.08)',
            border: '1px solid rgba(245,158,11,0.35)',
            borderRadius: 10, padding: '10px 12px',
            display: 'flex', gap: 8, alignItems: 'center',
          }}>
            <Shield size={15} color="var(--warning)" />
            <p style={{ fontSize: 12, color: 'var(--warning)', fontWeight: 600 }}>
              Privacy Protection Active — Personal data blocked
            </p>
          </div>
        )}

        {/* Confidence meter — only show for real results */}
        {!isPrivacyBlocked && pct > 0 && (
          <div style={{
            background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border)',
            borderRadius: 10, padding: '12px 14px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                Confidence
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{
                  fontSize: 11, fontWeight: 700,
                  color: confClass === 'high' ? 'var(--success)' : confClass === 'medium' ? 'var(--warning)' : 'var(--danger)',
                }}>
                  {confLabel}
                </span>
                <span style={{ fontSize: 16, fontWeight: 800, color: 'var(--text-primary)' }}>{pct}%</span>
              </div>
            </div>
            <div className="confidence-bar-track">
              <div className={`confidence-bar-fill ${confClass}`} style={{ width: `${pct}%` }} />
            </div>
          </div>
        )}

        {/* Main answer */}
        <div style={{
          background: 'rgba(0,212,255,0.04)',
          border: '1px solid rgba(0,212,255,0.15)',
          borderRadius: 12, padding: 16,
        }}>
          <p style={{ fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.8, whiteSpace: 'pre-wrap' }}>
            {response!.answer}
          </p>
        </div>

        {/* Status badges */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
          {response!.cache_hit && <span className="badge badge-green" style={{ fontSize: 10 }}>⚡ Cached</span>}
          {response!.validation_status === 'passed' && <span className="badge badge-cyan" style={{ fontSize: 10 }}>✓ Validated</span>}
          {response!.validation_status === 'failed' && <span className="badge badge-yellow" style={{ fontSize: 10 }}>⚠ Unvalidated</span>}
          {response!.retry_count > 0 && (
            <span className="badge badge-yellow" style={{ fontSize: 10 }}>
              <RefreshCw size={9} /> {response!.retry_count} retries
            </span>
          )}
        </div>

        {/* Token usage */}
        {Object.keys(response!.token_usage).length > 0 && (
          <div style={{
            background: 'rgba(30, 41, 59, 0.4)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: 12,
            padding: '14px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <Zap size={13} color="var(--accent-cyan)" />
                <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--text-primary)' }}>
                  Token Metrics
                </span>
              </div>
              <span style={{ fontSize: 9, padding: '2px 6px', borderRadius: 4, background: 'rgba(0, 212, 255, 0.12)', color: 'var(--accent-cyan)', fontWeight: 700 }}>
                Gemini LLM
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '8px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.04)' }}>
                <div style={{ fontSize: '9px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Input Tokens</div>
                <div style={{ fontSize: '13px', fontWeight: 800, color: 'var(--text-primary)', marginTop: '2px' }}>
                  {((response!.token_usage.planner_input || 0) + (response!.token_usage.sql_input || 0) + (response!.token_usage.validator_input || 0) + (response!.token_usage.response_input || 0)).toLocaleString()}
                </div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '8px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.04)' }}>
                <div style={{ fontSize: '9px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Output Tokens</div>
                <div style={{ fontSize: '13px', fontWeight: 800, color: 'var(--accent-cyan)', marginTop: '2px' }}>
                  {((response!.token_usage.planner_output || 0) + (response!.token_usage.sql_output || 0) + (response!.token_usage.validator_output || 0) + (response!.token_usage.response_output || 0)).toLocaleString()}
                </div>
              </div>
            </div>

            {/* Collapsible/detailed Breakdown */}
            <details style={{ cursor: 'pointer', outline: 'none' }}>
              <summary style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 600, userSelect: 'none', display: 'flex', alignItems: 'center', gap: '4px', outline: 'none' }}>
                <Info size={11} />
                <span>Show Agent Breakdown</span>
              </summary>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginTop: 8, padding: '8px 4px 0 4px', borderTop: '1px dashed rgba(255,255,255,0.06)' }}>
                {/* Planner */}
                {((response!.token_usage.planner_input || 0) > 0) && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Planner Agent</span>
                    <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>
                      {((response!.token_usage.planner_input || 0) + (response!.token_usage.planner_output || 0)).toLocaleString()}
                    </span>
                  </div>
                )}
                {/* SQL Agent */}
                {((response!.token_usage.sql_input || 0) > 0) && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>SQL Gen Agent</span>
                    <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>
                      {((response!.token_usage.sql_input || 0) + (response!.token_usage.sql_output || 0)).toLocaleString()}
                    </span>
                  </div>
                )}
                {/* Validator */}
                {((response!.token_usage.validator_input || 0) > 0) && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Validator Agent</span>
                    <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>
                      {((response!.token_usage.validator_input || 0) + (response!.token_usage.validator_output || 0)).toLocaleString()}
                    </span>
                  </div>
                )}
                {/* Response */}
                {((response!.token_usage.response_input || 0) > 0) && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Response Agent</span>
                    <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>
                      {((response!.token_usage.response_input || 0) + (response!.token_usage.response_output || 0)).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
            </details>

            <div style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: 10, marginTop: 10, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Total Usage</span>
              <span style={{ fontSize: 13, fontWeight: 800, color: 'var(--accent-cyan)' }}>
                {Object.values(response!.token_usage).reduce((a, b) => a + b, 0).toLocaleString()} <span style={{ fontSize: '9px', fontWeight: 500, color: 'var(--text-muted)' }}>tokens</span>
              </span>
            </div>
          </div>
        )}

        {/* References */}
        {!isPrivacyBlocked && question && (
          <div style={{
            background: 'rgba(99,102,241,0.05)', border: '1px solid rgba(99,102,241,0.2)',
            borderRadius: 10, padding: '10px 14px',
          }}>
            <p style={{ fontSize: 10, fontWeight: 700, color: 'var(--accent-indigo)', letterSpacing: '0.8px', textTransform: 'uppercase', marginBottom: 5 }}>
              References & Notes
            </p>
            <p style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.6 }}>
              Query executed against the automotive sales database. Results reflect current data as of this session.
              {response!.retry_count > 0 && ` Query was retried ${response!.retry_count} time(s) for accuracy.`}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResponsePanel;

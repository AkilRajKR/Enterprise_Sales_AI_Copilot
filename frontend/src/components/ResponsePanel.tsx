import React from 'react';
import { MessageSquare, Shield, Info } from 'lucide-react';
import { QueryResponse } from '../services/api';

interface ResponsePanelProps {
  response: QueryResponse | null;
  isLoading: boolean;
  question: string;
}

const LoadingSkeleton: React.FC = () => (
  <div style={{ padding: 18, display: 'flex', flexDirection: 'column', gap: 14 }}>
    {/* Confidence skeleton */}
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
        <div className="skeleton" style={{ height: 12, width: 90 }} />
        <div className="skeleton" style={{ height: 12, width: 40 }} />
      </div>
      <div className="skeleton" style={{ height: 8, width: '100%' }} />
    </div>
    {/* Text skeletons */}
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
      {[100, 85, 95, 70, 80].map((w, i) => (
        <div key={i} className="skeleton" style={{ height: 14, width: `${w}%` }} />
      ))}
    </div>
  </div>
);

const ResponsePanel: React.FC<ResponsePanelProps> = ({ response, isLoading, question }) => {

  /* ── Empty state ── */
  if (!response && !isLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div className="panel-header">
          <MessageSquare size={16} color="var(--accent-cyan)" />
          <span className="panel-header-title">AI Response</span>
        </div>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
          <div className="empty-icon">
            <MessageSquare size={22} />
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: 13, textAlign: 'center', lineHeight: 1.6 }}>
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

  /* ── Result state ── */
  const pct = Math.round((response!.confidence || 0) * 100);
  const confClass = pct >= 80 ? 'high' : pct >= 50 ? 'medium' : 'low';
  const confLabel = pct >= 80 ? 'High' : pct >= 50 ? 'Medium' : 'Low';

  const isPrivacyBlocked = response!.privacy_blocked;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>

      {/* Panel header */}
      <div className="panel-header">
        <MessageSquare size={16} color="var(--accent-cyan)" />
        <span className="panel-header-title">AI Response</span>
        {isPrivacyBlocked && <span className="badge badge-yellow" style={{ marginLeft: 'auto', fontSize: 10 }}>🔒 Privacy</span>}
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 16 }} className="animate-slideInRight">

        {/* Privacy blocked notice */}
        {isPrivacyBlocked && (
          <div style={{
            background: 'linear-gradient(135deg, rgba(245,158,11,0.08), rgba(239,68,68,0.06))',
            border: '1px solid rgba(245,158,11,0.35)',
            borderRadius: 10, padding: '10px 12px',
            display: 'flex', gap: 8, alignItems: 'flex-start',
          }}>
            <Shield size={15} color="var(--warning)" style={{ flexShrink: 0, marginTop: 1 }} />
            <p style={{ fontSize: 12, color: 'var(--warning)', fontWeight: 600 }}>
              Privacy Protection Active
            </p>
          </div>
        )}

        {/* Confidence meter */}
        {!isPrivacyBlocked && (
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
              <div
                className={`confidence-bar-fill ${confClass}`}
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        )}

        {/* Main answer */}
        <div style={{
          background: 'rgba(0,212,255,0.04)',
          border: '1px solid rgba(0,212,255,0.15)',
          borderRadius: 12, padding: 16, flex: 1,
        }}>
          <p style={{ fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.75, whiteSpace: 'pre-wrap' }}>
            {response!.answer}
          </p>
        </div>

        {/* Status badges */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
          {response!.cache_hit && <span className="badge badge-green" style={{ fontSize: 10 }}>⚡ Cached</span>}
          {response!.validation_status === 'passed' && <span className="badge badge-cyan" style={{ fontSize: 10 }}>✓ Validated</span>}
          {response!.validation_status === 'failed' && <span className="badge badge-yellow" style={{ fontSize: 10 }}>⚠ Unvalidated</span>}
        </div>

        {/* Token usage */}
        {Object.keys(response!.token_usage).length > 0 && (
          <div style={{
            background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border)',
            borderRadius: 10, padding: '10px 14px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
              <Info size={12} color="var(--text-muted)" />
              <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                Token Usage
              </span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
              {Object.entries(response!.token_usage).map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'capitalize' }}>
                    {k.replace(/_/g, ' ')}
                  </span>
                  <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-primary)' }}>
                    {Number(v).toLocaleString()}
                  </span>
                </div>
              ))}
              <div style={{ borderTop: '1px solid var(--border)', paddingTop: 5, marginTop: 3, display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)' }}>Total</span>
                <span style={{ fontSize: 11, fontWeight: 800, color: 'var(--accent-cyan)' }}>
                  {Object.values(response!.token_usage).reduce((a, b) => a + b, 0).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* References / Notes */}
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

import React, { useState } from 'react';
import { BarChart2, Database, Copy, Check, Zap } from 'lucide-react';
import { QueryResponse } from '../services/api';

interface VisualizationPanelProps {
  response: QueryResponse | null;
  isLoading: boolean;
  onSampleClick: (q: string) => void;
}

const BAR_COLORS = [
  'linear-gradient(90deg,#6366f1,#8b5cf6)',
  'linear-gradient(90deg,#0ea5e9,#06b6d4)',
  'linear-gradient(90deg,#22c55e,#16a34a)',
  'linear-gradient(90deg,#f59e0b,#d97706)',
  'linear-gradient(90deg,#ec4899,#db2777)',
  'linear-gradient(90deg,#14b8a6,#0d9488)',
  'linear-gradient(90deg,#8b5cf6,#7c3aed)',
  'linear-gradient(90deg,#06b6d4,#0284c7)',
];

const SAMPLE_QUESTIONS = [
  { icon: '👥', text: 'How many customers are there?', desc: 'Customer Analytics' },
  { icon: '🏷️', text: 'Which brand has the most customers?', desc: 'Brand Performance' },
  { icon: '🚗', text: 'Which model has the highest sales?', desc: 'Model Performance' },
  { icon: '🏢', text: 'Which dealer sold the most vehicles?', desc: 'Dealer Analytics' },
  { icon: '🏭', text: 'Which plant produced the most vehicles?', desc: 'Manufacturing' },
  { icon: '🔧', text: 'What are the most popular car options?', desc: 'Product Insights' },
];

/** Extract key-value pairs from evidence or infer from answer text */
function extractChartData(response: QueryResponse): Array<{ label: string; value: number }> {
  const ev = response.evidence;
  if (ev && Object.keys(ev).length > 0) {
    return Object.entries(ev)
      .filter(([, v]) => typeof v === 'number')
      .map(([k, v]) => ({ label: k.replace(/_/g, ' '), value: Number(v) }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 8);
  }
  return [];
}

const LoadingSkeleton: React.FC = () => (
  <div style={{ display: 'flex', flexDirection: 'column', gap: 12, padding: 18 }}>
    <div className="skeleton" style={{ height: 22, width: '40%' }} />
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {[75, 60, 90, 50, 70].map((w, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div className="skeleton" style={{ height: 12, width: 80, flexShrink: 0 }} />
          <div className="skeleton" style={{ height: 24, width: `${w}%`, borderRadius: 4 }} />
        </div>
      ))}
    </div>
    <div className="skeleton" style={{ height: 14, width: '60%', marginTop: 8 }} />
    <div className="skeleton" style={{ height: 14, width: '80%' }} />
    <div className="skeleton" style={{ height: 14, width: '55%' }} />
  </div>
);

const VisualizationPanel: React.FC<VisualizationPanelProps> = ({ response, isLoading, onSampleClick }) => {
  const [copied, setCopied] = useState(false);

  const copySQL = async () => {
    if (!response?.sql_query) return;
    await navigator.clipboard.writeText(response.sql_query);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const chartData = response ? extractChartData(response) : [];
  const maxVal = chartData.length > 0 ? Math.max(...chartData.map(d => d.value)) : 1;

  /* ── Empty state ── */
  if (!response && !isLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
        {/* Panel header */}
        <div className="panel-header">
          <Zap size={16} color="var(--accent-cyan)" />
          <span className="panel-header-title">Data Visualization</span>
        </div>

        {/* Sample questions grid */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 18 }}>
          <p style={{ color: 'var(--text-muted)', fontSize: 13, textAlign: 'center', marginBottom: 20 }}>
            Submit a query to see chart and data results here.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            {SAMPLE_QUESTIONS.map((s, i) => (
              <button
                key={i}
                className="sample-card"
                onClick={() => onSampleClick(s.text)}
              >
                <div style={{ fontSize: 22, marginBottom: 8 }}>{s.icon}</div>
                <p style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4, lineHeight: 1.4 }}>{s.text}</p>
                <p style={{ fontSize: 10, color: 'var(--accent-cyan)', fontWeight: 600 }}>{s.desc}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Empty SQL panel */}
        <div style={{ borderTop: '1px solid var(--border)', padding: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
            <Database size={14} color="var(--accent-cyan)" />
            <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Generated SQL</span>
          </div>
          <p style={{ fontSize: 12, color: 'var(--text-muted)', fontStyle: 'italic' }}>
            Generated SQL will appear here — paired with the chart above.
          </p>
        </div>
      </div>
    );
  }

  /* ── Loading state ── */
  if (isLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
        <div className="panel-header">
          <Zap size={16} color="var(--accent-cyan)" />
          <span className="panel-header-title">Data Visualization</span>
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
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>

      {/* Panel header */}
      <div className="panel-header">
        <BarChart2 size={16} color="var(--accent-cyan)" />
        <span className="panel-header-title">
          {chartData.length > 0 ? 'Data Visualization' : 'Query Result'}
        </span>
        {chartData.length > 0 && (
          <span className="badge badge-cyan" style={{ marginLeft: 'auto', fontSize: 10 }}>
            {chartData.length} items
          </span>
        )}
      </div>

      {/* Chart / result area */}
      <div style={{ flex: 1, overflowY: 'auto', padding: 16 }} className="animate-fadeInUp">
        {chartData.length > 0 ? (
          /* Bar Chart */
          <div>
            <p style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 14 }}>
              {Object.keys(response!.evidence).filter(k => typeof response!.evidence[k] !== 'number').join(' by ') || 'Metric Breakdown'}
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {chartData.map((d, i) => {
                const pct = (d.value / maxVal) * 100;
                return (
                  <div key={i}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'capitalize' }}>{d.label}</span>
                      <span style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-primary)' }}>{d.value.toLocaleString()}</span>
                    </div>
                    <div style={{ background: 'var(--bg-base)', borderRadius: 4, height: 26, overflow: 'hidden' }}>
                      <div
                        className="chart-bar"
                        style={{
                          width: `${pct}%`,
                          background: BAR_COLORS[i % BAR_COLORS.length],
                          animationDelay: `${i * 80}ms`,
                        }}
                      >
                        {pct > 20 ? d.value.toLocaleString() : ''}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          /* Text result for non-numeric */
          <div style={{ padding: '12px 0' }}>
            <div style={{
              background: 'linear-gradient(135deg, rgba(0,212,255,0.06), rgba(99,102,241,0.06))',
              border: '1px solid rgba(0,212,255,0.2)',
              borderRadius: 12,
              padding: 18,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>Result</span>
                {response?.cache_hit && <span className="badge badge-green" style={{ fontSize: 10 }}>⚡ Cached</span>}
                {response?.validation_status === 'passed' && <span className="badge badge-cyan" style={{ fontSize: 10 }}>✓ Validated</span>}
              </div>
              <p style={{ color: 'var(--text-primary)', fontSize: 13, lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
                {response?.answer || 'No result data available.'}
              </p>
            </div>
          </div>
        )}

        {/* Meta badges */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 14 }}>
          <span className="badge badge-blue" style={{ fontSize: 10 }}>
            ⏱ {response!.execution_time_ms < 1000 ? `${Math.round(response!.execution_time_ms)}ms` : `${(response!.execution_time_ms / 1000).toFixed(1)}s`}
          </span>
          {response!.retry_count > 0 && (
            <span className="badge badge-yellow" style={{ fontSize: 10 }}>🔄 {response!.retry_count} retries</span>
          )}
          {response!.privacy_blocked && (
            <span className="badge badge-red" style={{ fontSize: 10 }}>🔒 Privacy Blocked</span>
          )}
        </div>
      </div>

      {/* SQL panel */}
      {response?.sql_query && (
        <div style={{ borderTop: '1px solid var(--border)', padding: '12px 14px', maxHeight: 220, display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
            <Database size={14} color="var(--accent-cyan)" />
            <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '1px', textTransform: 'uppercase', color: 'var(--text-muted)' }}>
              Generated SQL
            </span>
            <button
              onClick={copySQL}
              style={{
                marginLeft: 'auto', background: 'var(--bg-card)', border: '1px solid var(--border)',
                borderRadius: 6, padding: '4px 10px', cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: 5,
                fontSize: 11, color: 'var(--text-primary)', transition: 'all 0.2s',
              }}
              onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--accent-cyan)')}
              onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--border)')}
            >
              {copied ? <Check size={11} color="var(--success)" /> : <Copy size={11} />}
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <div className="sql-code-block" style={{ flex: 1, overflowY: 'auto' }}>
            <pre style={{ margin: 0 }}><code>{response.sql_query}</code></pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default VisualizationPanel;

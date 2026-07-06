import React, { useState } from 'react';
import { ChevronDown, Copy, Check, AlertTriangle } from 'lucide-react';

interface QueryResponse {
  question: string;
  answer: string;
  sql_query: string;
  evidence: Record<string, any>;
  confidence: number;
  cache_hit: boolean;
  retry_count: number;
  validation_status: string;
  execution_time_ms: number;
  token_usage: Record<string, number>;
}

interface MessageProps {
  response?: QueryResponse;
  error?: string;
}

/** Format milliseconds to human-readable string */
function formatMs(ms: number): string {
  if (ms < 1000) return `${Math.round(ms)} ms`;
  return `${(ms / 1000).toFixed(1)} s`;
}

const Message: React.FC<MessageProps> = ({ response, error }) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [copiedCode, setCopiedCode] = useState(false);

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      next.has(section) ? next.delete(section) : next.add(section);
      return next;
    });
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedCode(true);
      setTimeout(() => setCopiedCode(false), 2000);
    } catch {
      // fallback silently
    }
  };

  // ── Error state ───────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 shadow-sm flex gap-3">
        <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-red-800 font-semibold">Error</p>
          <p className="text-red-700 text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  if (!response) return null;

  // ── Confidence badge colour ───────────────────────────────────────────────
  const confidenceColor =
    response.confidence > 0.8
      ? 'text-green-700 bg-green-100 border border-green-200'
      : response.confidence > 0.5
      ? 'text-yellow-700 bg-yellow-100 border border-yellow-200'
      : 'text-red-700 bg-red-100 border border-red-200';

  const totalTokens = Object.values(response.token_usage).reduce((a, b) => a + b, 0);

  return (
    <div className="space-y-3 animate-slideInRight">
      {/* ── Answer card ─────────────────────────────────────────────────── */}
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl p-5 shadow-sm">
        <p className="text-slate-800 leading-relaxed whitespace-pre-wrap">{response.answer}</p>

        <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-indigo-200">
          {/* Confidence */}
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${confidenceColor}`}>
            Confidence: {(response.confidence * 100).toFixed(0)}%
          </span>

          {/* Cache badge */}
          {response.cache_hit && (
            <span className="px-3 py-1 bg-emerald-100 text-emerald-700 border border-emerald-200 rounded-full text-xs font-semibold">
              ⚡ Cached
            </span>
          )}

          {/* Validation badge */}
          {response.validation_status === 'passed' && (
            <span className="px-3 py-1 bg-blue-100 text-blue-700 border border-blue-200 rounded-full text-xs font-semibold">
              ✓ Validated
            </span>
          )}
          {response.validation_status === 'failed' && (
            <span className="px-3 py-1 bg-orange-100 text-orange-700 border border-orange-200 rounded-full text-xs font-semibold">
              ⚠ Unvalidated
            </span>
          )}

          {/* Retry count (only show if > 0) */}
          {response.retry_count > 0 && (
            <span className="px-3 py-1 bg-yellow-100 text-yellow-700 border border-yellow-200 rounded-full text-xs font-semibold">
              🔄 {response.retry_count} {response.retry_count === 1 ? 'retry' : 'retries'}
            </span>
          )}

          {/* Execution time */}
          <span className="px-3 py-1 bg-slate-100 text-slate-700 border border-slate-200 rounded-full text-xs font-semibold">
            ⏱ {formatMs(response.execution_time_ms)}
          </span>

          {/* Total tokens */}
          {totalTokens > 0 && (
            <span className="px-3 py-1 bg-purple-100 text-purple-700 border border-purple-200 rounded-full text-xs font-semibold">
              🪙 {totalTokens.toLocaleString()} tokens
            </span>
          )}
        </div>
      </div>

      {/* ── SQL Query accordion ──────────────────────────────────────────── */}
      {response.sql_query && (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
          <button
            id="btn-toggle-sql"
            onClick={() => toggleSection('sql')}
            className="w-full px-5 py-3 flex items-center justify-between hover:bg-slate-50 transition"
          >
            <span className="font-semibold text-slate-900 flex items-center space-x-2">
              <span className="text-lg">🔍</span>
              <span>Generated SQL Query</span>
            </span>
            <ChevronDown
              className={`w-5 h-5 text-slate-600 transition-transform ${
                expandedSections.has('sql') ? 'rotate-180' : ''
              }`}
            />
          </button>
          {expandedSections.has('sql') && (
            <div className="px-5 py-3 border-t border-slate-200 bg-slate-50">
              <div className="relative">
                <pre className="text-xs bg-slate-900 text-slate-100 p-4 rounded-lg overflow-x-auto font-mono leading-relaxed">
                  <code>{response.sql_query}</code>
                </pre>
                <button
                  id="btn-copy-sql"
                  onClick={() => copyToClipboard(response.sql_query)}
                  title={copiedCode ? 'Copied!' : 'Copy SQL'}
                  className="absolute top-2 right-2 p-2 bg-slate-700 hover:bg-slate-600 text-white rounded transition"
                >
                  {copiedCode ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── Evidence accordion ───────────────────────────────────────────── */}
      {Object.keys(response.evidence).length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
          <button
            id="btn-toggle-evidence"
            onClick={() => toggleSection('evidence')}
            className="w-full px-5 py-3 flex items-center justify-between hover:bg-slate-50 transition"
          >
            <span className="font-semibold text-slate-900 flex items-center space-x-2">
              <span className="text-lg">📊</span>
              <span>Evidence & Data</span>
            </span>
            <ChevronDown
              className={`w-5 h-5 text-slate-600 transition-transform ${
                expandedSections.has('evidence') ? 'rotate-180' : ''
              }`}
            />
          </button>
          {expandedSections.has('evidence') && (
            <div className="px-5 py-3 border-t border-slate-200 bg-slate-50">
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(response.evidence).map(([key, value]) => (
                  <div key={key} className="bg-white p-3 rounded-lg border border-slate-200">
                    <p className="text-xs text-slate-500 font-semibold uppercase tracking-wide">{key}</p>
                    <p className="text-lg font-bold text-slate-900 mt-1">{String(value)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── Token usage accordion ─────────────────────────────────────────── */}
      {totalTokens > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
          <button
            id="btn-toggle-tokens"
            onClick={() => toggleSection('tokens')}
            className="w-full px-5 py-3 flex items-center justify-between hover:bg-slate-50 transition"
          >
            <span className="font-semibold text-slate-900 flex items-center space-x-2">
              <span className="text-lg">🪙</span>
              <span>Token Usage</span>
            </span>
            <ChevronDown
              className={`w-5 h-5 text-slate-600 transition-transform ${
                expandedSections.has('tokens') ? 'rotate-180' : ''
              }`}
            />
          </button>
          {expandedSections.has('tokens') && (
            <div className="px-5 py-3 border-t border-slate-200 bg-slate-50">
              <div className="space-y-2">
                {Object.entries(response.token_usage).map(([agent, tokens]) => (
                  <div key={agent} className="flex justify-between text-sm">
                    <span className="text-slate-600 capitalize">{agent.replace(/_/g, ' ')}:</span>
                    <span className="font-semibold text-slate-900">{Number(tokens).toLocaleString()}</span>
                  </div>
                ))}
                <div className="border-t border-slate-300 pt-2 mt-2 flex justify-between text-sm font-bold">
                  <span className="text-slate-700">Total:</span>
                  <span className="text-indigo-600">{totalTokens.toLocaleString()}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Message;
import React, { useState } from 'react';
import { ChevronDown, Copy, Check } from 'lucide-react';

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

const Message: React.FC<MessageProps> = ({ response, error }) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [copiedCode, setCopiedCode] = useState(false);

  const toggleSection = (section: string) => {
    const newSet = new Set(expandedSections);
    if (newSet.has(section)) {
      newSet.delete(section);
    } else {
      newSet.add(section);
    }
    setExpandedSections(newSet);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  if (error) {
    return (
      <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 shadow-sm">
        <p className="text-red-800 font-semibold">Error</p>
        <p className="text-red-700 text-sm mt-1">{error}</p>
      </div>
    );
  }

  if (!response) return null;

  const confidenceColor =
    response.confidence > 0.8 ? 'text-green-600 bg-green-50' :
    response.confidence > 0.5 ? 'text-yellow-600 bg-yellow-50' :
    'text-red-600 bg-red-50';

  return (
    <div className="space-y-3 animate-slideInRight">
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-200 rounded-xl p-5 shadow-sm">
        <p className="text-slate-800 leading-relaxed">{response.answer}</p>
        
        <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-indigo-200">
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${confidenceColor}`}>
            Confidence: {(response.confidence * 100).toFixed(0)}%
          </span>
          {response.cache_hit && (
            <span className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-xs font-semibold">
              ⚡ From Cache
            </span>
          )}
          {response.validation_status === 'passed' && (
            <span className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-semibold">
              ✓ Validated
            </span>
          )}
          <span className="px-3 py-1 bg-slate-100 text-slate-700 rounded-full text-xs font-semibold">
            {response.execution_time_ms}ms
          </span>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        <button
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
              <pre className="text-xs text-slate-700 bg-slate-900 text-slate-100 p-4 rounded-lg overflow-x-auto">
                <code>{response.sql_query}</code>
              </pre>
              <button
                onClick={() => copyToClipboard(response.sql_query)}
                className="absolute top-2 right-2 p-2 bg-slate-700 hover:bg-slate-600 text-white rounded transition"
              >
                {copiedCode ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
          </div>
        )}
      </div>

      {Object.keys(response.evidence).length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
          <button
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
                    <p className="text-xs text-slate-600 font-semibold uppercase tracking-wide">{key}</p>
                    <p className="text-lg font-bold text-slate-900 mt-1">{String(value)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        <button
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
                  <span className="text-slate-600 capitalize">{agent}:</span>
                  <span className="font-semibold text-slate-900">{tokens} tokens</span>
                </div>
              ))}
              <div className="border-t border-slate-300 pt-2 mt-2">
                <div className="flex justify-between text-sm font-bold">
                  <span className="text-slate-700">Total:</span>
                  <span className="text-indigo-600">
                    {Object.values(response.token_usage).reduce((a, b) => a + b, 0)} tokens
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Message;
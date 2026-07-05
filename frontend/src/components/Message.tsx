import React from 'react';
import { QueryResponse } from '../services/api';
import { Check, AlertCircle, Database, Zap, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface MessageProps {
  question?: string;
  response?: QueryResponse;
  isLoading?: boolean;
  error?: string;
}

const Message: React.FC<MessageProps> = ({ question, response, isLoading, error }) => {
  if (error) {
    return (
      <div className="flex gap-3 mb-4">
        <div className="flex-1">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-red-800 font-semibold mb-2">
              <AlertCircle className="w-5 h-5" />
              Error
            </div>
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (isLoading && question) {
    return (
      <div className="flex gap-3 mb-4">
        <div className="flex-1">
          <div className="bg-gray-50 rounded-lg p-4 mb-2">
            <p className="text-gray-800 font-semibold">Q: {question}</p>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 animate-pulse">
            <p className="text-blue-600">Thinking...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!response) return null;

  const getValidationColor = () => {
    if (response.validation_status === 'passed') return 'bg-green-50 border-green-200';
    if (response.validation_status === 'failed') return 'bg-yellow-50 border-yellow-200';
    return 'bg-gray-50 border-gray-200';
  };

  const getConfidenceColor = () => {
    if (response.confidence >= 0.9) return 'text-green-600';
    if (response.confidence >= 0.7) return 'text-blue-600';
    if (response.confidence >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="flex flex-col gap-3 mb-4">
      {/* Question */}
      <div className="bg-gray-100 rounded-lg p-4">
        <p className="text-gray-700">
          <span className="font-semibold text-gray-800">Q:</span> {response.question}
        </p>
      </div>

      {/* Answer */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-gray-800">
          <span className="font-semibold text-blue-800">A:</span> {response.answer}
        </p>
      </div>

      {/* Metadata Badges */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {/* Confidence */}
        <div className="bg-white border border-gray-200 rounded-lg p-3">
          <div className="text-xs font-semibold text-gray-600 uppercase mb-1">Confidence</div>
          <div className={`text-lg font-bold ${getConfidenceColor()}`}>
            {(response.confidence * 100).toFixed(0)}%
          </div>
        </div>

        {/* Validation Status */}
        <div className="bg-white border border-gray-200 rounded-lg p-3">
          <div className="text-xs font-semibold text-gray-600 uppercase mb-1 flex items-center gap-1">
            <Check className="w-3 h-3" />
            Validation
          </div>
          <div className="text-sm font-bold text-gray-800 capitalize">
            {response.validation_status}
          </div>
        </div>

        {/* Cache Hit */}
        <div className="bg-white border border-gray-200 rounded-lg p-3">
          <div className="text-xs font-semibold text-gray-600 uppercase mb-1 flex items-center gap-1">
            <Database className="w-3 h-3" />
            Cache
          </div>
          <div className="text-sm font-bold">
            <span className={response.cache_hit ? 'text-green-600' : 'text-gray-600'}>
              {response.cache_hit ? 'HIT' : 'MISS'}
            </span>
          </div>
        </div>

        {/* Execution Time */}
        <div className="bg-white border border-gray-200 rounded-lg p-3">
          <div className="text-xs font-semibold text-gray-600 uppercase mb-1 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Time
          </div>
          <div className="text-sm font-bold text-gray-800">
            {response.execution_time_ms.toFixed(0)}ms
          </div>
        </div>
      </div>

      {/* Retry Count */}
      {response.retry_count > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <p className="text-sm text-yellow-800">
            <span className="font-semibold">Note:</span> This query required {response.retry_count} retry attempt(s) to validate.
          </p>
        </div>
      )}

      {/* SQL Query (Expandable) */}
      <details className="bg-gray-50 border border-gray-200 rounded-lg">
        <summary className="p-4 cursor-pointer hover:bg-gray-100 flex items-center gap-2 font-semibold text-gray-700">
          <span>📊 SQL Query</span>
        </summary>
        <div className="border-t border-gray-200 p-4 bg-gray-900 rounded-b-lg">
          <code className="text-green-400 text-sm font-mono break-words">
            {response.sql_query}
          </code>
        </div>
      </details>

      {/* Evidence */}
      {Object.keys(response.evidence).length > 0 && (
        <details className="bg-gray-50 border border-gray-200 rounded-lg">
          <summary className="p-4 cursor-pointer hover:bg-gray-100 flex items-center gap-2 font-semibold text-gray-700">
            <span>📈 Evidence</span>
          </summary>
          <div className="border-t border-gray-200 p-4">
            <div className="bg-white rounded p-3 font-mono text-sm text-gray-700 overflow-x-auto">
              <pre>{JSON.stringify(response.evidence, null, 2)}</pre>
            </div>
          </div>
        </details>
      )}

      {/* Token Usage */}
      {Object.keys(response.token_usage).length > 0 && (
        <details className="bg-gray-50 border border-gray-200 rounded-lg">
          <summary className="p-4 cursor-pointer hover:bg-gray-100 flex items-center gap-2 font-semibold text-gray-700">
            <Zap className="w-4 h-4" />
            <span>Token Usage</span>
          </summary>
          <div className="border-t border-gray-200 p-4">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {Object.entries(response.token_usage).map(([key, value]) => (
                <div key={key} className="bg-white border border-gray-200 rounded p-2">
                  <div className="text-xs text-gray-600 capitalize">{key.replace(/_/g, ' ')}</div>
                  <div className="text-sm font-bold text-gray-800">{value}</div>
                </div>
              ))}
            </div>
            <div className="mt-3 pt-3 border-t border-gray-200 font-semibold text-gray-700">
              Total: {Object.values(response.token_usage).reduce((a, b) => a + (b || 0), 0)} tokens
            </div>
          </div>
        </details>
      )}
    </div>
  );
};

export default Message;

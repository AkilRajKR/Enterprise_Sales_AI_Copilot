import React, { useState, useEffect } from 'react';
import { getHistory } from '../services/api';
import { Clock, X } from 'lucide-react';

interface HistoryQuery {
  id: number;
  original_question: string;
  answer: string;
  confidence: number;
  created_at: string;
}

interface QueryHistoryProps {
  onSelectQuery: (question: string) => void;
  isOpen?: boolean;
  onToggle?: (open: boolean) => void;
}

const QueryHistory: React.FC<QueryHistoryProps> = ({ onSelectQuery, isOpen = true, onToggle }) => {
  const [history, setHistory] = useState<HistoryQuery[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen]);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await getHistory(10);
      setHistory(data.queries || []);
    } catch (error) {
      console.error('Failed to fetch history:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => onToggle?.(true)}
        className="fixed bottom-4 right-4 p-3 bg-indigo-600 text-white rounded-full shadow-lg hover:shadow-xl hover:scale-110 transition-all"
        title="Show history"
      >
        <Clock className="w-5 h-5" />
      </button>
    );
  }

  return (
    <div className="w-80 bg-white border-l border-slate-200 flex flex-col shadow-lg">
      <div className="px-4 py-4 border-b border-slate-200 flex items-center justify-between">
        <h2 className="font-bold text-slate-900 flex items-center space-x-2">
          <Clock className="w-5 h-5 text-indigo-600" />
          <span>Query History</span>
        </h2>
        <button
          onClick={() => onToggle?.(false)}
          className="p-1 hover:bg-slate-100 rounded transition"
        >
          <X className="w-5 h-5 text-slate-600" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 p-3">
        {loading ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin">⏳</div>
            <p className="text-sm text-slate-500 mt-2">Loading...</p>
          </div>
        ) : history.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm text-slate-500">No queries yet</p>
          </div>
        ) : (
          history.map((query) => (
            <button
              key={query.id}
              onClick={() => onSelectQuery(query.original_question)}
              className="w-full text-left p-3 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg hover:shadow-md transition border border-indigo-100 hover:border-indigo-400"
            >
              <p className="text-xs text-slate-500 mb-1 truncate">
                {new Date(query.created_at).toLocaleTimeString()}
              </p>
              <p className="text-sm text-slate-900 font-medium line-clamp-2">
                {query.original_question}
              </p>
              <div className="flex justify-between items-center mt-2">
                <span className="text-xs text-slate-600 line-clamp-1">{query.answer}</span>
                <span className="text-xs font-bold text-indigo-600">
                  {(query.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </button>
          ))
        )}
      </div>

      <div className="px-3 py-3 border-t border-slate-200">
        <button
          onClick={fetchHistory}
          className="w-full px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 transition"
        >
          Refresh History
        </button>
      </div>
    </div>
  );
};

export default QueryHistory;
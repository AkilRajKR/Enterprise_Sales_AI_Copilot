import React, { useState, useEffect } from 'react';
import { HistoryItem, getHistory } from '../services/api';
import { History, X } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface QueryHistoryProps {
  onSelectQuery: (question: string) => void;
}

const QueryHistory: React.FC<QueryHistoryProps> = ({ onSelectQuery }) => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadHistory();
    }
  }, [isOpen]);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const data = await getHistory(50);
      setHistory(data.queries);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 bg-blue-600 text-white p-3 rounded-full shadow-lg hover:bg-blue-700 transition flex items-center justify-center"
        title="Query History"
      >
        <History className="w-6 h-6" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 w-96 bg-white border border-gray-200 rounded-lg shadow-lg flex flex-col max-h-96 z-50">
      <div className="flex justify-between items-center p-4 border-b border-gray-200">
        <h3 className="font-semibold text-gray-800 flex items-center gap-2">
          <History className="w-5 h-5" />
          Query History
        </h3>
        <button
          onClick={() => setIsOpen(false)}
          className="text-gray-500 hover:text-gray-700"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-gray-500">Loading...</div>
        ) : history.length === 0 ? (
          <div className="p-4 text-center text-gray-500">No queries yet</div>
        ) : (
          <div className="divide-y divide-gray-200">
            {history.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  onSelectQuery(item.original_question);
                  setIsOpen(false);
                }}
                className="w-full text-left p-3 hover:bg-gray-50 transition"
              >
                <p className="text-sm font-medium text-gray-800 line-clamp-2">
                  {item.original_question}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                </p>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default QueryHistory;

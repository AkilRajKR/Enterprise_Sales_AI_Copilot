import React from 'react';
import { Send, Loader } from 'lucide-react';

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ value, onChange, onSubmit, isLoading }) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="bg-white border-t border-slate-200 p-4 shadow-lg">
      <div className="max-w-5xl mx-auto w-full">
        <div className="flex space-x-3">
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything about your sales data..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 bg-slate-50 border-2 border-slate-200 rounded-xl focus:border-indigo-500 focus:bg-white transition disabled:opacity-50 placeholder-slate-400 text-slate-900"
          />
          <button
            onClick={onSubmit}
            disabled={isLoading || !value.trim()}
            className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-xl font-semibold hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 transition-all duration-200 flex items-center space-x-2"
          >
            {isLoading ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Ask</span>
              </>
            )}
          </button>
        </div>
        <p className="text-xs text-slate-500 mt-2 ml-1">
          💡 Tip: Press Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};

export default ChatInput;
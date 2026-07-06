import React, { useState, useRef, useEffect } from 'react';
import { askQuestion, QueryResponse } from './services/api';
import Header from './components/Header';
import ChatInput from './components/ChatInput';
import Message from './components/Message';
import QueryHistory from './components/QueryHistory';
import StatusBar from './components/StatusBar';

interface ChatMessage {
  type: 'question' | 'response' | 'error';
  question?: string;
  response?: QueryResponse;
  error?: string;
  timestamp: Date;
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return;

    const question = input.trim();
    setInput('');
    setIsLoading(true);

    setMessages((prev) => [...prev, { type: 'question', question, timestamp: new Date() }]);

    try {
      const response = await askQuestion(question);
      setMessages((prev) => [
        ...prev,
        { type: 'response', response, timestamp: new Date() },
      ]);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to get response';
      setMessages((prev) => [
        ...prev,
        { type: 'error', error: errorMessage, timestamp: new Date() },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectFromHistory = (question: string) => {
    setInput(question);
    setShowHistory(false);
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Header />
      <StatusBar />

      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
            <div className="max-w-5xl mx-auto w-full">
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center py-12">
                  <div className="mb-8">
                    <div className="w-24 h-24 bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                      <span className="text-5xl">💼</span>
                    </div>
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-900 to-indigo-600 bg-clip-text text-transparent mb-3">
                      Enterprise Sales AI
                    </h1>
                    <p className="text-slate-600 max-w-md mx-auto text-lg">
                      Intelligent analytics powered by AI. Ask questions about your sales data in natural language.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mt-10 max-w-4xl w-full">
                    {[
                      {
                          icon: '👥',
                          text: 'How many customers are there?',
                          desc: 'Customer Analytics',
                        },
                        {
                          icon: '🏷️',
                          text: 'Which brand has the most customers?',
                          desc: 'Brand Performance',
                        },
                        {
                          icon: '🚗',
                          text: 'Which model has the highest sales?',
                          desc: 'Model Performance',
                        },
                        {
                          icon: '🏢',
                          text: 'Which dealer sold the most vehicles?',
                          desc: 'Dealer Analytics',
                        },
                        {
                          icon: '🚘',
                          text: 'How many Toyota vehicles have been sold?',
                          desc: 'Brand Sales',
                        },
                        {
                          icon: '🏭',
                          text: 'Which manufacturing plant produced the most vehicles?',
                          desc: 'Manufacturing Insights',
                        },].map((sample, idx) => (
                      <button
                        key={idx}
                        onClick={() => setInput(sample.text)}
                        className="group p-4 bg-white rounded-xl border-2 border-slate-200 hover:border-indigo-500 hover:shadow-lg transition-all duration-300 text-left hover:bg-indigo-50"
                      >
                        <div className="text-2xl mb-2">{sample.icon}</div>
                        <p className="text-slate-700 font-semibold text-sm mb-1">{sample.text}</p>
                        <p className="text-slate-500 text-xs">{sample.desc}</p>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((msg, idx) => (
                    <div key={idx} className="animate-fadeIn">
                      {msg.type === 'question' && (
                        <div className="bg-white rounded-xl p-4 border-l-4 border-indigo-600 shadow-sm">
                          <p className="text-slate-800">
                            <span className="font-semibold text-indigo-600">Q:</span> {msg.question}
                          </p>
                        </div>
                      )}
                      {msg.type === 'response' && msg.response && (
                        <Message response={msg.response} />
                      )}
                      {msg.type === 'error' && (
                        <Message error={msg.error} />
                      )}
                    </div>
                  ))}
                  {isLoading && (
                    <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-4 border border-indigo-200 shadow-sm">
                      <div className="flex items-center space-x-3">
                        <div className="flex space-x-2">
                          <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce delay-100"></div>
                          <div className="w-2 h-2 bg-indigo-600 rounded-full animate-bounce delay-200"></div>
                        </div>
                        <p className="text-indigo-600 font-medium">Analyzing your question...</p>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>
          </div>

          <ChatInput
            value={input}
            onChange={setInput}
            onSubmit={handleSubmit}
            isLoading={isLoading}
          />
        </div>

        <QueryHistory 
          onSelectQuery={handleSelectFromHistory} 
          isOpen={showHistory}
          onToggle={setShowHistory}
        />
      </div>
    </div>
  );
}

export default App;
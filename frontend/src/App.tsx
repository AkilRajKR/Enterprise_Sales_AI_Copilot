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

    // Add loading message
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
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Header />
      <StatusBar />

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 max-w-6xl mx-auto w-full">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="mb-6">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-4xl">🤖</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Welcome to Sales AI</h2>
              <p className="text-gray-600 max-w-md mx-auto">
                Ask natural language questions about your sales data, customers, products, and employees.
              </p>
            </div>

            {/* Sample Questions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-8 max-w-2xl w-full">
              {[
                'What are total sales?',
                'How many customers do we have?',
                'Which product had the most sales?',
                'What is the average order value?',
              ].map((sample) => (
                <button
                  key={sample}
                  onClick={() => setInput(sample)}
                  className="p-3 bg-white border border-gray-300 rounded-lg text-left hover:border-blue-500 hover:bg-blue-50 transition"
                >
                  <p className="text-gray-700 font-medium text-sm">{sample}</p>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg, idx) => (
              <div key={idx}>
                {msg.type === 'question' && (
                  <div className="bg-gray-100 rounded-lg p-4 mb-2">
                    <p className="text-gray-700">
                      <span className="font-semibold text-gray-800">Q:</span> {msg.question}
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
              <div className="bg-blue-50 rounded-lg p-4 animate-pulse">
                <p className="text-blue-600">Thinking...</p>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <ChatInput
        value={input}
        onChange={setInput}
        onSubmit={handleSubmit}
        isLoading={isLoading}
      />

      {/* Query History */}
      <QueryHistory onSelectQuery={handleSelectFromHistory} />
    </div>
  );
}

export default App;

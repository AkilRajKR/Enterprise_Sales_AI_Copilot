import React, { useState, useEffect, useCallback } from 'react';
import { askQuestion, healthCheck, QueryResponse } from './services/api';
import Header from './components/Header';
import UserPanel from './components/UserPanel';
import VisualizationPanel from './components/VisualizationPanel';
import ResponsePanel from './components/ResponsePanel';

type ApiStatus = 'healthy' | 'checking' | 'unhealthy';

function App() {
  const [input, setInput]           = useState('');
  const [isLoading, setIsLoading]   = useState(false);
  const [response, setResponse]     = useState<QueryResponse | null>(null);
  const [activeQuery, setActiveQuery] = useState('');
  const [currentQuestion, setCurrentQuestion] = useState('');
  const [queryMode, setQueryMode]   = useState<'new' | 'followup'>('new');
  const [apiStatus, setApiStatus]   = useState<ApiStatus>('checking');

  /* ── API health polling ── */
  useEffect(() => {
    const check = async () => {
      try {
        const h = await healthCheck();
        setApiStatus(h.status === 'healthy' ? 'healthy' : 'unhealthy');
      } catch {
        setApiStatus('unhealthy');
      }
    };
    check();
    const id = setInterval(check, 30_000);
    return () => clearInterval(id);
  }, []);

  /* ── Submit ── */
  const handleSubmit = useCallback(async () => {
    if (!input.trim() || isLoading) return;

    const question = input.trim();
    setCurrentQuestion(question);
    setInput('');
    setActiveQuery(question);
    setIsLoading(true);
    setResponse(null);

    try {
      const res = await askQuestion(question);
      setResponse(res);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Failed to get response';
      // Show error as a synthetic response
      setResponse({
        question,
        answer: `⚠️ Error: ${msg}\n\nPlease check that the backend server is running and try again.`,
        sql_query: '',
        evidence: {},
        confidence: 0,
        cache_hit: false,
        retry_count: 0,
        validation_status: 'failed',
        execution_time_ms: 0,
        token_usage: {},
        privacy_blocked: false,
      });
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading]);

  /* ── New Query: clear everything ── */
  const handleNewQuery = useCallback(() => {
    setInput('');
    setQueryMode('new');
    setResponse(null);
    setActiveQuery('');
    setCurrentQuestion('');
  }, []);

  /* ── Follow-up: keep context, just switch mode ── */
  const handleFollowUp = useCallback(() => {
    setQueryMode('followup');
    setInput('');
  }, []);

  /* ── Clear input only ── */
  const handleClear = useCallback(() => {
    setInput('');
  }, []);

  /* ── Sample question clicked ── */
  const handleSampleClick = useCallback((q: string) => {
    setInput(q);
    setQueryMode('new');
    setResponse(null);
    setActiveQuery('');
    setCurrentQuestion('');
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden', background: 'var(--bg-base)' }}>

      {/* Header */}
      <Header apiStatus={apiStatus} />

      {/* 3-Column Body */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>

        {/* LEFT: User Panel */}
        <UserPanel
          input={input}
          onInputChange={setInput}
          onSubmit={handleSubmit}
          onNewQuery={handleNewQuery}
          onFollowUp={handleFollowUp}
          onClear={handleClear}
          isLoading={isLoading}
          queryMode={queryMode}
          activeQuery={activeQuery}
          hasResult={!!response}
        />

        {/* MIDDLE: Visualization Panel */}
        <div style={{
          flex: 1,
          background: 'var(--bg-panel)',
          borderRight: '1px solid var(--border)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}>
          <VisualizationPanel
            response={response}
            isLoading={isLoading}
            onSampleClick={handleSampleClick}
          />
        </div>

        {/* RIGHT: Response Panel */}
        <div style={{
          width: 340,
          background: 'var(--bg-panel)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          flexShrink: 0,
        }}>
          <ResponsePanel
            response={response}
            isLoading={isLoading}
            question={currentQuestion}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
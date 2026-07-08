import React, { useState, useEffect } from 'react';
import { Activity, Clock, Shield } from 'lucide-react';
import { healthCheck } from '../services/api';

interface HeaderProps {
  apiStatus: 'healthy' | 'checking' | 'unhealthy';
}

const Header: React.FC<HeaderProps> = ({ apiStatus }) => {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const fmt = (d: Date) =>
    d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });

  return (
    <header style={{ background: 'var(--header-bg)', borderBottom: '1px solid var(--border)' }}
      className="flex items-center justify-between px-6 py-3 z-50 flex-shrink-0">

      {/* Left: Logo */}
      <div className="flex items-center gap-3">
        <div style={{
          background: 'linear-gradient(135deg, #0ea5e9, #6366f1)',
          borderRadius: 10, width: 38, height: 38,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 18px rgba(14,165,233,0.35)'
        }}>
          <Activity size={20} color="#fff" />
        </div>
        <div>
          <div style={{ fontSize: 15, fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1.2 }}>
            Sales AI
          </div>
          <div style={{ fontSize: 9, fontWeight: 700, letterSpacing: '1.2px', color: 'var(--accent-cyan)', textTransform: 'uppercase' }}>
            Automotive Intelligence Platform
          </div>
        </div>
      </div>

      {/* Center: Title */}
      <div className="flex items-center gap-2" style={{ position: 'absolute', left: '50%', transform: 'translateX(-50%)' }}>
        <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '2px', textTransform: 'uppercase' }}>
          AI Analytics Copilot
        </span>
      </div>

      {/* Right: Session + Status + Badge */}
      <div className="flex items-center gap-4">
        {/* Privacy shield icon */}
        <div className="flex items-center gap-1" title="Privacy guard active">
          <Shield size={14} color="var(--success)" />
          <span style={{ fontSize: 10, color: 'var(--success)', fontWeight: 600 }}>Privacy Active</span>
        </div>

        {/* API Status */}
        <div className="flex items-center gap-2">
          <span className={`status-dot ${apiStatus}`} />
          <span style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 500 }}>
            Session · {fmt(time)}
          </span>
        </div>

        {/* Company Badge */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(0,212,255,0.15), rgba(59,130,246,0.15))',
          border: '1px solid rgba(0,212,255,0.3)',
          borderRadius: 8, padding: '5px 12px',
          fontSize: 12, fontWeight: 700, color: 'var(--accent-cyan)'
        }}>
          Allianz Sales
        </div>
      </div>
    </header>
  );
};

export default Header;
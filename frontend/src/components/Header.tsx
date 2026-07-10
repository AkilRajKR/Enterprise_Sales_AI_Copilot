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

      {/* Left: Brand */}
      <div className="flex items-center gap-3">
        <div style={{
          background: 'linear-gradient(135deg, #1e3a8a, #3b82f6)',
          borderRadius: 8, width: 34, height: 34,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 12px rgba(59,130,246,0.25)'
        }}>
          <Shield size={18} color="#fff" />
        </div>
        <div>
          <div style={{ fontSize: 13, fontWeight: 800, color: '#fff', letterSpacing: '0.5px', lineHeight: 1.2 }}>
            KINETIX
          </div>
          <div style={{ fontSize: 8, fontWeight: 700, letterSpacing: '1px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            Sales Analytics
          </div>
        </div>
      </div>

      {/* Center: Centered Proper App Name */}
      <div className="flex items-center gap-2" style={{ position: 'absolute', left: '50%', transform: 'translateX(-50%)' }}>
        <h1 style={{
          fontSize: '18px',
          fontWeight: 800,
          letterSpacing: '0.5px',
          background: 'linear-gradient(to right, #ffffff, #94a3b8, #38bdf8)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          margin: 0,
        }}>
          Kinetix Sales AI
        </h1>
      </div>

      {/* Right: API Health, Shield, Time */}
      <div className="flex items-center gap-4">
        {/* Privacy Active Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          padding: '4px 8px',
          borderRadius: '6px',
          fontSize: '11px',
          fontWeight: 600,
          background: 'rgba(16, 185, 129, 0.08)',
          color: '#10b981',
          border: '1px solid rgba(16, 185, 129, 0.15)',
        }} title="Data privacy guard active">
          <Shield size={12} color="#10b981" />
          <span>Privacy Guard</span>
        </div>

        {/* API Health Status Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 10px',
          borderRadius: '6px',
          fontSize: '11px',
          fontWeight: 600,
          border: '1px solid',
          background: apiStatus === 'healthy' ? 'rgba(16, 185, 129, 0.08)' 
                    : apiStatus === 'checking' ? 'rgba(59, 130, 246, 0.08)' 
                    : 'rgba(239, 68, 68, 0.08)',
          color: apiStatus === 'healthy' ? '#10b981' 
               : apiStatus === 'checking' ? '#3b82f6' 
               : '#ef4444',
          borderColor: apiStatus === 'healthy' ? 'rgba(16, 185, 129, 0.15)' 
                     : apiStatus === 'checking' ? 'rgba(59, 130, 246, 0.15)' 
                     : 'rgba(239, 68, 68, 0.15)',
        }}>
          <span style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            background: 'currentColor',
            boxShadow: apiStatus === 'healthy' ? '0 0 8px #10b981' 
                     : apiStatus === 'checking' ? '0 0 8px #3b82f6' 
                     : '0 0 8px #ef4444',
          }} />
          {apiStatus === 'healthy' ? 'API Active' 
           : apiStatus === 'checking' ? 'Checking API...' 
           : 'API Offline'}
        </div>

        {/* Time clock */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
          fontSize: '11px',
          color: 'var(--text-muted)',
          fontWeight: 500,
          background: 'rgba(255, 255, 255, 0.03)',
          padding: '4px 8px',
          borderRadius: '6px',
          border: '1px solid rgba(255, 255, 255, 0.05)',
        }}>
          <Clock size={12} />
          <span>{fmt(time)}</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
import React, { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';
import { healthCheck } from '../services/api';

const StatusBar: React.FC = () => {
  const [status, setStatus] = useState<'healthy' | 'checking' | 'unhealthy'>('checking');

  useEffect(() => {
    checkHealthStatus();
    const interval = setInterval(checkHealthStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkHealthStatus = async () => {
    try {
      const response = await healthCheck();
      setStatus(response.status === 'healthy' ? 'healthy' : 'unhealthy');
    } catch {
      setStatus('unhealthy');
    }
  };

  const statusConfig = {
    healthy: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200', label: 'API Healthy' },
    checking: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', label: 'Checking...' },
    unhealthy: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', label: 'API Unavailable' },
  };

  const config = statusConfig[status];

  return (
    <div className={`${config.bg} border-b ${config.border} px-4 py-2`}>
      <div className="max-w-7xl mx-auto flex items-center space-x-2">
        <Activity className={`w-4 h-4 ${config.text}`} />
        <span className={`text-sm font-medium ${config.text}`}>{config.label}</span>
        {status === 'checking' && <span className="inline-block animate-spin">⟳</span>}
      </div>
    </div>
  );
};

export default StatusBar;
import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Wifi, WifiOff } from 'lucide-react';
import { healthCheck } from '../services/api';

const StatusBar: React.FC = () => {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  useEffect(() => {
    const check = async () => {
      try {
        await healthCheck();
        setIsHealthy(true);
      } catch (error) {
        setIsHealthy(false);
      }
      setLastCheck(new Date());
    };

    check();
    const interval = setInterval(check, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (isHealthy === null) return null;

  return (
    <div
      className={`p-3 text-sm flex items-center gap-2 ${
        isHealthy
          ? 'bg-green-50 border-b border-green-200 text-green-700'
          : 'bg-red-50 border-b border-red-200 text-red-700'
      }`}
    >
      {isHealthy ? (
        <>
          <CheckCircle className="w-4 h-4" />
          <span>API is healthy</span>
        </>
      ) : (
        <>
          <AlertCircle className="w-4 h-4" />
          <span>API is unavailable</span>
        </>
      )}
      {lastCheck && (
        <span className="text-xs ml-auto opacity-75">
          Last checked {lastCheck.toLocaleTimeString()}
        </span>
      )}
    </div>
  );
};

export default StatusBar;

import React from 'react';
import { Activity, Settings } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-lg flex items-center justify-center">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Sales AI</h1>
            <p className="text-xs text-slate-500">Enterprise Analytics Platform</p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <button className="p-2 hover:bg-slate-100 rounded-lg transition">
            <Settings className="w-5 h-5 text-slate-600" />
          </button>
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-full flex items-center justify-center cursor-pointer hover:shadow-lg transition">
            <span className="text-white font-bold text-sm">AI</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
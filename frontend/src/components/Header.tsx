import React from 'react';
import { Brain } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-6 shadow-lg">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-3 mb-2">
          <Brain className="w-8 h-8" />
          <h1 className="text-3xl font-bold">Enterprise Sales AI</h1>
        </div>
        <p className="text-blue-100">Multi-agent AI system for sales analytics</p>
      </div>
    </header>
  );
};

export default Header;

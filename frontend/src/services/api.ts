import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface QueryRequest {
  question: string;
}

export interface QueryResponse {
  question: string;
  answer: string;
  sql_query: string;
  evidence: Record<string, any>;
  confidence: number;
  cache_hit: boolean;
  retry_count: number;
  validation_status: string;
  execution_time_ms: number;
  token_usage: Record<string, number>;
}

export interface HistoryItem {
  id: number;
  original_question: string;
  answer: string;
  confidence: number;
  created_at: string;
}

export interface HistoryResponse {
  total: number;
  queries: HistoryItem[];
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
}

export const askQuestion = async (question: string): Promise<QueryResponse> => {
  const response = await apiClient.post<QueryResponse>('/ask', {
    question,
  });
  return response.data;
};

export const getHistory = async (limit: number = 50): Promise<HistoryResponse> => {
  const response = await apiClient.get<HistoryResponse>(`/history?limit=${limit}`);
  return response.data;
};

export const healthCheck = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
};

export default apiClient;

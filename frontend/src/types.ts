export interface CountryFormData {
  name: string;
  countryCode: string;
  population: number;
  birthRate: number;
  deathRate: number;
  gdpPerCapita: number;
  urbanization: number;
  educationIndex: number;
  healthcareSpending: number;
  fertilityRate: number;
  medianAge: number;
  lifeExpectancy: number;
}

export interface ForecastPoint {
  year: number;
  population: number;
  growthRate: number;
  birthRate: number;
  deathRate: number;
}

export interface ModelMetrics {
  train_rmse: number;
  val_rmse: number;
  train_mae: number;
  val_mae: number;
  train_r2: number;
  val_r2: number;
  training_time: number;
  feature_importance: Record<string, number>;
}

export interface PredictionResponse {
  forecast: ForecastPoint[];
  metrics?: ModelMetrics | null;
  rag_adjustments?: {
    summary?: string;
    adjustments?: Record<string, number>;
    insights?: string[];
    sources?: { title: string; url: string }[];
  } | null;
}

export interface ModelStatus {
  is_trained: boolean;
  metrics?: ModelMetrics | null;
  feature_importance?: Record<string, number> | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
}

export interface ChatContext {
  country?: string;
  use_rag?: boolean;
  population?: number;
  forecast_years?: number;
  adjustments?: Record<string, number>;
}

export interface ChatResponsePayload {
  response: string;
  timestamp: string;
}


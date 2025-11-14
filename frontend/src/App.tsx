import { useCallback, useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  CountryFormData,
  ForecastPoint,
  ModelMetrics,
  ModelStatus,
  PredictionResponse,
  ChatMessage,
  ChatResponsePayload
} from "./types";
import OverviewDonutChart from "./components/OverviewDonutChart";
import ForecastAreaChart from "./components/ForecastAreaChart";
import PopulationPyramidChart from "./components/PopulationPyramidChart";
import CountryComparisonChart from "./components/CountryComparisonChart";
import FeatureImportanceChart from "./components/FeatureImportanceChart";
import ChatPopup from "./components/ChatPopup";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api";

type StatSummary = {
  key: string;
  label: string;
  value: number;
  format?: "percentage" | "currency" | "number";
  accent?: "blue" | "green" | "orange" | "purple";
};

type AgeDistribution = {
  label: string;
  male: number;
  female: number;
};

type ResearchHighlight = {
  title: string;
  description: string;
};

type CountryProfile = {
  code: string;
  name: string;
  formPreset: CountryFormData;
  stats: StatSummary[];
  insights: string[];
  research: ResearchHighlight[];
  ageDistribution: AgeDistribution[];
};

type CountriesResponse = {
  countries: CountryProfile[];
  missing?: string[];
};

const DEFAULT_COUNTRY_CODE = "VN";

const TABS = [
  { id: "overview", label: "Tổng Quan" },
  { id: "forecast", label: "Dự Báo AI" },
  { id: "pyramid", label: "Tháp Dân Số" },
  { id: "comparison", label: "So Sánh" },
  { id: "model", label: "Mô Hình AI" }
];

const formatValue = (value: number, format: StatSummary["format"]) => {
  if (format === "percentage") {
    return `${value.toFixed(2)}%`;
  }

  if (format === "currency") {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0
    }).format(value);
  }

  return new Intl.NumberFormat("vi-VN", {
    maximumFractionDigits: 1
  }).format(value);
};

const formatPopulation = (value: number) => {
  if (value >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(1)} tỷ`;
  }
  if (value >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)} triệu`;
  }
  return new Intl.NumberFormat("vi-VN").format(value);
};

const App = () => {
  const [profiles, setProfiles] = useState<Record<string, CountryProfile>>({});
  const [countryOrder, setCountryOrder] = useState<string[]>([]);
  const [activeCountry, setActiveCountry] = useState<string>(DEFAULT_COUNTRY_CODE);
  const [formValues, setFormValues] = useState<CountryFormData | null>(null);
  const [years, setYears] = useState<number>(50);
  const [useRag, setUseRag] = useState<boolean>(true);
  const [forecast, setForecast] = useState<ForecastPoint[]>([]);
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [ragAdjustments, setRagAdjustments] =
    useState<PredictionResponse["rag_adjustments"]>(null);
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [chatOpen, setChatOpen] = useState<boolean>(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatLoading, setChatLoading] = useState<boolean>(false);
  const [chatError, setChatError] = useState<string | null>(null);

  const selectedProfile = profiles[activeCountry];

  const runPrediction = useCallback(
    async (overrideData?: CountryFormData, overrideYears?: number, ragOverride?: boolean) => {
      const payloadData = overrideData ?? formValues;
      if (!payloadData) {
        return;
      }
      const forecastYears = overrideYears ?? years;
      const ragEnabled = ragOverride ?? useRag;

      setLoading(true);
      setError(null);
      try {
        const payload = {
          country_data: {
            name: payloadData.name,
            country_code: payloadData.countryCode,
            country_code_iso3: payloadData.countryCode,
            population: payloadData.population,
            birthRate: payloadData.birthRate,
            deathRate: payloadData.deathRate,
            gdpPerCapita: payloadData.gdpPerCapita,
            urbanization: payloadData.urbanization,
            educationIndex: payloadData.educationIndex,
            healthcareSpending: payloadData.healthcareSpending,
            fertilityRate: payloadData.fertilityRate,
            medianAge: payloadData.medianAge,
            lifeExpectancy: payloadData.lifeExpectancy
          },
          years: forecastYears,
          use_rag: ragEnabled
        };

        const response = await axios.post<PredictionResponse>(
          `${API_BASE_URL}/predict`,
          payload
        );

        setForecast(response.data.forecast ?? []);
        setMetrics(response.data.metrics ?? null);
        setRagAdjustments(response.data.rag_adjustments ?? null);
      } catch (requestError: any) {
        if (requestError?.response?.data?.detail) {
          setError(requestError.response.data.detail);
        } else {
          setError("Không thể dự báo. Vui lòng thử lại sau.");
        }
      } finally {
        setLoading(false);
      }
    },
    [formValues, useRag, years]
  );

  useEffect(() => {
    axios
      .get<CountriesResponse>(`${API_BASE_URL}/countries/asean`)
      .then((response) => {
        const mapped = response.data.countries.reduce<Record<string, CountryProfile>>(
          (acc, profile) => {
            acc[profile.code] = profile;
            return acc;
          },
          {}
        );
        setProfiles(mapped);
        const order = response.data.countries.map((item) => item.code);
        setCountryOrder(order);
        const initialCode = mapped[DEFAULT_COUNTRY_CODE] ? DEFAULT_COUNTRY_CODE : order[0];
        if (initialCode) {
          setActiveCountry(initialCode);
          setFormValues(mapped[initialCode].formPreset);
          runPrediction(mapped[initialCode].formPreset, years, useRag);
        }
      })
      .catch(() => {
        setError("Không thể tải dữ liệu ASEAN. Vui lòng thử lại sau.");
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCountryChange = (code: string) => {
    const profile = profiles[code];
    if (!profile) return;
    setActiveCountry(code);
    setFormValues(profile.formPreset);
    setYears(50);
    runPrediction(profile.formPreset, 50);
  };

  const handleSliderChange = (key: "birthRate" | "deathRate", value: number) => {
    setFormValues((prev) => {
      if (!prev) return prev;
      const updated = { ...prev, [key]: value };
      runPrediction(updated);
      return updated;
    });
  };

  const handleYearsChange = (value: number) => {
    setYears(value);
    runPrediction(undefined, value);
  };

  const handleSendChat = async (message: string) => {
    const timestamp = new Date().toISOString();
    const newMessage: ChatMessage = {
      id: `user-${timestamp}`,
      role: "user",
      content: message,
      timestamp
    };

    setChatMessages((prev) => [...prev, newMessage]);
    setChatLoading(true);
    setChatError(null);

    try {
      const context = {
        country: selectedProfile.name,
        use_rag: useRag,
        population: formValues.population,
        forecast_years: years,
        adjustments: {
          birthRate: formValues.birthRate,
          deathRate: formValues.deathRate,
          gdpPerCapita: formValues.gdpPerCapita,
          urbanization: formValues.urbanization
        }
      };

      const response = await axios.post<ChatResponsePayload>(`${API_BASE_URL}/chat`, {
        message,
        context
      });

      const assistantMessage: ChatMessage = {
        id: `assistant-${response.data.timestamp}`,
        role: "assistant",
        content: response.data.response,
        timestamp: response.data.timestamp
      };

      setChatMessages((prev) => [...prev, assistantMessage]);
    } catch (requestError: any) {
      setChatError(
        requestError?.response?.data?.detail ?? "Không thể gọi trợ lý AI. Vui lòng thử lại sau."
      );
    } finally {
      setChatLoading(false);
    }
  };

  useEffect(() => {
    axios
      .get<ModelStatus>(`${API_BASE_URL}/model/status`)
      .then((response) => setModelStatus(response.data))
      .catch(() => setModelStatus(null));
  }, []);

  useEffect(() => {
    runPrediction(formValues, years);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const forecastSummary = useMemo(() => {
    if (!forecast.length) {
      return null;
    }
    const start = forecast[0];
    const end = forecast[forecast.length - 1];
    const absoluteGrowth = end.population - start.population;
    const totalGrowthRate = start.population
      ? (absoluteGrowth / start.population) * 100
      : 0;

    return {
      startPopulation: start.population,
      endPopulation: end.population,
      absoluteGrowth,
      totalGrowthRate
    };
  }, [forecast]);

  const comparisonDataset = useMemo(() => {
    return countryOrder
      .map((code) => {
        const profile = profiles[code];
        if (!profile) {
          return null;
        }
        return {
          label: profile.name,
          population: profile.formPreset.population / 1_000_000,
          birthRate: profile.formPreset.birthRate,
          deathRate: profile.formPreset.deathRate
        };
      })
      .filter(Boolean) as {
      label: string;
      population: number;
      birthRate: number;
      deathRate: number;
    }[];
  }, [countryOrder, profiles]);

  const dynamicStats = useMemo(() => {
    if (!selectedProfile) {
      return [];
    }
    // Use original profile data (World Bank), not adjusted form values
    const sourceData = selectedProfile.formPreset;
    return selectedProfile.stats.map((stat) => {
      switch (stat.key) {
        case "population":
          return { ...stat, value: sourceData.population / 1_000_000 };
        case "birthRate":
          return { ...stat, value: sourceData.birthRate };
        case "deathRate":
          return { ...stat, value: sourceData.deathRate };
        case "growth":
          return { ...stat, value: sourceData.birthRate - sourceData.deathRate };
        case "gdp":
          return { ...stat, value: sourceData.gdpPerCapita };
        default:
          return stat;
      }
    });
  }, [selectedProfile]);

  const statusReady = modelStatus?.is_trained ?? false;
  const statusR2 =
    metrics?.val_r2 ?? modelStatus?.metrics?.val_r2 ?? modelStatus?.metrics?.train_r2 ?? null;

  if (!selectedProfile || !formValues) {
    return (
      <div className="dashboard-shell">
        <div className="alert loading">Đang tải dữ liệu ASEAN...</div>
      </div>
    );
  }

  return (
    <div className="dashboard-shell">
      <button
        type="button"
        className="chat-launcher"
        onClick={() => setChatOpen(true)}
        aria-label="Mở chat AI"
      >
        AI Chat
      </button>

      <ChatPopup
        open={chatOpen}
        messages={chatMessages}
        loading={chatLoading}
        error={chatError}
        onClose={() => setChatOpen(false)}
        onSend={handleSendChat}
      />
      <header className="dashboard-header">
        <div>
          <h1>Mô Hình Phân Tích Dân Số</h1>
          <p>Machine Learning dự báo dân số</p>
        </div>
        <div className={`model-badge ${statusReady ? "ready" : "idle"}`}>
          <span className="dot" />
          {statusReady ? "Mô hình đã sẵn sàng" : "Đang chờ huấn luyện"}
          {statusR2 ? ` • R²: ${(statusR2 * 100).toFixed(1)}%` : ""}
        </div>
      </header>

      <section className="country-strip">
        <div className="country-select">
          <span className="country-label">Chọn Quốc Gia:</span>
          <div className="country-buttons">
            {countryOrder.map((code) => (
              <button
                key={code}
                type="button"
                className={`country-button ${activeCountry === code ? "active" : ""}`}
                onClick={() => handleCountryChange(code)}
              >
                {profiles[code]?.name ?? code}
              </button>
            ))}
          </div>
        </div>
        <div className="model-mode">
          <span>Kích hoạt RAG</span>
          <label className="toggle">
            <input
              type="checkbox"
              checked={useRag}
              onChange={(event) => {
                const nextValue = event.target.checked;
                setUseRag(nextValue);
                runPrediction(undefined, years, nextValue);
              }}
            />
            <span className="toggle-slider" />
          </label>
        </div>
      </section>

      <nav className="tab-bar">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            className={`tab-button ${activeTab === tab.id ? "active" : ""}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <div className="dashboard-layout">
        <aside className="sidebar">
          <div className="sidebar-card">
            <h3>Thông Kê Hiện Tại</h3>
            <div className="stat-list">
              {dynamicStats.map((stat) => (
                <div className={`stat-chip ${stat.accent ?? ""}`} key={stat.key}>
                  <span>{stat.label}</span>
                  <strong>{formatValue(stat.value, stat.format)}</strong>
                </div>
              ))}
            </div>
          </div>

          <div className="sidebar-card">
            <h3>Phân Tích AI</h3>
            <ul className="insight-list">
              {selectedProfile.insights.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="sidebar-card">
            <h3>AI &amp; Nghiên Cứu Dân Số</h3>
            <div className="research-grid">
              {selectedProfile.research.map((item) => (
                <article className="research-card" key={item.title}>
                  <h4>{item.title}</h4>
                  <p>{item.description}</p>
                </article>
              ))}
            </div>
          </div>
        </aside>

        <main className="main-panel">
          {error && <div className="alert error">{error}</div>}
          {loading && !forecast.length && (
            <div className="alert loading">Đang tải dự báo từ mô hình...</div>
          )}

          {activeTab === "overview" && (
            <section className="panel-card">
              <div className="panel-header">
                <h2>Tổng Quan • {selectedProfile.name}</h2>
                {forecastSummary && (
                  <div className="summary-badge">
                    Tăng trưởng {forecastSummary.totalGrowthRate.toFixed(1)}% trong{" "}
                    {years} năm
                  </div>
                )}
              </div>
              <div className="overview-grid">
                <div className="highlight-card">
                  <span>Tổng Dân Số</span>
                  <h3>{formatPopulation(formValues.population)}</h3>
                  {forecastSummary && (
                    <p>
                      Dự báo: {formatPopulation(forecastSummary.endPopulation)} năm{" "}
                      {forecast.length ? forecast[forecast.length - 1].year : ""}
                    </p>
                  )}
                </div>
                <div className="highlight-card success">
                  <span>Tăng Trưởng Hiện Tại</span>
                  <h3>
                    {formatValue(
                      dynamicStats.find((stat) => stat.key === "growth")?.value ?? 0,
                      "percentage"
                    )}
                  </h3>
                  <p>Duy trì đà tăng trưởng bền vững trong 5 năm tới.</p>
                </div>
                <div className="highlight-card gradient">
                  <span>Ghi chú mô hình</span>
                  <p>
                    Mô hình XGBoost kết hợp RAG điều chỉnh theo ngữ cảnh để dự báo dân số
                    chính xác và giàu thông tin.
                  </p>
                </div>
              </div>

              <div className="panel-split">
                <div className="chart-card">
                  <h3>Phân Bố Độ Tuổi</h3>
                  <OverviewDonutChart
                    data={selectedProfile.ageDistribution.map((item) => ({
                      label: item.label,
                      value: item.male + item.female
                    }))}
                  />
                </div>
                <div className="chart-card">
                  <h3>Dự Báo Dân Số</h3>
                  <ForecastAreaChart data={forecast} />
                </div>
              </div>

              {ragAdjustments && (
                <div className="panel-card rag-panel">
                  <div className="panel-header">
                    <h3>Điều chỉnh RAG</h3>
                    <span className="rag-tag">Nguồn dữ liệu AI</span>
                  </div>
                  {ragAdjustments.summary && (
                    <p className="rag-summary">{ragAdjustments.summary}</p>
                  )}
                  {ragAdjustments.insights && (
                    <ul className="rag-insights">
                      {ragAdjustments.insights.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </section>
          )}

          {activeTab === "forecast" && (
            <section className="panel-card">
              <div className="panel-header">
                <h2>Dự Báo AI • {selectedProfile.name}</h2>
                <div className="controls">
                  <div className="control-item">
                    <label htmlFor="yearsSlider">Số năm dự báo: {years}</label>
                    <input
                      id="yearsSlider"
                      type="range"
                      min={5}
                      max={75}
                      step={5}
                      value={years}
                      onChange={(event) => handleYearsChange(Number(event.target.value))}
                    />
                  </div>
                  <div className="control-item">
                    <label htmlFor="birthRateSlider">
                      Tỷ lệ sinh: {formValues.birthRate.toFixed(1)}‰
                    </label>
                    <input
                      id="birthRateSlider"
                      type="range"
                      min={5}
                      max={40}
                      step={0.1}
                      value={formValues.birthRate}
                      onChange={(event) =>
                        handleSliderChange("birthRate", Number(event.target.value))
                      }
                    />
                  </div>
                  <div className="control-item">
                    <label htmlFor="deathRateSlider">
                      Tỷ lệ tử: {formValues.deathRate.toFixed(1)}‰
                    </label>
                    <input
                      id="deathRateSlider"
                      type="range"
                      min={2}
                      max={20}
                      step={0.1}
                      value={formValues.deathRate}
                      onChange={(event) =>
                        handleSliderChange("deathRate", Number(event.target.value))
                      }
                    />
                  </div>
                </div>
              </div>

              <ForecastAreaChart data={forecast} />

              {forecastSummary && (
                <div className="forecast-summary-grid">
                  <div>
                    <span>Hiện tại</span>
                    <strong>{formatPopulation(forecastSummary.startPopulation)}</strong>
                  </div>
                  <div>
                    <span>{forecast.length ? forecast[forecast.length - 1].year : ""}</span>
                    <strong>{formatPopulation(forecastSummary.endPopulation)}</strong>
                  </div>
                  <div>
                    <span>Thay đổi</span>
                    <strong>{forecastSummary.totalGrowthRate.toFixed(1)}%</strong>
                  </div>
                </div>
              )}
            </section>
          )}

          {activeTab === "pyramid" && (
            <section className="panel-card">
              <div className="panel-header">
                <h2>Tháp Dân Số • {selectedProfile.name}</h2>
              </div>
              <PopulationPyramidChart data={selectedProfile.ageDistribution} />
            </section>
          )}

          {activeTab === "comparison" && (
            <section className="panel-card">
              <div className="panel-header">
                <h2>So Sánh Các Quốc Gia</h2>
              </div>
              <CountryComparisonChart dataset={comparisonDataset} />
            </section>
          )}

          {activeTab === "model" && (
            <section className="panel-card">
              <div className="panel-header">
                <h2>Mô Hình AI</h2>
              </div>
              {metrics ? (
                <div className="model-grid">
                  <div className="model-card">
                    <h3>Độ chính xác</h3>
                    <div className="metric-pair">
                      <span>R² Validation</span>
                      <strong>{metrics.val_r2.toFixed(3)}</strong>
                    </div>
                    <div className="metric-pair">
                      <span>RMSE Validation</span>
                      <strong>{metrics.val_rmse.toFixed(3)}</strong>
                    </div>
                    <div className="metric-pair">
                      <span>MAE Validation</span>
                      <strong>{metrics.val_mae.toFixed(3)}</strong>
                    </div>
                    <div className="metric-pair">
                      <span>Training Time</span>
                      <strong>{metrics.training_time.toFixed(2)}s</strong>
                    </div>
                  </div>
                  <div className="model-card">
                    <h3>Tầm quan trọng đặc trưng</h3>
                    <FeatureImportanceChart data={metrics.feature_importance} />
                  </div>
                </div>
              ) : (
                <div className="alert info">
                  Chưa có thông số mô hình. Hãy huấn luyện mô hình trước khi theo dõi.
                </div>
              )}
            </section>
          )}
        </main>
      </div>
    </div>
  );
};

export default App;


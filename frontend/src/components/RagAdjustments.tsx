import { PredictionResponse } from "../types";

type Props = {
  data: PredictionResponse["rag_adjustments"];
};

const RagAdjustments = ({ data }: Props) => {
  if (!data) {
    return (
      <div className="empty-state">
        Chưa có điều chỉnh RAG. Bật chế độ RAG trong biểu mẫu để xem gợi ý.
      </div>
    );
  }

  const { summary, adjustments, insights, sources } = data;

  return (
    <div className="rag-section">
      <span className="rag-tag">AI RAG Insights</span>
      {summary && <p>{summary}</p>}

      {adjustments && Object.keys(adjustments).length > 0 && (
        <div className="rag-adjustments">
          {Object.entries(adjustments).map(([key, value]) => (
            <div className="adjustment-item" key={key}>
              <span>{key}</span>
              <strong>{value > 0 ? `+${value.toFixed(2)}` : value.toFixed(2)}</strong>
            </div>
          ))}
        </div>
      )}

      {insights && insights.length > 0 && (
        <div className="forecast-summary">
          <span className="summary-title">Nhận định</span>
          {insights.map((insight, index) => (
            <span className="summary-line" key={index}>
              {insight}
            </span>
          ))}
        </div>
      )}

      {sources && sources.length > 0 && (
        <div className="forecast-summary">
          <span className="summary-title">Nguồn tham khảo</span>
          {sources.map((source, index) => (
            <span className="summary-line" key={index}>
              <a href={source.url} target="_blank" rel="noreferrer">
                {source.title}
              </a>
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export default RagAdjustments;


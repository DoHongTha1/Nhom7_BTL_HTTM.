import { FormEvent } from "react";
import { CountryFormData } from "../types";

const FEATURE_LABELS: Record<keyof CountryFormData, string> = {
  name: "Tên quốc gia",
  countryCode: "Mã quốc gia",
  population: "Dân số hiện tại",
  birthRate: "Tỷ suất sinh (‰)",
  deathRate: "Tỷ suất tử (‰)",
  gdpPerCapita: "GDP bình quân đầu người (USD)",
  urbanization: "Đô thị hóa (%)",
  educationIndex: "Chỉ số giáo dục",
  healthcareSpending: "Chi tiêu y tế (% GDP)",
  fertilityRate: "Tổng tỷ suất sinh",
  medianAge: "Độ tuổi trung vị",
  lifeExpectancy: "Tuổi thọ trung bình"
};

type Props = {
  values: CountryFormData;
  years: number;
  useRag: boolean;
  loading: boolean;
  onChange: (key: keyof CountryFormData, value: string) => void;
  onYearsChange: (value: number) => void;
  onToggleRag: (value: boolean) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

const numericKeys: (keyof CountryFormData)[] = [
  "population",
  "birthRate",
  "deathRate",
  "gdpPerCapita",
  "urbanization",
  "educationIndex",
  "healthcareSpending",
  "fertilityRate",
  "medianAge",
  "lifeExpectancy"
];

const PopulationForm = ({
  values,
  years,
  useRag,
  loading,
  onChange,
  onYearsChange,
  onToggleRag,
  onSubmit
}: Props) => {
  return (
    <form className="card" onSubmit={onSubmit}>
      <div className="card-header">
        <h2 className="card-title">Thông số đầu vào</h2>
      </div>

      <div className="form-grid">
        {(Object.keys(values) as (keyof CountryFormData)[]).map((key) => (
          <div className="form-group" key={key}>
            <label htmlFor={key}>{FEATURE_LABELS[key]}</label>
            <input
              id={key}
              type={numericKeys.includes(key) ? "number" : "text"}
              min={numericKeys.includes(key) ? "0" : undefined}
              step={numericKeys.includes(key) ? "0.01" : undefined}
              required={key === "name" || key === "countryCode" || key === "population"}
              value={
                numericKeys.includes(key)
                  ? String(values[key] ?? "")
                  : (values[key] as string)
              }
              onChange={(event) => onChange(key, event.target.value)}
            />
          </div>
        ))}
      </div>

      <div className="form-grid">
        <div className="form-group">
          <label htmlFor="years">Số năm dự báo</label>
          <input
            id="years"
            type="number"
            min={1}
            max={30}
            value={years}
            onChange={(event) => onYearsChange(Number(event.target.value))}
          />
        </div>
        <div className="form-group">
          <label htmlFor="useRag">Kích hoạt điều chỉnh RAG</label>
          <select
            id="useRag"
            value={useRag ? "true" : "false"}
            onChange={(event) => onToggleRag(event.target.value === "true")}
          >
            <option value="false">Tắt</option>
            <option value="true">Bật</option>
          </select>
        </div>
      </div>

      <button className="submit-button" type="submit" disabled={loading}>
        {loading ? "Đang dự báo..." : "Dự báo dân số"}
      </button>
    </form>
  );
};

export default PopulationForm;


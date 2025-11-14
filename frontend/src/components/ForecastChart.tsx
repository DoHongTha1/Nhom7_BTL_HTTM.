import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from "chart.js";
import { ForecastPoint } from "../types";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

type Props = {
  data: ForecastPoint[];
};

const ForecastChart = ({ data }: Props) => {
  if (!data.length) {
    return (
      <div className="chart-wrapper">
        <p className="empty-state">Nhập thông số và chạy dự báo để xem biểu đồ.</p>
      </div>
    );
  }

  const chartData = {
    labels: data.map((point) => point.year),
    datasets: [
      {
        label: "Dân số dự báo",
        data: data.map((point) => Math.round(point.population)),
        borderColor: "#4a6cf7",
        backgroundColor: "rgba(74, 108, 247, 0.16)",
        tension: 0.35,
        fill: true,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: "#f5f8ff"
      },
      {
        label: "Tăng trưởng (%)",
        data: data.map((point) => point.growthRate),
        borderColor: "#f59e0b",
        backgroundColor: "rgba(245, 158, 11, 0.12)",
        tension: 0.3,
        yAxisID: "growth-rate",
        pointRadius: 4,
        pointHoverRadius: 6
      }
    ]
  };

  const options = {
    responsive: true,
    interaction: {
      mode: "index" as const,
      intersect: false
    },
    scales: {
      y: {
        title: {
          display: true,
          text: "Dân số"
        },
        ticks: {
          callback: (value: number | string) => {
            const num = typeof value === "string" ? Number(value) : value;
            if (num >= 1_000_000_000) {
              return `${(num / 1_000_000_000).toFixed(1)}B`;
            }
            if (num >= 1_000_000) {
              return `${(num / 1_000_000).toFixed(1)}M`;
            }
            return num.toLocaleString();
          }
        }
      },
      "growth-rate": {
        position: "right" as const,
        grid: {
          drawOnChartArea: false
        },
        title: {
          display: true,
          text: "Tăng trưởng (%)"
        }
      }
    },
    plugins: {
      legend: {
        labels: {
          color: "#0f1729"
        }
      },
      tooltip: {
        callbacks: {
          label: (context: any) => {
            if (context.dataset.label === "Dân số dự báo") {
              return `${context.dataset.label}: ${context.raw.toLocaleString()}`;
            }
            return `${context.dataset.label}: ${context.raw.toFixed(2)}%`;
          }
        }
      }
    }
  };

  return (
    <div className="chart-wrapper">
      <h3 className="chart-title">Dự báo dân số và tốc độ tăng trưởng</h3>
      <Line data={chartData} options={options} />
    </div>
  );
};

export default ForecastChart;


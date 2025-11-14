import { memo } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler,
  ChartOptions
} from "chart.js";
import { Line } from "react-chartjs-2";
import { ForecastPoint } from "../types";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler
);

type Props = {
  data: ForecastPoint[];
};

const ForecastAreaChart = memo(({ data }: Props) => {
  if (!data.length) {
    return <p className="empty-state">Chưa có dự báo. Điều chỉnh thông số để xem kết quả.</p>;
  }

  const chartData = {
    labels: data.map((item) => item.year),
    datasets: [
      {
        label: "Dân số (triệu người)",
        data: data.map((item) => item.population / 1_000_000),
        borderColor: "#6366f1",
        backgroundColor: "rgba(79, 70, 229, 0.18)",
        tension: 0.4,
        fill: true,
        pointRadius: 3,
        pointHoverRadius: 5
      },
      {
        label: "Tăng trưởng (%)",
        data: data.map((item) => item.growthRate),
        borderColor: "#f97316",
        backgroundColor: "rgba(249, 115, 22, 0.12)",
        yAxisID: "growth",
        tension: 0.3,
        fill: false,
        pointRadius: 2,
        pointHoverRadius: 4
      }
    ]
  };

  const options: ChartOptions<"line"> = {
    responsive: true,
    interaction: {
      mode: "index",
      intersect: false
    },
    scales: {
      y: {
        title: {
          display: true,
          text: "Dân số (triệu)"
        },
        grid: {
          color: "rgba(15, 23, 42, 0.08)"
        }
      },
      growth: {
        position: "right",
        title: {
          display: true,
          text: "Tăng trưởng (%)"
        },
        grid: {
          drawOnChartArea: false
        }
      }
    },
    plugins: {
      legend: {
        display: true,
        labels: {
          color: "#334155"
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            if (context.dataset.label === "Dân số (triệu người)") {
              return `${context.dataset.label}: ${context.parsed.y.toFixed(2)} triệu`;
            }
            return `${context.dataset.label}: ${context.parsed.y.toFixed(2)}%`;
          }
        }
      }
    }
  };

  return <Line data={chartData} options={options} />;
});

export default ForecastAreaChart;


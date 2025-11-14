import { memo } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  ChartOptions
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Tooltip,
  Legend
);

type ComparisonRow = {
  label: string;
  population: number;
  birthRate: number;
  deathRate: number;
};

type Props = {
  dataset: ComparisonRow[];
};

const CountryComparisonChart = memo(({ dataset }: Props) => {
  if (!dataset.length) {
    return <p className="empty-state">Chưa có dữ liệu so sánh.</p>;
  }

  const labels = dataset.map((item) => item.label);

  const chartData = {
    labels,
    datasets: [
      {
        type: "bar" as const,
        label: "Dân số (triệu)",
        data: dataset.map((item) => item.population),
        backgroundColor: "rgba(99, 102, 241, 0.8)",
        borderRadius: 8,
        order: 1
      },
      {
        type: "line" as const,
        label: "Tỷ lệ sinh (‰)",
        data: dataset.map((item) => item.birthRate),
        borderColor: "#22c55e",
        backgroundColor: "#22c55e",
        fill: false,
        yAxisID: "rates",
        tension: 0.3,
        order: 0
      },
      {
        type: "line" as const,
        label: "Tỷ lệ tử (‰)",
        data: dataset.map((item) => item.deathRate),
        borderColor: "#ef4444",
        backgroundColor: "#ef4444",
        fill: false,
        yAxisID: "rates",
        tension: 0.3,
        order: 0
      }
    ]
  };

  const options: ChartOptions<"bar"> = {
    responsive: true,
    scales: {
      y: {
        title: {
          display: true,
          text: "Dân số (triệu)"
        },
        grid: {
          color: "rgba(15, 23, 42, 0.06)"
        }
      },
      rates: {
        position: "right",
        title: {
          display: true,
          text: "‰"
        },
        grid: {
          drawOnChartArea: false
        }
      }
    },
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          color: "#0f172a"
        }
      }
    }
  };

  return <Bar data={chartData} options={options} />;
});

export default CountryComparisonChart;


import { memo } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
  ChartOptions
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

type Props = {
  data: Record<string, number>;
};

const FeatureImportanceChart = memo(({ data }: Props) => {
  const entries = Object.entries(data ?? {});

  if (!entries.length) {
    return <p className="empty-state">Chưa có dữ liệu tầm quan trọng đặc trưng.</p>;
  }

  const chartData = {
    labels: entries.map(([label]) => label),
    datasets: [
      {
        label: "Tầm quan trọng",
        data: entries.map(([, value]) => value),
        backgroundColor: "rgba(59, 130, 246, 0.75)",
        borderRadius: 6
      }
    ]
  };

  const options: ChartOptions<"bar"> = {
    indexAxis: "y",
    responsive: true,
    scales: {
      x: {
        ticks: {
          callback: (value) => `${Number(value).toFixed(2)}`
        }
      }
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.parsed.x.toFixed(3)}`
        }
      }
    }
  };

  return <Bar data={chartData} options={options} />;
});

export default FeatureImportanceChart;

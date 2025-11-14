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
  data: {
    label: string;
    male: number;
    female: number;
  }[];
};

const PopulationPyramidChart = memo(({ data }: Props) => {
  if (!data.length) {
    return <p className="empty-state">Chưa có dữ liệu tháp dân số.</p>;
  }

  const chartData = {
    labels: data.map((item) => item.label),
    datasets: [
      {
        label: "Nam (%)",
        data: data.map((item) => -item.male),
        backgroundColor: "rgba(59, 130, 246, 0.8)"
      },
      {
        label: "Nữ (%)",
        data: data.map((item) => item.female),
        backgroundColor: "rgba(249, 168, 212, 0.7)"
      }
    ]
  };

  const options: ChartOptions<"bar"> = {
    indexAxis: "y",
    responsive: true,
    scales: {
      x: {
        stacked: true,
        ticks: {
          callback: (value) => `${Math.abs(Number(value)).toFixed(0)}%`
        },
        title: {
          display: true,
          text: "Tỷ trọng dân số (%)"
        }
      },
      y: {
        stacked: true
      }
    },
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          color: "#0f172a"
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const val = Math.abs(Number(context.parsed.x)).toFixed(2);
            return `${context.dataset.label}: ${val}%`;
          }
        }
      }
    }
  };

  return <Bar data={chartData} options={options} />;
});

export default PopulationPyramidChart;


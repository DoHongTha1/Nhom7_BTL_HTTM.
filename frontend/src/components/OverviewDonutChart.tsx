import { memo } from "react";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  Title,
  ChartOptions
} from "chart.js";
import { Pie } from "react-chartjs-2";

ChartJS.register(ArcElement, Tooltip, Legend, Title);

type Props = {
  data: {
    label: string;
    value: number;
  }[];
};

const OverviewDonutChart = memo(({ data }: Props) => {
  if (!data.length) {
    return <p className="empty-state">Chưa có dữ liệu độ tuổi.</p>;
  }

  const chartData = {
    labels: data.map((item) => item.label),
    datasets: [
      {
        data: data.map((item) => item.value),
        backgroundColor: ["#4F46E5", "#7C3AED", "#0EA5E9", "#22C55E", "#F97316"],
        hoverOffset: 8,
        borderColor: "#FFFFFF",
        borderWidth: 2
      }
    ]
  };

  const options: ChartOptions<"pie"> = {
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          usePointStyle: true,
          color: "#0f172a",
          padding: 20
        }
      },
      title: {
        display: false
      }
    }
  };

  return <Pie data={chartData} options={options} />;
});

export default OverviewDonutChart;


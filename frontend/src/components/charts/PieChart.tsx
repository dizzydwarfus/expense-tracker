"use client";

import React from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import ChartDataLabels from "chartjs-plugin-datalabels";

// Register Chart.js components/plugins
ChartJS.register(ArcElement, Tooltip, Legend, ChartDataLabels);

interface PieChartProps {
  categories: string[];
  amounts: number[];
}

export default function PieChart({ categories, amounts }: PieChartProps) {
  const data = {
    labels: categories,
    datasets: [
      {
        data: amounts,
        backgroundColor: [
          "rgba(255, 99, 132, 0.2)", // Red
          "rgba(54, 162, 235, 0.2)", // Blue
          "rgba(255, 206, 86, 0.2)", // Yellow
          "rgba(75, 192, 192, 0.2)", // Teal
          "rgba(153, 102, 255, 0.2)", // Purple
          "rgba(255, 159, 64, 0.2)", // Orange
          // add more colors if you have more categories
        ],
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      tooltip: { enabled: true },
      legend: {
        display: true,
        labels: {
          color: "#FFFFFF",
        },
      },
      datalabels: {
        color: "#FFFFFF",
        formatter: (value: number) =>
          value === 0 ? "" : `€${value.toFixed(2)}`,
      },
    },
  };

  return <Pie data={data} options={options} />;
}

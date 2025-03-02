"use client";

import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import ChartDataLabels from "chartjs-plugin-datalabels";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartDataLabels
);

interface Dataset {
  label: string;
  data: number[];
  backgroundColor?: string | string[];
}

interface StackedBarChartProps {
  dates: string[];
  categoryData: Dataset[];
}

export default function StackedBarChart({
  dates,
  categoryData,
}: StackedBarChartProps) {
  // Optionally assign background colors, etc.
  // We'll assume your array already has them.

  const data = {
    labels: dates,
    datasets: categoryData, // e.g. [{ label: 'Food', data: [10,20], backgroundColor: 'rgba(...)' }, ...]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        stacked: true as const,
        ticks: {
          color: "#FFF",
        },
      },
      y: {
        stacked: true as const,
        ticks: {
          color: "#FFF",
        },
      },
    },
    plugins: {
      legend: {
        display: true,
        labels: {
          color: "#FFF",
        },
      },
      tooltip: {
        enabled: true,
      },
      datalabels: {
        color: "#FFFFFF",
        anchor: "end" as const,
        align: "top" as const,
        formatter: (value: number) =>
          value === 0 ? "" : `€${value.toFixed(2)}`,
      },
    },
  };

  return <Bar data={data} options={options} />;
}

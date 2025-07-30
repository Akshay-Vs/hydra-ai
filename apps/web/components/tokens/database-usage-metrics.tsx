'use client';

import type { ChartData, ChartOptions } from 'chart.js';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

import { lineOptions } from '@/configs/charts/line-chart';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const DatabaseUsageChart = () => {
  const options: ChartOptions<'line'> = {
    ...lineOptions,
    scales: {
      x: {
        display: true,
        title: {
          display: true,
        },
        grid: {
          display: false,
        },
        border: {
          display: false,
        },
      },
      y: {
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'Usage (in GB)',
        },
        suggestedMin: -10,
        suggestedMax: 200,
      },
    },
    plugins: {
      ...lineOptions.plugins,
      tooltip: {
        ...lineOptions.plugins?.tooltip,
        callbacks: {
          ...lineOptions.plugins?.tooltip?.callbacks,
          label: context => {
            const datasetLabel = context.dataset.label ?? '';
            const value = context.raw;
            return `${datasetLabel}: ${value}GB`;
          },
        },
      },
    },
  };

  const data: ChartData<'line'> = {
    labels: ['12/07', '12/08', '12/09', '12/10', '12/11', '12/12', '12/13'],
    datasets: [
      {
        label: 'TiVector',
        data: [0, 0, 0, 540, 600, 690, 740],
        backgroundColor: '#9F97E4',
        fill: true,
        borderColor: '#9F97E4',
        cubicInterpolationMode: 'monotone',
        tension: 0.4,
        borderWidth: 2,
      },
      {
        label: 'TiKV',
        data: [0, 0, 20, 50, 100, 140, 170],
        backgroundColor: '#E4D297',
        borderColor: '#E4D297',
        fill: true,
        cubicInterpolationMode: 'monotone',
        tension: 0.4,
        borderWidth: 2,
      },
      {
        label: 'TiFlash',
        data: [0, 0, 0, 150, 500, 540, 670],
        backgroundColor: '#DA97E4',
        borderColor: '#DA97E4',
        fill: true,
        cubicInterpolationMode: 'monotone',
        tension: 0.4,
        borderWidth: 2,
      },
    ],
  };

  return <Line options={options} data={data} className="max-h-[calc(45vh-3rem)] px-4" />;
};

export default DatabaseUsageChart;

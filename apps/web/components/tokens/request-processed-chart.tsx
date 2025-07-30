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

const RequestProcessedChart = () => {
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
        display: false,
        title: {
          display: true,
          text: 'Value',
        },
        suggestedMin: -10,
        suggestedMax: 200,
      },
    },
  };

  const data: ChartData<'line'> = {
    labels: ['1:00', '1:30', '2:00', '2:30', '3:00', '3:30', '4:00'],
    datasets: [
      {
        label: 'Passed requests',
        data: [100, 400, 500, 200, 600, 900, 340],
        backgroundColor: '#97CAE4',
        borderColor: '#97CAE4',
        cubicInterpolationMode: 'monotone',
        tension: 0.4,
        borderWidth: 2,
      },
      {
        label: 'Failed requests',
        data: [4, 20, 10, 500, 60, 0, 7],
        backgroundColor: '#E49797',
        borderColor: '#E49797',
        cubicInterpolationMode: 'monotone',
        tension: 0.4,
        borderWidth: 2,
      },
    ],
  };

  return <Line options={options} data={data} className="h-56 px-4" />;
};

export default RequestProcessedChart;

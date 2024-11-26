// src/components/HealthRadarChart.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Radar } from 'react-chartjs-2';

const HealthRadarChart = () => {
    const [data, setData] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('http://localhost:4000/health-metrics/device123'); // Replace with your device_id
                setData(response.data);
            } catch (error) {
                console.error('Error fetching health metrics data:', error);
            }
        };
        fetchData();
    }, []);

    const aggregatedMetrics = data.reduce((acc, curr) => {
        if (!acc[curr.metric_type]) acc[curr.metric_type] = 0;
        acc[curr.metric_type] += curr.value;
        return acc;
    }, {});

    const chartData = {
        labels: Object.keys(aggregatedMetrics),
        datasets: [
            {
                label: 'Health Metrics',
                data: Object.values(aggregatedMetrics),
                backgroundColor: 'rgba(179,181,198,0.2)',
                borderColor: 'rgba(179,181,198,1)',
                pointBackgroundColor: 'rgba(179,181,198,1)',
            }
        ]
    };

    return <Radar data={chartData} />;
};

export default HealthRadarChart;

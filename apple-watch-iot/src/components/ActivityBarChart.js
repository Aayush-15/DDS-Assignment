// src/components/ActivityBarChart.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';

const ActivityBarChart = () => {
    const [data, setData] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('http://localhost:4000/activity-tracking/device123'); // Replace with your device_id
                setData(response.data);
            } catch (error) {
                console.error('Error fetching activity data:', error);
            }
        };
        fetchData();
    }, []);

    const chartData = {
        labels: data.map(item => new Date(item.timestamp).toLocaleString()),
        datasets: [
            {
                label: 'Steps',
                data: data.filter(item => item.activity_type === 'walking').map(item => item.value),
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
            },
            {
                label: 'Distance (meters)',
                data: data.filter(item => item.activity_type === 'running').map(item => item.value),
                backgroundColor: 'rgba(153, 102, 255, 0.6)',
            }
        ]
    };

    return <Bar data={chartData} />;
};

export default ActivityBarChart;

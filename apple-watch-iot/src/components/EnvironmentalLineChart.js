// src/components/EnvironmentalLineChart.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';

const EnvironmentalLineChart = () => {
    const [data, setData] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('http://localhost:4000/environmental-data/device123'); // Replace with your device_id
                setData(response.data);
            } catch (error) {
                console.error('Error fetching environmental data:', error);
            }
        };
        fetchData();
    }, []);

    const chartData = {
        labels: data.map(item => new Date(item.timestamp).toLocaleString()),
        datasets: [
            {
                label: 'Temperature (°C)',
                data: data.filter(item => item.data_type === 'temperature').map(item => parseFloat(item.value)),
                borderColor: 'rgba(255, 99, 132, 1)',
                fill: false,
            },
            {
                label: 'Humidity (%)',
                data: data.filter(item => item.data_type === 'humidity').map(item => parseFloat(item.value)),
                borderColor: 'rgba(54, 162, 235, 1)',
                fill: false,
            }
        ]
    };

    return <Line data={chartData} />;
};

export default EnvironmentalLineChart;

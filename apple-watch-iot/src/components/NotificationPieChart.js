// src/components/NotificationPieChart.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Pie } from 'react-chartjs-2';

const NotificationPieChart = () => {
    const [data, setData] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('http://localhost:4000/notifications/device123'); // Replace with your device_id
                setData(response.data);
            } catch (error) {
                console.error('Error fetching notification data:', error);
            }
        };
        fetchData();
    }, []);

    const notificationCounts = data.reduce((acc, curr) => {
        acc[curr.notification_type] = (acc[curr.notification_type] || 0) + 1;
        return acc;
    }, {});

    const chartData = {
        labels: Object.keys(notificationCounts),
        datasets: [
            {
                data: Object.values(notificationCounts),
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
                hoverOffset: 4,
            }
        ]
    };

    return <Pie data={chartData} />;
};

export default NotificationPieChart;

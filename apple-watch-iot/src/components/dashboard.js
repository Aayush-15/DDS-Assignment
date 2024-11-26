// src/components/Dashboard.js
import React from 'react';
import ActivityBarChart from './ActivityBarChart';
import NotificationPieChart from './NotificationPieChart';
import EnvironmentalLineChart from './EnvironmentalLineChart';
import HealthRadarChart from './HealthRadarChart';

const Dashboard = () => {
    return (
        <div className="container mt-4">
            <h1 className="text-center">Apple Watch IoT Dashboard</h1>
            <div className="row">
                <div className="col-md-6">
                    <h3>Activity Tracking</h3>
                    <ActivityBarChart />
                </div>
                <div className="col-md-6">
                    <h3>Notifications</h3>
                    <NotificationPieChart />
                </div>
            </div>
            <div className="row mt-4">
                <div className="col-md-6">
                    <h3>Environmental Data</h3>
                    <EnvironmentalLineChart />
                </div>
                <div className="col-md-6">
                    <h3>Health Metrics</h3>
                    <HealthRadarChart />
                </div>
            </div>
        </div>
    );
};

export default Dashboard;

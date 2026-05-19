import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  RadialLinearScale,
  Filler
} from 'chart.js';
import { Doughnut, Bar, Line, Radar } from 'react-chartjs-2';

ChartJS.register(
  ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement,
  PointElement, LineElement, RadialLinearScale, Filler
);
ChartJS.defaults.color = '#666666';
ChartJS.defaults.font.family = "'Inter', sans-serif";

const commonOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: { usePointStyle: true, padding: 20, font: { size: 11, weight: '500' } }
    }
  }
};

const Dashboard = ({ data, modelMetrics, loadDashboard, generateReport, reportLoading }) => {
  const summary = useMemo(() => {
    let highRisk = 0;
    let lowRisk = 0;
    let totalSpend = 0;
    data.forEach(d => {
      if (d.risk_level === 'High') highRisk++;
      if (d.risk_level === 'Low') lowRisk++;
      totalSpend += parseFloat(d.total_spend || 0);
    });
    const avgSpend = data.length > 0 ? (totalSpend / data.length).toFixed(2) : 0;
    return { total: data.length, highRisk, lowRisk, avgSpend };
  }, [data]);

  const chartsData = useMemo(() => {
    let churn = 0, stay = 0;
    let risk = { 'High': 0, 'Medium': 0, 'Low': 0 };
    let subs = { 'Basic': 0, 'Standard': 0, 'Premium': 0 };

    const last7Days = [];
    const trends = {};
    for (let i = 6; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      const key = d.toLocaleDateString();
      last7Days.push(key);
      trends[key] = 0;
    }

    const parseDate = (dateStr) => {
      if (!dateStr) return new Date();
      const safeStr = dateStr.replace(/-/g, '/') + ' UTC';
      return new Date(safeStr);
    };

    data.forEach(d => {
      if (d.prediction === 'Likely to Churn') churn++; else stay++;
      if (risk[d.risk_level] !== undefined) risk[d.risk_level]++;
      if (subs[d.subscription_type] !== undefined) subs[d.subscription_type]++;
      const rowDate = parseDate(d.timestamp).toLocaleDateString();
      if (trends[rowDate] !== undefined) trends[rowDate]++;
    });

    const trendData = last7Days.map(date => trends[date]);

    return { churn, stay, risk, subs, last7Days, trendData };
  }, [data]);

  const pieData = {
    labels: ['Churn', 'Stay'],
    datasets: [{ data: [chartsData.churn, chartsData.stay], backgroundColor: ['#111111', '#E5E5E5'], borderWidth: 0, cutout: '80%' }]
  };

  const barData = {
    labels: ['High', 'Medium', 'Low'],
    datasets: [{ label: 'Customers', data: [chartsData.risk['High'], chartsData.risk['Medium'], chartsData.risk['Low']], backgroundColor: ['#111111', '#666666', '#E5E5E5'], borderRadius: 4 }]
  };

  const subData = {
    labels: ['Basic', 'Standard', 'Premium'],
    datasets: [{
      label: 'Subscribers',
      data: [chartsData.subs['Basic'], chartsData.subs['Standard'], chartsData.subs['Premium']],
      backgroundColor: 'rgba(0, 0, 0, 0.05)',
      borderColor: '#111111',
      borderWidth: 2,
      pointBackgroundColor: '#111111'
    }]
  };

  const trendLineData = {
    labels: chartsData.last7Days,
    datasets: [{
      label: 'Predictions',
      data: chartsData.trendData,
      borderColor: '#111111',
      backgroundColor: 'transparent',
      borderWidth: 2,
      tension: 0.3,
      pointBackgroundColor: '#111111',
      pointRadius: 4
    }]
  };

  return (
    <section id="dashboard" className="page active">
      <div className="page-header">
        <div>
          <h1>Customer Churn Analytics Dashboard</h1>
          <p className="subtitle">Real-time insights and predictive model performance metrics.</p>
        </div>
        <div className="header-actions">
          <div className="filter-bar">
            <label htmlFor="modelFilter"><i className="fa-solid fa-filter"></i> Filter by Model</label>
            <select id="modelFilter" onChange={(e) => loadDashboard(e.target.value)}>
              <option value="">All Models</option>
              <option value="Logistic Regression">Logistic Regression</option>
              <option value="KNN">KNN</option>
              <option value="Naive Bayes">Naive Bayes</option>
              <option value="SVM">SVM</option>
            </select>
          </div>
          <button className="btn-primary" onClick={generateReport} disabled={reportLoading}>
            <i className="fa-solid fa-file-pdf"></i>
            <span>Export Report</span>
            {reportLoading && <div className="loader" style={{ width: '14px', height: '14px', borderWidth: '2px', borderTopColor: 'white' }}></div>}
          </button>
          <button className="btn-secondary" onClick={() => loadDashboard()}>
            <i className="fa-solid fa-arrows-rotate"></i>
          </button>
        </div>
      </div>

      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon"><i className="fa-solid fa-users"></i></div>
          <div className="kpi-content">
            <span className="kpi-label">Total Predictions</span>
            <h2 className="kpi-value">{summary.total}</h2>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon dark"><i className="fa-solid fa-user-minus"></i></div>
          <div className="kpi-content">
            <span className="kpi-label">High Risk</span>
            <h2 className="kpi-value">{summary.highRisk}</h2>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon light"><i className="fa-solid fa-user-check"></i></div>
          <div className="kpi-content">
            <span className="kpi-label">Safe Customers</span>
            <h2 className="kpi-value">{summary.lowRisk}</h2>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon border"><i className="fa-solid fa-wallet"></i></div>
          <div className="kpi-content">
            <span className="kpi-label">Avg. Monthly Spend</span>
            <h2 className="kpi-value">${summary.avgSpend}</h2>
          </div>
        </div>
      </div>

      <div className="section-title">
        <h3><i className="fa-solid fa-microchip"></i> Model Performance Comparison</h3>
      </div>
      <div className="metrics-grid">
        {modelMetrics?.models && Object.entries(modelMetrics.models).map(([modelName, metrics]) => {
          const acc = `${Math.round(metrics.accuracy * 100)}%`;
          const isBest = modelName === modelMetrics.best_model;
          return (
            <div key={modelName} className="kpi-card" style={isBest ? { borderColor: '#111111', boxShadow: '0 4px 16px rgba(0,0,0,0.12)' } : {}}>
              <div className={`kpi-icon ${isBest ? 'dark' : 'border'}`}>
                <i className="fa-solid fa-microchip"></i>
              </div>
              <div className="kpi-content">
                <span className="kpi-label">{modelName} Accuracy {isBest ? '⭐' : ''}</span>
                <h2 className="kpi-value">{acc}</h2>
              </div>
            </div>
          );
        })}
      </div>

      <div className="dashboard-grid">
        <div className="card chart-card">
          <div className="card-header">
            <h4>Churn Distribution</h4>
            <i className="fa-solid fa-circle-info hint"></i>
          </div>
          <div className="chart-box">
            <Doughnut data={pieData} options={commonOptions} />
          </div>
        </div>
        <div className="card chart-card">
          <div className="card-header">
            <h4>Risk Level Analysis</h4>
            <i className="fa-solid fa-circle-info hint"></i>
          </div>
          <div className="chart-box">
            <Bar data={barData} options={{ ...commonOptions, plugins: { legend: { display: false } }, scales: { y: { grid: { color: '#F5F5F5' } }, x: { grid: { display: false } } } }} />
          </div>
        </div>
        <div className="card chart-card">
          <div className="card-header">
            <h4>Subscription Tier Breakdown</h4>
            <i className="fa-solid fa-circle-info hint"></i>
          </div>
          <div className="chart-box">
            <Radar data={subData} options={{ ...commonOptions, scales: { r: { grid: { color: '#E5E5E5' }, ticks: { display: false }, pointLabels: { font: { weight: '600' } } } } }} />
          </div>
        </div>
        <div className="card chart-card">
          <div className="card-header">
            <h4>Prediction Trends</h4>
            <i className="fa-solid fa-circle-info hint"></i>
          </div>
          <div className="chart-box">
            <Line data={trendLineData} options={{ ...commonOptions, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: '#F5F5F5' } }, x: { grid: { display: false } } } }} />
          </div>
        </div>
      </div>
    </section>
  );
};

export default Dashboard;

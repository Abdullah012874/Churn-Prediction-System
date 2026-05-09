// API Configuration
const API_URL = 'http://localhost:5000';

// Global Chart Instances
let churnPieChart = null;
let riskBarChart = null;
let subChart = null;
let trendChart = null;

// UI Helpers
function showPage(pageId, event) {
    if (event) event.preventDefault();
    
    // Manage active states for pages
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    document.querySelectorAll('.nav-links a').forEach(link => link.classList.remove('active'));
    
    document.getElementById(pageId).classList.add('active');
    
    const activeLink = document.querySelector(`.nav-links a[onclick*="${pageId}"]`);
    if (activeLink) activeLink.classList.add('active');

    // Close mobile menu if open
    document.querySelector('.nav-links').classList.remove('show');

    // Trigger dashboard data fetch
    if (pageId === 'dashboard') {
        loadDashboard();
    }
}

function toggleMobileMenu() {
    document.querySelector('.nav-links').classList.toggle('show');
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const msgEl = document.getElementById('toastMsg');
    const iconEl = toast.querySelector('.toast-icon');
    
    toast.className = `toast ${type}`;
    msgEl.textContent = message;
    
    if (type === 'error') {
        iconEl.className = 'fa-solid fa-circle-xmark toast-icon';
    } else {
        iconEl.className = 'fa-solid fa-circle-check toast-icon';
    }
    
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

// Prediction Logic
async function handlePredict(event) {
    event.preventDefault();
    
    const form = document.getElementById('predictionForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    const btn = document.getElementById('predictBtn');
    const spinner = document.getElementById('predictSpinner');
    const icon = btn.querySelector('.fa-wand-magic-sparkles');
    
    btn.disabled = true;
    spinner.classList.remove('hidden');
    if (icon) icon.classList.add('hidden');

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('API Error');

        const result = await response.json();
        renderResult(result);
        showPage('result');
        showToast('Prediction generated successfully!');

    } catch (error) {
        console.error(error);
        showToast('Error connecting to server. Is the API running?', 'error');
    } finally {
        btn.disabled = false;
        spinner.classList.add('hidden');
        if (icon) icon.classList.remove('hidden');
        form.reset();
    }
}

function renderResult(result) {
    document.getElementById('resultTitle').textContent = result.prediction;
    
    // Badge Setup
    const badge = document.getElementById('riskBadge');
    badge.textContent = `${result.risk_level} Risk`;
    badge.className = `result-badge badge-${result.risk_level.toLowerCase()}`;
    
    // Animated Progress Circle
    const probPercent = Math.round(result.probability * 100);
    const probText = document.getElementById('probText');
    const circle = document.getElementById('probCircle');
    const trend = document.getElementById('trendIndicator');
    
    let color = '#10b981'; // Green
    trend.innerHTML = `<i class="fa-solid fa-arrow-trend-up"></i> Customer is stable`;
    trend.style.color = color;

    if (result.risk_level === 'High') {
        color = '#ef4444'; // Red
        trend.innerHTML = `<i class="fa-solid fa-arrow-trend-down"></i> Immediate action required`;
        trend.style.color = color;
    } else if (result.risk_level === 'Medium') {
        color = '#f59e0b'; // Yellow
        trend.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> Monitor closely`;
        trend.style.color = color;
    }
    
    // Animate Number and Circle
    let currentVal = 0;
    probText.textContent = `0%`;
    circle.style.background = `conic-gradient(${color} 0%, rgba(255,255,255,0.05) 0%)`;

    const interval = setInterval(() => {
        if (currentVal >= probPercent) {
            clearInterval(interval);
            return;
        }
        currentVal++;
        probText.textContent = `${currentVal}%`;
        circle.style.background = `conic-gradient(${color} ${currentVal}%, rgba(255,255,255,0.05) 0%)`;
    }, 15);

    // Render Suggestions
    const list = document.getElementById('suggestionsList');
    list.innerHTML = '';
    result.suggestions.forEach(sugg => {
        const div = document.createElement('div');
        div.className = 'suggestion-card';
        div.innerHTML = `
            <div class="sugg-icon"><i class="fa-solid fa-lightbulb"></i></div>
            <div class="sugg-text">
                <p>${sugg}</p>
            </div>
        `;
        list.appendChild(div);
    });
}

// Dashboard Logic
async function loadDashboard() {
    try {
        const response = await fetch(`${API_URL}/api/history`);
        if (!response.ok) throw new Error('Failed to fetch dashboard data');
        
        const data = await response.json();
        
        updateSummaryCards(data);
        renderTable(data);
        renderCharts(data);
        
    } catch (error) {
        console.error(error);
        showToast('Failed to sync dashboard', 'error');
    }
}

function updateSummaryCards(data) {
    const total = data.length;
    let highRisk = 0;
    let lowRisk = 0;
    let totalSpend = 0;

    data.forEach(d => {
        if (d.risk_level === 'High') highRisk++;
        if (d.risk_level === 'Low') lowRisk++;
        totalSpend += parseFloat(d.total_spend || 0);
    });

    const avgSpend = total > 0 ? (totalSpend / total).toFixed(2) : 0;

    document.getElementById('totalPreds').textContent = total;
    document.getElementById('highRiskPreds').textContent = highRisk;
    document.getElementById('lowRiskPreds').textContent = lowRisk;
    document.getElementById('avgSpend').textContent = `$${avgSpend}`;
}

// Safely parse SQLite date (YYYY-MM-DD HH:MM:SS) for cross-browser support
function parseDate(dateStr) {
    if (!dateStr) return new Date();
    // Replace '-' with '/' to fix Safari/iOS parsing issues and append ' UTC' to convert to local time
    const safeStr = dateStr.replace(/-/g, '/') + ' UTC';
    return new Date(safeStr);
}

function renderTable(data) {
    const tbody = document.querySelector('#historyTable tbody');
    tbody.innerHTML = '';
    
    // Show only the latest 8 for brevity
    data.slice(0, 8).forEach(row => { 
        const d = parseDate(row.timestamp);
        const dateStr = `${d.toLocaleDateString()} ${d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${dateStr}</td>
            <td>Age ${row.age} / ${row.gender}</td>
            <td>$${row.total_spend} / ${row.subscription_type}</td>
            <td><strong>${row.prediction}</strong></td>
            <td><span class="badge-sm badge-${row.risk_level.toLowerCase()}">${row.risk_level}</span></td>
            <td><button class="action-btn" onclick="deleteRecord(${row.id})" title="Delete Record"><i class="fa-solid fa-trash"></i></button></td>
        `;
        tbody.appendChild(tr);
    });
}

async function deleteRecord(id) {
    if (!confirm('Permanently delete this record?')) return;
    
    try {
        const response = await fetch(`${API_URL}/api/history/${id}`, { method: 'DELETE' });
        if (response.ok) {
            showToast('Record deleted successfully');
            loadDashboard();
        }
    } catch (error) {
        console.error(error);
        showToast('Failed to delete record', 'error');
    }
}

function renderCharts(data) {
    // 1. Process Data
    let churn = 0, stay = 0;
    let risk = { 'High': 0, 'Medium': 0, 'Low': 0 };
    let subs = { 'Basic': 0, 'Standard': 0, 'Premium': 0 };
    
    // Group by Date for Trends
    let trends = {};
    const last7Days = [];
    for (let i = 6; i >= 0; i--) {
        const d = new Date();
        d.setDate(d.getDate() - i);
        const dateKey = d.toLocaleDateString();
        last7Days.push(dateKey);
        trends[dateKey] = 0;
    }

    data.forEach(d => {
        // Churn
        if (d.prediction === 'Likely to Churn') churn++; else stay++;
        // Risk
        if (risk[d.risk_level] !== undefined) risk[d.risk_level]++;
        // Subscription
        if (subs[d.subscription_type] !== undefined) subs[d.subscription_type]++;
        // Trend
        const rowDate = parseDate(d.timestamp).toLocaleDateString();
        if (trends[rowDate] !== undefined) trends[rowDate]++;
    });

    const trendData = last7Days.map(date => trends[date]);

    // 2. Safely Destroy Existing Charts
    if (churnPieChart) churnPieChart.destroy();
    if (riskBarChart) riskBarChart.destroy();
    if (subChart) subChart.destroy();
    if (trendChart) trendChart.destroy();

    // 3. Global Chart Settings
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = "'Outfit', sans-serif";
    const commonOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#f8fafc' } } } };

    // Churn Doughnut
    const ctxPie = document.getElementById('churnPieChart').getContext('2d');
    churnPieChart = new Chart(ctxPie, {
        type: 'doughnut',
        data: {
            labels: ['Churn', 'Stay'],
            datasets: [{ data: [churn, stay], backgroundColor: ['#ef4444', '#10b981'], borderWidth: 0, cutout: '70%' }]
        },
        options: commonOptions
    });

    // Risk Bar
    const ctxBar = document.getElementById('riskBarChart').getContext('2d');
    riskBarChart = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: ['High', 'Medium', 'Low'],
            datasets: [{ label: 'Customers', data: [risk['High'], risk['Medium'], risk['Low']], backgroundColor: ['#ef4444', '#f59e0b', '#10b981'], borderRadius: 6 }]
        },
        options: { ...commonOptions, plugins: { legend: { display: false } }, scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } } }
    });

    // Subscription Polar Area
    const ctxSub = document.getElementById('subChart').getContext('2d');
    subChart = new Chart(ctxSub, {
        type: 'polarArea',
        data: {
            labels: ['Basic', 'Standard', 'Premium'],
            datasets: [{ data: [subs['Basic'], subs['Standard'], subs['Premium']], backgroundColor: ['rgba(59, 130, 246, 0.7)', 'rgba(139, 92, 246, 0.7)', 'rgba(236, 72, 153, 0.7)'], borderWidth: 0 }]
        },
        options: { ...commonOptions, scales: { r: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { display: false } } } }
    });

    // Trend Line Chart
    const ctxTrend = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(ctxTrend, {
        type: 'line',
        data: {
            labels: last7Days,
            datasets: [{
                label: 'Predictions',
                data: trendData,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#8b5cf6',
                pointRadius: 4
            }]
        },
        options: { ...commonOptions, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } } }
    });
}

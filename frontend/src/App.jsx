import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import PredictForm from './components/PredictForm';
import PredictionResult from './components/PredictionResult';
import PredictionHistory from './components/PredictionHistory';
import Toast from './components/Toast';
import { fetchHistory, fetchModelComparison, predictChurn, generateReportAPI, generateSpecificReportAPI, clearHistoryAPI, deleteRecordAPI } from './services/api';

function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [toast, setToast] = useState({ message: '', type: 'success', isVisible: false });

  // Data states
  const [historyData, setHistoryData] = useState([]);
  const [modelMetrics, setModelMetrics] = useState(null);
  const [predictionResult, setPredictionResult] = useState(null);

  // Loading states
  const [predictLoading, setPredictLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);

  const showToast = (message, type = 'success') => {
    setToast({ message, type, isVisible: true });
    setTimeout(() => setToast((prev) => ({ ...prev, isVisible: false })), 3500);
  };

  const loadDashboard = async (modelFilter = '') => {
    try {
      const history = await fetchHistory(modelFilter);
      setHistoryData(history);
      const metrics = await fetchModelComparison();
      setModelMetrics(metrics);
    } catch (error) {
      console.error(error);
      showToast('Failed to sync dashboard', 'error');
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const handlePredict = async (data) => {
    if (!data.selected_model) {
      showToast('Please select a prediction model before submitting.', 'error');
      return;
    }
    setPredictLoading(true);
    try {
      const result = await predictChurn(data);
      setPredictionResult(result);
      await loadDashboard(); // refresh metrics/history after prediction
      setActivePage('result');
      showToast('Prediction generated successfully!');
    } catch (error) {
      console.error(error);
      showToast(error.response?.data?.error || 'Error connecting to server. Is the API running?', 'error');
    } finally {
      setPredictLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    setReportLoading(true);
    try {
      const blob = await generateReportAPI();
      const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = 'Churn_Prediction_Report.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      showToast('Report downloaded successfully!');
    } catch (error) {
      console.error(error);
      showToast('Failed to generate report', 'error');
    } finally {
      setReportLoading(false);
    }
  };

  const handleGenerateSpecificReport = async (id) => {
    // Optionally use the same global reportLoading or a new state.
    // For simplicity, just use setReportLoading since it locks the UI appropriately.
    setReportLoading(true);
    try {
      const blob = await generateSpecificReportAPI(id);
      const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = `Churn_Prediction_Report_${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      showToast('Specific report downloaded successfully!');
    } catch (error) {
      console.error(error);
      showToast('Failed to generate specific report', 'error');
    } finally {
      setReportLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (!window.confirm('Are you sure you want to permanently delete ALL history?')) return;
    try {
      await clearHistoryAPI();
      showToast('All history cleared successfully');
      loadDashboard();
    } catch (error) {
      console.error(error);
      showToast('Failed to clear history', 'error');
    }
  };

  const handleDeleteRecord = async (id) => {
    if (!window.confirm('Permanently delete this record?')) return;
    try {
      await deleteRecordAPI(id);
      showToast('Record deleted successfully');
      loadDashboard();
    } catch (error) {
      console.error(error);
      showToast('Failed to delete record', 'error');
    }
  };

  const toggleMobileSidebar = () => {
    setIsMobileOpen(!isMobileOpen);
  };

  return (
    <>
      <Sidebar
        activePage={activePage}
        setActivePage={setActivePage}
        isMobileOpen={isMobileOpen}
        toggleMobileSidebar={toggleMobileSidebar}
        generateReport={handleGenerateReport}
        reportLoading={reportLoading}
      />
      <main className="main-content">
        {activePage === 'dashboard' && (
          <Dashboard
            data={historyData}
            modelMetrics={modelMetrics}
            loadDashboard={loadDashboard}
            generateReport={handleGenerateReport}
            reportLoading={reportLoading}
          />
        )}
        {activePage === 'predict' && (
          <PredictForm
            handlePredict={handlePredict}
            predictLoading={predictLoading}
          />
        )}
        {activePage === 'result' && (
          <PredictionResult
            result={predictionResult}
            modelMetrics={modelMetrics}
            setActivePage={setActivePage}
          />
        )}
        {activePage === 'history' && (
          <PredictionHistory
            data={historyData}
            clearAllHistory={handleClearHistory}
            deleteRecord={handleDeleteRecord}
            generateSpecificReport={handleGenerateSpecificReport}
          />
        )}
      </main>
      <Toast message={toast.message} type={toast.type} isVisible={toast.isVisible} />
    </>
  );
}

export default App;

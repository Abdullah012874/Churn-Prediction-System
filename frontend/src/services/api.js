import axios from 'axios';

const API_URL = 'http://localhost:5000';

export const fetchHistory = async (modelFilter = '') => {
  const url = modelFilter
    ? `${API_URL}/api/history?model=${encodeURIComponent(modelFilter)}`
    : `${API_URL}/api/history`;
  const response = await axios.get(url);
  return response.data;
};

export const fetchModelComparison = async () => {
  const response = await axios.get(`${API_URL}/model-comparison`);
  return response.data;
};

export const predictChurn = async (data) => {
  const response = await axios.post(`${API_URL}/predict`, data);
  return response.data;
};

export const generateReportAPI = async () => {
  const response = await axios.get(`${API_URL}/generate-report`, {
    responseType: 'blob'
  });
  return response.data;
};

export const clearHistoryAPI = async () => {
  const response = await axios.delete(`${API_URL}/api/history/clear`);
  return response.data;
};

export const deleteRecordAPI = async (id) => {
  const response = await axios.delete(`${API_URL}/api/history/${id}`);
  return response.data;
};

export const generateSpecificReportAPI = async (id) => {
  const response = await axios.get(`${API_URL}/generate-report/${id}`, {
    responseType: 'blob'
  });
  return response.data;
};


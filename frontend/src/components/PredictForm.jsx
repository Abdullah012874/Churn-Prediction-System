import React, { useState } from 'react';

const PredictForm = ({ handlePredict, predictLoading }) => {
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    tenure: '',
    subscription_type: '',
    contract_length: '',
    usage_frequency: '',
    support_calls: '',
    payment_delay: '',
    total_spend: '',
    last_interaction: '',
  });

  const [selectedModel, setSelectedModel] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const onSubmit = (e) => {
    e.preventDefault();
    handlePredict({ ...formData, selected_model: selectedModel });
  };

  const models = [
    { name: 'Logistic Regression', desc: 'Linear probabilistic classifier', icon: 'fa-chart-line' },
    { name: 'KNN', desc: 'K-Nearest Neighbours', icon: 'fa-share-nodes' },
    { name: 'Naive Bayes', desc: 'Probabilistic Bayes classifier', icon: 'fa-atom' },
    { name: 'SVM', desc: 'Support Vector Machine', icon: 'fa-vector-square' }
  ];

  return (
    <section id="predict" className="page active">
      <div className="page-header centered">
        <h1>Churn Risk Assessment</h1>
        <p className="subtitle">Input customer behavior metrics for deep behavioral analysis.</p>
      </div>

      <div className="form-container">
        <form id="predictionForm" className="card" onSubmit={onSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label>Age</label>
              <input type="number" name="age" required min="18" max="100" placeholder="e.g. 30" value={formData.age} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Gender</label>
              <select name="gender" required value={formData.gender} onChange={handleChange}>
                <option value="" disabled>Select Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
            </div>
            <div className="form-group">
              <label>Tenure (Months)</label>
              <input type="number" name="tenure" required min="0" placeholder="e.g. 12" value={formData.tenure} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Subscription Tier</label>
              <select name="subscription_type" required value={formData.subscription_type} onChange={handleChange}>
                <option value="" disabled>Select Tier</option>
                <option value="Basic">Basic</option>
                <option value="Standard">Standard</option>
                <option value="Premium">Premium</option>
              </select>
            </div>
            <div className="form-group">
              <label>Contract Type</label>
              <select name="contract_length" required value={formData.contract_length} onChange={handleChange}>
                <option value="" disabled>Select Contract</option>
                <option value="Monthly">Monthly</option>
                <option value="Quarterly">Quarterly</option>
                <option value="Annual">Annual</option>
              </select>
            </div>
            <div className="form-group">
              <label>Usage Frequency (Days/Month)</label>
              <input type="number" name="usage_frequency" required min="0" max="31" placeholder="e.g. 15" value={formData.usage_frequency} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Support Calls</label>
              <input type="number" name="support_calls" required min="0" placeholder="e.g. 2" value={formData.support_calls} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Payment Delay (Days)</label>
              <input type="number" name="payment_delay" required min="0" placeholder="e.g. 0" value={formData.payment_delay} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Total Spend ($)</label>
              <input type="number" name="total_spend" required min="0" step="0.01" placeholder="e.g. 450.00" value={formData.total_spend} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label>Last Interaction (Days Ago)</label>
              <input type="number" name="last_interaction" required min="0" placeholder="e.g. 3" value={formData.last_interaction} onChange={handleChange} />
            </div>
          </div>

          <div className="model-selector-section">
            <div className="model-selector-header">
              <i className="fa-solid fa-microchip"></i>
              <span>Select Prediction Model</span>
              <span className="model-required-badge">Required</span>
            </div>
            <div className="model-selector" role="radiogroup" aria-label="Select a prediction model">
              {models.map(m => (
                <div
                  key={m.name}
                  className={`model-card ${selectedModel === m.name ? 'selected' : ''}`}
                  onClick={() => setSelectedModel(m.name)}
                  onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setSelectedModel(m.name); } }}
                  tabIndex="0"
                  role="radio"
                  aria-checked={selectedModel === m.name}
                >
                  <div className="model-card-icon"><i className={`fa-solid ${m.icon}`}></i></div>
                  <div className="model-card-body">
                    <span className="model-card-name">{m.name}</span>
                    <span className="model-card-desc">{m.desc}</span>
                  </div>
                  <div className="model-card-check"><i className="fa-solid fa-circle-check"></i></div>
                </div>
              ))}
            </div>
          </div>

          <div className="form-footer">
            <button type="submit" className="btn-primary large" disabled={predictLoading}>
              <span className={`btn-text ${predictLoading ? 'hidden' : ''}`}>Analyze Risk <i className="fa-solid fa-magnifying-glass-chart"></i></span>
              {predictLoading && <div className="loader"></div>}
            </button>
          </div>
        </form>
      </div>
    </section>
  );
};

export default PredictForm;

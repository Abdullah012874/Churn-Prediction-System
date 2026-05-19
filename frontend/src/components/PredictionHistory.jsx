import React from 'react';

const PredictionHistory = ({ data, clearAllHistory, deleteRecord, generateSpecificReport }) => {
  const parseDate = (dateStr) => {
    if (!dateStr) return new Date();
    const safeStr = dateStr.replace(/-/g, '/') + ' UTC';
    return new Date(safeStr);
  };

  return (
    <section id="history" className="page active">
      <div className="page-header">
        <div>
          <h1>Prediction History</h1>
          <p className="subtitle">Review and manage all historical risk assessments.</p>
        </div>
        <div className="header-actions">
          <button className="btn-secondary danger" onClick={clearAllHistory}>
            <i className="fa-solid fa-trash-can"></i> Clear All
          </button>
        </div>
      </div>

      <div className="card table-card">
        <div className="table-responsive">
          <table id="historyTable">
            <thead>
              <tr>
                <th>Date</th>
                <th>Customer Profile</th>
                <th>Subscription</th>
                <th>Model Used</th>
                <th>Prediction</th>
                <th>Risk Level</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {data.slice(0, 10).map((row, index) => {
                const d = parseDate(row.timestamp);
                const dateStr = d.toLocaleDateString();
                const model = row.selected_model || row.used_model || 'Unknown';

                return (
                  <tr key={row.id || index}>
                    <td>{dateStr}</td>
                    <td>Age {row.age || '?'} / {row.gender || '?'}</td>
                    <td>{row.subscription_type || '?'}</td>
                    <td><span className="model-tag">{model}</span></td>
                    <td><strong>{row.prediction || '?'}</strong></td>
                    <td>
                      <span className={`badge-sm badge-${(row.risk_level || 'low').toLowerCase()}`}>
                        {row.risk_level || '?'}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                        <button className="action-btn" onClick={() => generateSpecificReport(row.id)} title="Download PDF Report" style={{ color: '#111111' }}>
                          <i className="fa-solid fa-file-pdf"></i>
                        </button>
                        <button className="action-btn" onClick={() => deleteRecord(row.id)} title="Delete">
                          <i className="fa-solid fa-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
              {data.length === 0 && (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '2rem' }}>No history available.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};

export default PredictionHistory;

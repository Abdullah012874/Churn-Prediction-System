import React from 'react';

const Sidebar = ({ activePage, setActivePage, isMobileOpen, toggleMobileSidebar, generateReport, reportLoading }) => {
  return (
    <>
      <aside className={`sidebar ${isMobileOpen ? 'active' : ''}`} id="sidebar">
        <div className="sidebar-logo">
          <div className="logo-box">
            <i className="fa-solid fa-brain"></i>
          </div>
          <span className="logo-text">Churn AI</span>
        </div>

        <nav className="sidebar-nav">
          <ul>
            <li>
              <a
                href="#"
                onClick={(e) => { e.preventDefault(); setActivePage('dashboard'); toggleMobileSidebar(); }}
                className={`nav-item ${activePage === 'dashboard' ? 'active' : ''}`}
              >
                <i className="fa-solid fa-chart-pie"></i>
                <span>Dashboard</span>
              </a>
            </li>
            <li>
              <a
                href="#"
                onClick={(e) => { e.preventDefault(); setActivePage('predict'); toggleMobileSidebar(); }}
                className={`nav-item ${activePage === 'predict' ? 'active' : ''}`}
              >
                <i className="fa-solid fa-wand-magic-sparkles"></i>
                <span>Predict Churn</span>
              </a>
            </li>
            <li>
              <a
                href="#"
                onClick={(e) => { e.preventDefault(); setActivePage('history'); toggleMobileSidebar(); }}
                className={`nav-item ${activePage === 'history' ? 'active' : ''}`}
              >
                <i className="fa-solid fa-clock-rotate-left"></i>
                <span>Prediction History</span>
              </a>
            </li>
            <li>
              <a
                href="#"
                onClick={(e) => { e.preventDefault(); generateReport(); }}
                className="nav-item report-link"
              >
                <i className="fa-solid fa-file-pdf"></i>
                <span>Generate Report</span>
                {reportLoading && (
                  <div className="loader" style={{ width: '14px', height: '14px', borderWidth: '2px', borderTopColor: 'var(--text-secondary)', marginLeft: '10px' }}></div>
                )}
              </a>
            </li>
          </ul>
        </nav>

        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="user-avatar">AT</div>
            <div className="user-info">
              <span className="user-name">Abdullah Tanveer</span>
              <span className="user-role">Administrator</span>
            </div>
          </div>
        </div>
      </aside>

      <header className="mobile-header">
        <button className="menu-toggle" onClick={toggleMobileSidebar}>
          <i className="fa-solid fa-bars"></i>
        </button>
        <span className="mobile-logo">Churn AI</span>
        <div className="user-avatar-sm">AT</div>
      </header>
    </>
  );
};

export default Sidebar;

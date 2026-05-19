import React from 'react';

const Toast = ({ message, type, isVisible }) => {
  return (
    <div className={`toast ${type} ${isVisible ? 'show' : ''}`}>
      <i
        className={
          type === 'error'
            ? 'fa-solid fa-circle-xmark toast-icon'
            : 'fa-solid fa-circle-check toast-icon'
        }
      ></i>
      <span>{message}</span>
    </div>
  );
};

export default Toast;

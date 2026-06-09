import React from 'react';
import './GuestBanner.css';

const GuestBanner = ({ remainingMessages, maxMessages, onLogin }) => {
  const percentage = (remainingMessages / maxMessages) * 100;

  return (
    <div className="guest-banner">
      <div className="guest-banner-content">
        <div className="guest-icon">👤</div>
        <div className="guest-info">
          <div className="guest-title">Guest Mode</div>
          <div className="guest-message-count">
            {remainingMessages} of {maxMessages} messages remaining
          </div>
        </div>
        <button onClick={onLogin} className="guest-login-btn">
          Sign up → 
        </button>
      </div>
      <div className="guest-progress-bar">
        <div 
          className="guest-progress-fill" 
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default GuestBanner;
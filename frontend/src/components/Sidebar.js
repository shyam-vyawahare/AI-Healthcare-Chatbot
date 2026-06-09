import React, { useState, useEffect } from 'react';
import './Sidebar.css';

const Sidebar = ({ isOpen, onClose, user, onLogout, onNavigate }) => {
  const [chatHistory, setChatHistory] = useState({});
  const [activeTab, setActiveTab] = useState('chat');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (user && isOpen && activeTab === 'chat') {
      fetchChatHistory();
    }
  }, [user, isOpen, activeTab]);

  const fetchChatHistory = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:5000/api/auth/chat-history', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await response.json();
      setChatHistory(data.history || {});
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const sortedDates = Object.keys(chatHistory).sort().reverse();

  return (
    <>
      <div className={`sidebar-overlay ${isOpen ? 'open' : ''}`} onClick={onClose} />
      <div className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <span className="logo-icon">⌘</span>
            <span className="logo-text">AarogyaAI</span>
          </div>
          <button className="sidebar-close" onClick={onClose}>×</button>
        </div>

        <div className="sidebar-tabs">
          <button 
            className={`sidebar-tab ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            Profile
          </button>
          <button 
            className={`sidebar-tab ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            History
          </button>
        </div>

        <div className="sidebar-content">
          {activeTab === 'profile' && user && (
            <div className="profile-section">
              <div className="profile-avatar">
                {user.name ? user.name[0].toUpperCase() : user.email[0].toUpperCase()}
              </div>
              <div className="profile-name">{user.name || 'User'}</div>
              <div className="profile-email">{user.email}</div>
              <div className="profile-details">
                {user.age && <div className="profile-detail">Age: {user.age}</div>}
                {user.gender && <div className="profile-detail">Gender: {user.gender}</div>}
                <div className="profile-detail">Member since: {new Date().getFullYear()}</div>
              </div>
              <button onClick={onLogout} className="logout-btn">
                Sign out
              </button>
            </div>
          )}

          {activeTab === 'chat' && (
            <div className="history-section">
              <div className="history-header">
                <h3>Chat History</h3>
              </div>
              {isLoading ? (
                <div className="history-loading">Loading...</div>
              ) : sortedDates.length === 0 ? (
                <div className="history-empty">No chat history yet</div>
              ) : (
                <div className="history-list">
                  {sortedDates.map(date => (
                    <div key={date} className="history-group">
                      <div className="history-date">{date}</div>
                      {chatHistory[date].map((chat, idx) => (
                        <div 
                          key={chat.id || idx} 
                          className="history-item"
                          onClick={() => onNavigate(chat)}
                        >
                          <div className="history-question">
                            {chat.user_message?.slice(0, 50)}...
                          </div>
                          <div className="history-time">
                            {new Date(chat.timestamp).toLocaleTimeString()}
                          </div>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Sidebar;
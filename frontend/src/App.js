import React, { useState, useEffect } from 'react';
import ChatInterfaceNew from './components/ChatInterfaceNew';
import DiseasePanel from './components/DiseasePanel';
import QuickButtons from './components/QuickButtons';
import HomePage from './HomePage';
import TeamPage from './TeamPage';
import Login from './components/Auth/Login';
import Signup from './components/Auth/Signup';
import Sidebar from './components/Sidebar';
import GuestBanner from './components/GuestBanner';
import { AuthProvider, useAuth } from './context/AuthContext';
import './App.css';

const AppContent = () => {
  const { 
    user, 
    isAuthenticated, 
    isGuest,
    guestMessageCount,
    guestMaxMessages,
    logout,
    incrementGuestMessage,
    checkGuestLimit,
    createGuestSession,
    currentPage,
    selectedLanguage,
    setSelectedLanguage,
    messages,
    addMessage,
    clearMessages,
    navigateTo,
    sessionId
  } = useAuth();
  
  const [showDiseasePanel, setShowDiseasePanel] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [canSendMessage, setCanSendMessage] = useState(true);

  useEffect(() => {
    // Restore sidebar state from localStorage
    const savedSidebarState = localStorage.getItem('sidebarOpen');
    if (savedSidebarState === 'true') {
      setIsSidebarOpen(true);
    }
  }, []);

  // Save sidebar state
  useEffect(() => {
    localStorage.setItem('sidebarOpen', isSidebarOpen);
  }, [isSidebarOpen]);

  useEffect(() => {
    if (isGuest) {
      checkGuestLimit().then(result => {
        setCanSendMessage(result.canChat);
      });
    } else {
      setCanSendMessage(true);
    }
  }, [isGuest, guestMessageCount]);

  const handleStartGuestChat = async () => {
    if (!localStorage.getItem('guestId')) {
      await createGuestSession();
    }
    navigateTo('chat');
  };

  const handleOpenLogin = () => {
    navigateTo('login');
  };

  const handleOpenSignup = () => {
    navigateTo('signup');
  };

  const handleAuthSuccess = () => {
    navigateTo('chat');
  };

  const handleBackToHome = () => {
    clearMessages();
    navigateTo('home');
  };

  const handleSendMessage = async () => {
    if (isGuest && guestMessageCount >= guestMaxMessages) {
      navigateTo('login');
      return false;
    }
    
    if (isGuest) {
      const result = await incrementGuestMessage();
      if (!result.canChat) {
        navigateTo('login');
        return false;
      }
    }
    return true;
  };

  // Page routing based on persisted state
  if (currentPage === 'login') {
    return <Login onSwitchToSignup={handleOpenSignup} onSuccess={handleAuthSuccess} onBack={handleBackToHome} />;
  }

  if (currentPage === 'signup') {
    return <Signup onSwitchToLogin={handleOpenLogin} onSuccess={handleAuthSuccess} onBack={handleBackToHome} />;
  }

  if (currentPage === 'team') {
    return <TeamPage onBack={handleBackToHome} />;
  }

  if (currentPage === 'home') {
    return (
      <HomePage 
        onStartGuestChat={handleStartGuestChat}
        onOpenLogin={handleOpenLogin}
        onOpenSignup={handleOpenSignup}
        onOpenTeam={() => navigateTo('team')}
      />
    );
  }

  // Chat interface
  return (
    <div className="app-container">
      <Sidebar 
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        user={user}
        onLogout={() => {
          logout();
          navigateTo('home');
        }}
        onNavigate={(chat) => {
          console.log('Navigate to chat:', chat);
          setIsSidebarOpen(false);
        }}
      />

      <header className="app-header">
        <div className="header-content">
          <button className="menu-btn" onClick={() => setIsSidebarOpen(true)}>
            ☰
          </button>
          <div className="logo-section" onClick={handleBackToHome} style={{ cursor: 'pointer' }}>
            <div className="logo-icon">⌘</div>
            <div className="logo-text">
              <h1>AarogyaAI</h1>
            </div>
          </div>
          
          <div className="header-actions">
            <select 
              className="language-selector"
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
            >
              <option value="en">English</option>
              <option value="hi">हिन्दी</option>
              <option value="mr">मराठी</option>
              <option value="ta">தமிழ்</option>
              <option value="te">తెలుగు</option>
              <option value="bn">বাংলা</option>
            </select>
            
            <button 
              className={`disease-btn ${showDiseasePanel ? 'active' : ''}`}
              onClick={() => setShowDiseasePanel(!showDiseasePanel)}
            >
              Info
            </button>
            
            <button 
              className="team-nav-btn"
              onClick={() => navigateTo('team')}
            >
              Team
            </button>
            
            {!isAuthenticated && (
              <button 
                className="auth-btn"
                onClick={handleOpenLogin}
              >
                Sign in
              </button>
            )}
          </div>
        </div>
      </header>

      <div className="app-main">
        {isGuest && (
          <GuestBanner 
            remainingMessages={guestMaxMessages - guestMessageCount}
            maxMessages={guestMaxMessages}
            onLogin={handleOpenLogin}
          />
        )}
        
        <div className="content-layout">
          <div className={`chat-wrapper ${showDiseasePanel ? 'with-panel' : ''}`}>
            <ChatInterfaceNew 
              selectedLanguage={selectedLanguage} 
              user={user}
              guestId={localStorage.getItem('guestId')}
              onSendMessage={handleSendMessage}
              persistedMessages={messages}
              onMessagesUpdate={addMessage}
              sessionId={sessionId}
            />
          </div>
          
          {showDiseasePanel && (
            <div className="disease-panel-wrapper">
              <DiseasePanel selectedLanguage={selectedLanguage} />
            </div>
          )}
        </div>
      </div>

      <div className="quick-buttons-section">
        <QuickButtons selectedLanguage={selectedLanguage} />
      </div>

      <footer className="app-footer">
        <div className="footer-content">
          <p>⚠️ Medical Disclaimer: This AI assistant provides general health information only.</p>
        </div>
      </footer>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
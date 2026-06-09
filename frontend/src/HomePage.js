import React, { useState, useEffect } from 'react';
import './HomePage.css';

const HomePage = ({ onStartGuestChat, onOpenLogin, onOpenSignup,onOpenTeam }) => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [typedText, setTypedText] = useState('');
  const fullText = 'Less structure, more intelligence.';

  useEffect(() => {
    // Typing animation
    let i = 0;
    const interval = setInterval(() => {
      if (i <= fullText.length) {
        setTypedText(fullText.slice(0, i));
        i++;
      } else {
        clearInterval(interval);
      }
    }, 50);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const quickActions = [
    { icon: '+', label: 'No waiting', action: null },
    { icon: '⌘', label: 'no appointments', action: null },
    { icon: '⚙️', label: 'no language barriers', action: null },
    { icon: '🎨', label: 'Easy from Ure phone', action: null },
  ];

  const navLinks = [
    'Product', 'Resources', 'Community', 'Events', 'Blog', 
    'Docs', 'Updates', 'Help center', 'AI image generator', 
    'Trust center', 'AI music generator', 'API', 'Manus browser', 
    'Team plan', 'Startups', 'Widle', 'Research', 'Playbook', 
    'Mail', 'Manus', 'Brand assets', 'Slack integration'
  ];

  const socialLinks = ['in', 'X', '0', 'from 0Meta'];

  return (
    <div className="homepage">
      {/* Animated background gradient */}
      <div 
        className="homepage-bg"
        style={{
          background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(0,0,0,0.02) 0%, rgba(0,0,0,0) 50%)`
        }}
      />

      {/* Main Content */}
      <div className="homepage-content">
        {/* Header */}
        <header className="home-header">
          <div className="home-logo">
            <span className="logo-symbol">⌘</span>
            <span className="logo-text">AarogyaAI</span>
          </div>
          <div className="home-actions">
          <button onClick={onOpenTeam} className="home-btn-outline">Meet the Founders</button>
            <button onClick={onOpenLogin} className="home-btn-outline">Sign in</button>
            <button onClick={onOpenSignup} className="home-btn-primary">Get started →</button>
          </div>
        </header>

        {/* Hero Section */}
        <section className="hero-section">
          <div className="hero-badge">
            <span className="badge-dot"></span>
            <span>What can I do for you?</span>
          </div>
          
          <h1 className="hero-title">
          Healthcare information,
          in your mother tongue.
          </h1>
          
          <div className="hero-typed">
            <span className="typed-cursor">_</span>
            <span className="typed-text">{typedText}</span>
          </div>

          {/* Quick Actions */}
          <div className="quick-actions">
            {quickActions.map((action, index) => (
              <button key={index} className="quick-action-btn">
                {action.icon} {action.label}
              </button>
            ))}
          </div>
        </section>

        {/* Guest Access Card */}
        <div className="guest-card">
          <div className="guest-card-header">
            <span className="guest-icon">👤</span>
            <div>
              <h3>Try before you sign up</h3>
              <p>Send 3 messages as a guest — no email required</p>
            </div>
          </div>
          <button onClick={onStartGuestChat} className="guest-start-btn">
            Start as guest →
          </button>
          <div className="guest-features">
            <span>✓ 3 free messages</span>
            <span>✓ No registration</span>
            <span>✓ Full chatbot access</span>
          </div>
        </div>

        {/* Features Grid */}
        <div className="features-grid">
          <div className="feature-item">
            <div className="feature-icon">🌐</div>
            <h4>6+ Languages</h4>
            <p>Hindi, Marathi, Tamil, Telugu, Bengali, English</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">🤖</div>
            <h4>AI-Powered</h4>
            <p>Intelligent health responses in seconds</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">📚</div>
            <h4>50+ Diseases</h4>
            <p>Comprehensive health database</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">🚨</div>
            <h4>Emergency Detection</h4>
            <p>Smart symptom analysis</p>
          </div>
        </div>

        {/* Navigation Links */}
        <div className="nav-links">
          {navLinks.map((link, index) => (
            <a key={index} href="#" className="nav-link">{link}</a>
          ))}
        </div>

        {/* Footer */}
        <footer className="home-footer">
          <div className="footer-social">
            {socialLinks.map((link, index) => (
              <a key={index} href="#" className="social-link">{link}</a>
            ))}
          </div>
          <div className="footer-copyright">
            <span>© 2024 AarogyaAI</span>
            <span>Health information for everyone</span>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default HomePage;
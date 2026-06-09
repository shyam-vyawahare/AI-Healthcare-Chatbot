import React, { useState, useEffect } from 'react';
import './LandingPage.css';

const LandingPage = ({ onSelectUserType }) => {
  const [selectedType, setSelectedType] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('');

  useEffect(() => {
    // Scroll to top when component mounts
    window.scrollTo(0, 0);
    
    // Add animation on scroll
    const handleScroll = () => {
      const elements = document.querySelectorAll('.fade-up');
      elements.forEach(el => {
        const rect = el.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight - 100;
        if (isVisible) {
          el.classList.add('visible');
        }
      });
    };
    
    window.addEventListener('scroll', handleScroll);
    handleScroll();
    
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleGetStarted = (type) => {
    setSelectedType(type);
    setModalType(type);
    setShowModal(true);
  };

  const confirmSelection = () => {
    setShowModal(false);
    if (onSelectUserType) {
      onSelectUserType(modalType);
    }
  };

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-overlay"></div>
        <div className="container">
          <div className="hero-content">
            <div className="hero-badge">
              <span className="badge-icon">🚀</span>
              <span>AI-Powered Healthcare Assistant</span>
            </div>
            <h1 className="hero-title">
              <span className="gradient-text">AarogyaAI</span>
              <br />
              Your 24/7 Intelligent Health Companion
            </h1>
            <p className="hero-subtitle">
              Breaking language barriers in healthcare with multilingual AI support. 
              Get instant, reliable health information in English, Hindi, Marathi, and more.
            </p>
            <div className="hero-stats">
              <div className="stat">
                <span className="stat-number">6+</span>
                <span className="stat-label">Languages</span>
              </div>
              <div className="stat">
                <span className="stat-number">50+</span>
                <span className="stat-label">Diseases Covered</span>
              </div>
              <div className="stat">
                <span className="stat-number">24/7</span>
                <span className="stat-label">Availability</span>
              </div>
              <div className="stat">
                <span className="stat-number">10k+</span>
                <span className="stat-label">Users Served</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* What Makes Us Different Section */}
      <section className="different-section">
        <div className="container">
          <div className="section-header">
            <h2>What Makes <span className="gradient-text">AarogyaAI</span> Different?</h2>
            <p>Not just another chatbot — Your intelligent health partner</p>
          </div>
          <div className="features-grid">
            <div className="feature-card fade-up">
              <div className="feature-icon">🌐</div>
              <h3>True Multilingual Support</h3>
              <p>Speak in English, Hindi, Marathi, Tamil, Telugu, or Bengali — get responses in your preferred language. No language barriers in healthcare.</p>
            </div>
            <div className="feature-card fade-up">
              <div className="feature-icon">🤖</div>
              <h3>Advanced AI Intelligence</h3>
              <p>Powered by Google's Gemini AI, providing accurate, context-aware health information with conversational memory.</p>
            </div>
            <div className="feature-card fade-up">
              <div className="feature-icon">📚</div>
              <h3>Comprehensive Disease Database</h3>
              <p>Access detailed information on COVID-19, Dengue, Malaria, Diabetes, Typhoid and more with symptoms, prevention, and care tips.</p>
            </div>
            <div className="feature-card fade-up">
              <div className="feature-icon">⚡</div>
              <h3>Instant Emergency Detection</h3>
              <p>Smart detection of emergency keywords with immediate redirection to medical services when needed.</p>
            </div>
            <div className="feature-card fade-up">
              <div className="feature-icon">🔄</div>
              <h3>Community-Driven Knowledge</h3>
              <p>Doctors and medical experts can contribute to expand our disease database, making it more comprehensive every day.</p>
            </div>
            <div className="feature-card fade-up">
              <div className="feature-icon">🔒</div>
              <h3>Privacy First</h3>
              <p>Your conversations are private and secure. No personal data stored without consent.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Dual CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-header">
            <h2>Join the Healthcare Revolution</h2>
            <p>Choose your path and start your journey with AarogyaAI</p>
          </div>
          <div className="cta-cards">
            {/* General User Card */}
            <div className="cta-card user-card fade-up">
              <div className="card-badge">Most Popular</div>
              <div className="card-icon">👤</div>
              <h3>General User</h3>
              <p className="card-description">
                Get instant health information, symptom guidance, and preventive care tips in your preferred language.
              </p>
              <div className="card-features">
                <div className="feature">✓ 24/7 AI Chatbot Access</div>
                <div className="feature">✓ Multilingual Support</div>
                <div className="feature">✓ Disease Information Database</div>
                <div className="feature">✓ Symptom Checker</div>
                <div className="feature">✓ Health Tips & Resources</div>
              </div>
              <button 
                className="cta-button user-button"
                onClick={() => handleGetStarted('user')}
              >
                Start Chatting Now 🚀
              </button>
            </div>

            {/* Doctor/Expert Card */}
            <div className="cta-card doctor-card fade-up">
              <div className="card-badge expert">Expert Access</div>
              <div className="card-icon">👨‍⚕️</div>
              <h3>Medical Expert</h3>
              <p className="card-description">
                Contribute to our knowledge base. Add new diseases, symptoms, treatments, and help improve healthcare access.
              </p>
              <div className="card-features">
                <div className="feature">✓ Add New Diseases</div>
                <div className="feature">✓ Update Symptom Database</div>
                <div className="feature">✓ Contribute Treatment Info</div>
                <div className="feature">✓ Review Medical Content</div>
                <div className="feature">✓ Impact Public Health</div>
              </div>
              <button 
                className="cta-button doctor-button"
                onClick={() => handleGetStarted('doctor')}
              >
                Join as Expert 👨‍⚕️
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works">
        <div className="container">
          <div className="section-header">
            <h2>How <span className="gradient-text">AarogyaAI</span> Works</h2>
            <p>Simple, intuitive, and powerful</p>
          </div>
          <div className="steps">
            <div className="step fade-up">
              <div className="step-number">1</div>
              <div className="step-icon">💬</div>
              <h4>Type Your Question</h4>
              <p>Ask anything about symptoms, diseases, or preventive care in your preferred language</p>
            </div>
            <div className="step fade-up">
              <div className="step-number">2</div>
              <div className="step-icon">🤖</div>
              <h4>AI Processes</h4>
              <p>Our AI analyzes your query and retrieves relevant health information</p>
            </div>
            <div className="step fade-up">
              <div className="step-number">3</div>
              <div className="step-icon">🌐</div>
              <h4>Get Response</h4>
              <p>Receive accurate, helpful information in your language with preventive tips</p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials">
        <div className="container">
          <div className="section-header">
            <h2>Trusted by Thousands</h2>
            <p>Real stories from our users</p>
          </div>
          <div className="testimonials-grid">
            <div className="testimonial-card fade-up">
              <div className="testimonial-content">
                <p>"AarogyaAI helped my mother understand her diabetes better in Marathi. She now follows preventive care regularly!"</p>
              </div>
              <div className="testimonial-author">
                <div className="author-avatar">📝</div>
                <div>
                  <div className="author-name">Rajesh Sharma</div>
                  <div className="author-role">Family Caregiver</div>
                </div>
              </div>
            </div>
            <div className="testimonial-card fade-up">
              <div className="testimonial-content">
                <p>"As a doctor, I appreciate how accurately it provides general health information. Great tool for rural healthcare."</p>
              </div>
              <div className="testimonial-author">
                <div className="author-avatar">👨‍⚕️</div>
                <div>
                  <div className="author-name">Dr. Priya Mehta</div>
                  <div className="author-role">General Physician</div>
                </div>
              </div>
            </div>
            <div className="testimonial-card fade-up">
              <div className="testimonial-content">
                <p>"Finally a health chatbot that speaks my language! The Hindi support is fantastic and very accurate."</p>
              </div>
              <div className="testimonial-author">
                <div className="author-avatar">👩</div>
                <div>
                  <div className="author-name">Sunita Verma</div>
                  <div className="author-role">Rural Health Worker</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <div className="footer-logo">🏥 AarogyaAI</div>
              <p>Democratizing healthcare information with AI</p>
            </div>
            <div className="footer-links">
              <div className="link-group">
                <h4>Product</h4>
                <a href="#features">Features</a>
                <a href="#how-it-works">How It Works</a>
                <a href="#testimonials">Testimonials</a>
              </div>
              <div className="link-group">
                <h4>Legal</h4>
                <a href="#">Privacy Policy</a>
                <a href="#">Terms of Service</a>
                <a href="#">Medical Disclaimer</a>
              </div>
              <div className="link-group">
                <h4>Contact</h4>
                <a href="#">support@aarogyaai.com</a>
                <a href="#">+91-XXX-XXX-XXXX</a>
                <a href="#">Help Center</a>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            <p>© 2024 AarogyaAI. All rights reserved. Not a substitute for professional medical advice.</p>
            <div className="footer-disclaimer">
              ⚠️ Emergency? Call 108 immediately. AarogyaAI provides educational information only.
            </div>
          </div>
        </div>
      </footer>

      {/* Modal for confirmation */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-icon">
              {modalType === 'user' ? '👤' : '👨‍⚕️'}
            </div>
            <h3>{modalType === 'user' ? 'Welcome to AarogyaAI!' : 'Welcome Medical Expert!'}</h3>
            <p>
              {modalType === 'user' 
                ? "You're about to experience intelligent, multilingual health assistance. Ready to start your health journey?" 
                : "Thank you for contributing to better healthcare! You'll be redirected to the expert portal."}
            </p>
            <div className="modal-buttons">
              <button className="modal-cancel" onClick={() => setShowModal(false)}>Cancel</button>
              <button className="modal-confirm" onClick={confirmSelection}>Continue →</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LandingPage;
import React, { useState, useEffect } from 'react';
import './TeamPage.css';

const TeamPage = ({ onBack }) => {
  const [members, setMembers] = useState([
    {
      id: 1,
      name: "Ashish Sarda",
      role: "SAP Developer & AI Engineer",
      bio: "Full-stack developer specializing in AI integration and healthcare technology. Passionate about making healthcare accessible through innovative solutions.",
      expertise: ["AI/ML", "Full Stack", "SAP"],
      social: {
        github: "https://github.com/ashishsarda",
        linkedin: "https://linkedin.com/in/ashishsarda",
        twitter: "https://twitter.com/ashishsarda"
      },
      image: null,
      quote: "Technology should serve humanity, not the other way around."
    },
    {
      id: 2,
      name: "Shyam Vyawahare",
      role: "Backend & Database Specialist",
      bio: "Backend architect with expertise in scalable systems and data management. Committed to building robust healthcare solutions that make a difference.",
      expertise: ["Backend Dev", "Database Design", "API Development"],
      social: {
        github: "https://github.com/shyamvyawahare",
        linkedin: "https://linkedin.com/in/shyamvyawahare",
        twitter: "https://twitter.com/shyamvyawahare"
      },
      image: null,
      quote: "Code is the closest thing we have to magic."
    }
  ]);

  const [selectedMember, setSelectedMember] = useState(null);
  const [uploadingImage, setUploadingImage] = useState(null);

  useEffect(() => {
    // Load images from localStorage
    const savedImages = localStorage.getItem('teamImages');
    if (savedImages) {
      const images = JSON.parse(savedImages);
      setMembers(prev => prev.map(member => ({
        ...member,
        image: images[member.id] || null
      })));
    }
  }, []);

  const handleImageUpload = (memberId, event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const imageData = reader.result;
        
        // Update member image
        setMembers(prev => prev.map(member => 
          member.id === memberId ? { ...member, image: imageData } : member
        ));
        
        // Save to localStorage
        const savedImages = localStorage.getItem('teamImages');
        const images = savedImages ? JSON.parse(savedImages) : {};
        images[memberId] = imageData;
        localStorage.setItem('teamImages', JSON.stringify(images));
        
        setUploadingImage(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('');
  };

  const handleMemberClick = (member) => {
    setSelectedMember(member);
  };

  const closeModal = () => {
    setSelectedMember(null);
  };

  return (
    <div className="team-page">
      {/* Animated Background */}
      <div className="team-bg">
        <div className="bg-orb orb-1"></div>
        <div className="bg-orb orb-2"></div>
        <div className="bg-orb orb-3"></div>
      </div>

      {/* Header */}
      <header className="team-header">
        <button onClick={onBack} className="back-to-home">
          ← Back to Home
        </button>
        <div className="team-logo">
          <span className="logo-symbol">⌘</span>
          <span>AarogyaAI</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="team-main">
        <div className="team-hero">
          <div className="hero-badge">
            <span className="badge-dot"></span>
            <span>The Minds Behind AarogyaAI</span>
          </div>
          <h1 className="team-title">
            Meet the <span className="gradient-text">Team</span>
          </h1>
          <p className="team-subtitle">
            Passionate developers committed to revolutionizing healthcare through AI
          </p>
        </div>

        <div className="team-grid">
          {members.map((member) => (
            <div key={member.id} className="team-card" onClick={() => handleMemberClick(member)}>
              <div className="card-glow"></div>
              
              {/* Image Container */}
              <div className="member-image-container">
                {member.image ? (
                  <img src={member.image} alt={member.name} className="member-image" />
                ) : (
                  <div className="member-initials">
                    {getInitials(member.name)}
                  </div>
                )}
                
                {/* Upload Button */}
                <label className="upload-btn">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleImageUpload(member.id, e)}
                    style={{ display: 'none' }}
                  />
                  <span className="upload-icon">📸</span>
                </label>
              </div>

              <div className="member-info">
                <h3 className="member-name">{member.name}</h3>
                <p className="member-role">{member.role}</p>
                <p className="member-bio">{member.bio}</p>
                
                <div className="member-expertise">
                  {member.expertise.map((skill, idx) => (
                    <span key={idx} className="expertise-tag">{skill}</span>
                  ))}
                </div>

                <div className="member-social">
                  <a href={member.social.github} target="_blank" rel="noopener noreferrer" className="social-link">
                    <span>GitHub</span>
                  </a>
                  <a href={member.social.linkedin} target="_blank" rel="noopener noreferrer" className="social-link">
                    <span>LinkedIn</span>
                  </a>
                  <a href={member.social.twitter} target="_blank" rel="noopener noreferrer" className="social-link">
                    <span>Twitter</span>
                  </a>
                </div>
              </div>

              <div className="card-hover-effect"></div>
            </div>
          ))}
        </div>

        {/* Team Stats */}
        <div className="team-stats">
          <div className="stat-item">
            <div className="stat-number">2</div>
            <div className="stat-label">Team Members</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">50+</div>
            <div className="stat-label">Diseases Covered</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">6</div>
            <div className="stat-label">Languages</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">24/7</div>
            <div className="stat-label">Availability</div>
          </div>
        </div>

        {/* Mission Section */}
        <div className="mission-section">
          <h2>Our Mission</h2>
          <p>
            We believe that healthcare information should be accessible to everyone, 
            regardless of language or location. AarogyaAI is our contribution to making 
            quality health information available in every Indian language, completely free.
          </p>
          <div className="mission-quote">
            "Democratizing healthcare through technology"
          </div>
        </div>
      </main>

      {/* Member Detail Modal */}
      {selectedMember && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>×</button>
            
            <div className="modal-content">
              <div className="modal-image">
                {selectedMember.image ? (
                  <img src={selectedMember.image} alt={selectedMember.name} />
                ) : (
                  <div className="modal-initials">
                    {getInitials(selectedMember.name)}
                  </div>
                )}
              </div>
              
              <div className="modal-info">
                <h2>{selectedMember.name}</h2>
                <p className="modal-role">{selectedMember.role}</p>
                
                <div className="modal-bio">
                  <h3>Biography</h3>
                  <p>{selectedMember.bio}</p>
                </div>
                
                <div className="modal-quote">
                  <span className="quote-mark">"</span>
                  <p>{selectedMember.quote}</p>
                </div>
                
                <div className="modal-expertise">
                  <h3>Expertise</h3>
                  <div className="expertise-list">
                    {selectedMember.expertise.map((skill, idx) => (
                      <span key={idx} className="expertise-item">{skill}</span>
                    ))}
                  </div>
                </div>
                
                <div className="modal-social">
                  <h3>Connect</h3>
                  <div className="social-links">
                    <a href={selectedMember.social.github} target="_blank" rel="noopener noreferrer" className="social-btn github">
                      GitHub
                    </a>
                    <a href={selectedMember.social.linkedin} target="_blank" rel="noopener noreferrer" className="social-btn linkedin">
                      LinkedIn
                    </a>
                    <a href={selectedMember.social.twitter} target="_blank" rel="noopener noreferrer" className="social-btn twitter">
                      Twitter
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="team-footer">
        <p>© 2024 AarogyaAI | Built with ❤️ for better healthcare</p>
      </footer>
    </div>
  );
};

export default TeamPage;
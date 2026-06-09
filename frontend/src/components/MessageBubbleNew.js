import React from 'react';
import './MessageBubbleNew.css';

const MessageBubbleNew = ({ message }) => {
  const { text, sender, timestamp, isError, severityGuidance } = message;
  
  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatText = (text) => {
    // Handle markdown-like formatting
    let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/•/g, '<span class="bullet">•</span>');
    formatted = formatted.replace(/\n/g, '<br/>');
    return formatted;
  };

  return (
    <div className={`message-row ${sender}`}>
      {sender === 'bot' && (
        <div className="message-avatar">
          <div className="bot-avatar-small">🧠</div>
        </div>
      )}
      
      <div className={`message-bubble-premium ${sender} ${isError ? 'error' : ''}`}>
        <div 
          className="message-text-premium"
          dangerouslySetInnerHTML={{ __html: formatText(text) }}
        />
        
        {severityGuidance && severityGuidance.severity !== 'low' && (
          <div className={`severity-tag ${severityGuidance.severity}`}>
            {severityGuidance.severity === 'high' ? '🚨' : '⚠️'} 
            {severityGuidance.recommendation}
          </div>
        )}
        
        <div className="message-time-premium">
          {formatTime(timestamp)}
        </div>
      </div>
      
      {sender === 'user' && (
        <div className="message-avatar user">
          <div className="user-avatar-small">👤</div>
        </div>
      )}
    </div>
  );
};

export default MessageBubbleNew;
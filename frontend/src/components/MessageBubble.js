import React from 'react';
import ReactMarkdown from 'react-markdown';
import './MessageBubble.css';

const MessageBubble = ({ message }) => {
  const { text, sender, timestamp, isError, severityGuidance, aiSource } = message;
  
  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getSourceIcon = (source) => {
    switch(source) {
      case 'gemini_ai':
        return '🤖';
      case 'disease_database':
        return '📚';
      case 'fallback_rules':
        return '⚙️';
      default:
        return '💬';
    }
  };

  // Custom components for markdown rendering
  const MarkdownComponents = {
    // Bold text
    strong: ({node, ...props}) => <strong style={{ fontWeight: 'bold', color: '#075E54' }} {...props} />,
    // Lists
    ul: ({node, ...props}) => <ul style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }} {...props} />,
    ol: ({node, ...props}) => <ol style={{ margin: '0.5rem 0', paddingLeft: '1.5rem' }} {...props} />,
    li: ({node, ...props}) => <li style={{ margin: '0.25rem 0' }} {...props} />,
    // Paragraphs
    p: ({node, ...props}) => <p style={{ margin: '0.5rem 0', lineHeight: '1.4' }} {...props} />,
    // Headers
    h1: ({node, ...props}) => <h1 style={{ fontSize: '1.3rem', margin: '0.5rem 0' }} {...props} />,
    h2: ({node, ...props}) => <h2 style={{ fontSize: '1.2rem', margin: '0.5rem 0' }} {...props} />,
    h3: ({node, ...props}) => <h3 style={{ fontSize: '1.1rem', margin: '0.5rem 0' }} {...props} />,
    // Line breaks
    br: ({node, ...props}) => <br {...props} />,
  };

  return (
    <div className={`message-wrapper ${sender}`}>
      <div className={`message-bubble ${sender} ${isError ? 'error' : ''}`}>
        {sender === 'bot' && (
          <div className="bot-icon">
            {getSourceIcon(aiSource)}
          </div>
        )}
        <div className="message-content">
          <div className="message-text">
            {sender === 'bot' ? (
              <ReactMarkdown components={MarkdownComponents}>
                {text}
              </ReactMarkdown>
            ) : (
              // User messages - plain text
              text.split('\n').map((line, i) => (
                <React.Fragment key={i}>
                  {line}
                  {i < text.split('\n').length - 1 && <br />}
                </React.Fragment>
              ))
            )}
          </div>
          
          {/* Severity Guidance (if available) */}
          {severityGuidance && severityGuidance.severity !== 'low' && (
            <div className={`severity-badge ${severityGuidance.severity}`}>
              {severityGuidance.severity === 'high' ? '🚨' : '⚠️'} 
              {severityGuidance.recommendation}
            </div>
          )}
          
          <div className="message-time">
            {formatTime(timestamp)}
            {sender === 'user' && <span className="read-status">✓</span>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
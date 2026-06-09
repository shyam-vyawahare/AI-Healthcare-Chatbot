import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import './ChatInterfaceNew.css';

const ChatInterfaceNew = ({ 
  selectedLanguage = 'en', 
  user = null, 
  guestId = null, 
  onSendMessage = null,
  persistedMessages = [],
  onMessagesUpdate = null,
  sessionId: propSessionId = null
}) => {
  // All useState hooks must be inside the component
  const [messages, setMessages] = useState(persistedMessages || []);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [sessionId, setSessionId] = useState(propSessionId || uuidv4());
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  const [showSuggestions, setShowSuggestions] = useState(true);
  
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const inputRef = useRef(null);

  // Save session ID to localStorage
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('sessionId', sessionId);
    }
  }, [sessionId]);

  // Sync messages with parent component
  useEffect(() => {
    if (onMessagesUpdate && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage && !lastMessage.synced) {
        onMessagesUpdate(lastMessage);
        setMessages(prev => prev.map(msg => 
          msg.id === lastMessage.id ? { ...msg, synced: true } : msg
        ));
      }
    }
  }, [messages, onMessagesUpdate]);

  // Restore messages from localStorage on mount
  useEffect(() => {
    const savedMessages = localStorage.getItem('chatMessages');
    if (savedMessages && messages.length === 0) {
      try {
        const parsed = JSON.parse(savedMessages);
        setMessages(parsed);
        if (parsed.length > 1) {
          setShowSuggestions(false);
        }
      } catch (e) {
        console.error('Error loading saved messages:', e);
      }
    }
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('chatMessages', JSON.stringify(messages.slice(-50)));
    }
  }, [messages]);

  // Auto-scroll logic
  const handleScroll = () => {
    if (messagesContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
      setShouldAutoScroll(isAtBottom);
    }
  };

  const scrollToBottom = () => {
    if (shouldAutoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Welcome message
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage = {
        id: Date.now(),
        text: getWelcomeMessage(selectedLanguage),
        sender: 'bot',
        timestamp: new Date(),
        language: selectedLanguage
      };
      setMessages([welcomeMessage]);
    }
  }, [selectedLanguage]);

  const getWelcomeMessage = (lang) => {
    const messages = {
      'en': "👋 Welcome to AarogyaAI!\n\nI'm your intelligent health assistant powered by Google Gemini AI. Ask me anything about symptoms, diseases, prevention, or wellness. I can respond in multiple languages - just type in your preferred language!\n\n💡 Try asking: 'I have fever and headache' or 'Tell me about diabetes prevention'",
      'hi': "👋 आरोग्यAI में आपका स्वागत है!\n\nमैं आपका बुद्धिमान स्वास्थ्य सहायक हूं। मुझसे लक्षणों, बीमारियों, रोकथाम या स्वास्थ्य के बारे में कुछ भी पूछें।\n\n💡 पूछें: 'मुझे बुखार और सिरदर्द है' या 'डायबिटीज के बारे में बताएं'",
      'mr': "👋 आरोग्यAI मध्ये आपले स्वागत आहे!\n\nमी तुमचा बुद्धिमान आरोग्य सहाय्यक आहे. मला लक्षणे, रोग, प्रतिबंध किंवा आरोग्याबद्दल काहीही विचारा.\n\n💡 विचारा: 'मला ताप आणि डोकेदुखी आहे' किंवा 'मधुमेहाबद्दल सांगा'"
    };
    return messages[lang] || messages['en'];
  };

  const getSuggestions = () => {
    const suggestions = {
      'en': [
        { icon: '🤒', text: 'I have fever and headache' },
        { icon: '🤧', text: 'Cold and cough remedies' },
        { icon: '🩺', text: 'Diabetes symptoms' },
        { icon: '🦟', text: 'Dengue prevention tips' },
        { icon: '💊', text: 'Medicine safety tips' },
        { icon: '🏥', text: 'When to see a doctor' }
      ],
      'hi': [
        { icon: '🤒', text: 'मुझे बुखार और सिरदर्द है' },
        { icon: '🤧', text: 'ज़ुकाम और खांसी के उपाय' },
        { icon: '🩺', text: 'मधुमेह के लक्षण' },
        { icon: '🦟', text: 'डेंगू बचाव के टिप्स' },
        { icon: '💊', text: 'दवा सुरक्षा टिप्स' },
        { icon: '🏥', text: 'डॉक्टर कब दिखाएं' }
      ],
      'mr': [
        { icon: '🤒', text: 'मला ताप आणि डोकेदुखी आहे' },
        { icon: '🤧', text: 'सर्दी आणि खोकला उपचार' },
        { icon: '🩺', text: 'मधुमेहाची लक्षणे' },
        { icon: '🦟', text: 'डेंग्यू प्रतिबंध टिप्स' },
        { icon: '💊', text: 'औषध सुरक्षा टिप्स' },
        { icon: '🏥', text: 'डॉक्टरकडे कधी जावे' }
      ]
    };
    return suggestions[selectedLanguage] || suggestions['en'];
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;
    
    // Check guest limit
    if (onSendMessage) {
      const canSend = await onSendMessage();
      if (!canSend) return;
    }

    setShouldAutoScroll(true);
    setShowSuggestions(false);

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date(),
      language: selectedLanguage
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setIsThinking(true);

    try {
      const response = await axios.post('http://localhost:5000/api/chat', {
        message: inputMessage,
        session_id: sessionId,
        language: selectedLanguage,
        user_id: user?.user_id,
        guest_id: guestId
      });

      const botMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date(),
        language: selectedLanguage,
        severityGuidance: response.data.severity_guidance,
        aiSource: response.data.ai_source
      };

      setMessages(prev => [...prev, botMessage]);
      
      // Save to parent if needed
      if (onMessagesUpdate) {
        onMessagesUpdate(botMessage);
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        text: getErrorMessage(selectedLanguage),
        sender: 'bot',
        timestamp: new Date(),
        isError: true,
        language: selectedLanguage
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsThinking(false);
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  };

  const getErrorMessage = (lang) => {
    const errors = {
      'en': "⚠️ Sorry, I'm having trouble connecting. Please check your internet and try again.",
      'hi': "⚠️ क्षमा करें, कनेक्ट करने में समस्या हो रही है। कृपया अपना इंटरनेट जांचें और पुनः प्रयास करें।",
      'mr': "⚠️ क्षमस्व, कनेक्ट करण्यात अडचण येत आहे. कृपया तुमचे इंटरनेट तपासा आणि पुन्हा प्रयत्न करा."
    };
    return errors[lang] || errors['en'];
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
    setTimeout(() => sendMessage(), 100);
  };

  const clearChat = () => {
    setMessages([{
      id: Date.now(),
      text: getWelcomeMessage(selectedLanguage),
      sender: 'bot',
      timestamp: new Date(),
      language: selectedLanguage
    }]);
    setShouldAutoScroll(true);
    setShowSuggestions(true);
    localStorage.removeItem('chatMessages');
  };

  const getPlaceholderText = (lang) => {
    const placeholders = {
      'en': "Ask me anything about your health...",
      'hi': "अपने स्वास्थ्य के बारे में कुछ भी पूछें...",
      'mr': "तुमच्या आरोग्याबद्दल काहीही विचारा..."
    };
    return placeholders[lang] || placeholders['en'];
  };

  // Format message text with markdown
  const formatMessageText = (text) => {
    if (!text) return '';
    
    // Handle bullet points
    let formatted = text.replace(/•/g, '<span class="bullet">•</span>');
    formatted = formatted.replace(/\n/g, '<br/>');
    
    // Handle bold text
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Handle numbered lists
    formatted = formatted.replace(/(\d+)\. /g, '<span class="list-number">$1.</span> ');
    
    return formatted;
  };

  return (
    <div className="chat-container-premium">
      {/* Chat Header */}
      <div className="chat-header-premium">
        <div className="header-left">
          <div className="ai-avatar">
            <div className="avatar-ring">
              <span className="avatar-icon">🧠</span>
            </div>
            <div className="ai-status">
              <h3>AarogyaAI Assistant</h3>
              <div className="status-indicator">
                <span className="status-dot"></span>
                <span>Gemini AI Ready</span>
              </div>
            </div>
          </div>
        </div>
        <div className="header-right">
          <button className="header-btn" onClick={clearChat} title="New chat">
            <span>+</span>
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div 
        className="messages-area-premium" 
        ref={messagesContainerRef}
        onScroll={handleScroll}
      >
        <div className="messages-wrapper">
          {messages.map((message) => (
            <div key={message.id} className={`message-row ${message.sender}`}>
              {message.sender === 'bot' && (
                <div className="message-avatar">
                  <div className="bot-avatar-small">🧠</div>
                </div>
              )}
              
              <div className={`message-bubble-premium ${message.sender} ${message.isError ? 'error' : ''}`}>
                <div 
                  className="message-text-premium"
                  dangerouslySetInnerHTML={{ __html: formatMessageText(message.text) }}
                />
                
                {message.severityGuidance && message.severityGuidance.severity !== 'low' && (
                  <div className={`severity-tag ${message.severityGuidance.severity}`}>
                    {message.severityGuidance.severity === 'high' ? '🚨' : '⚠️'} 
                    {message.severityGuidance.recommendation}
                  </div>
                )}
                
                <div className="message-time-premium">
                  {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
              
              {message.sender === 'user' && (
                <div className="message-avatar user">
                  <div className="user-avatar-small">👤</div>
                </div>
              )}
            </div>
          ))}
          
          {/* Thinking/Loading Animation */}
          {isThinking && (
            <div className="thinking-indicator">
              <div className="thinking-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span className="thinking-text">AarogyaAI is thinking...</span>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Suggestions */}
      {showSuggestions && messages.length === 1 && (
        <div className="suggestions-area">
          <p className="suggestions-title">Quick questions you can ask:</p>
          <div className="suggestions-grid">
            {getSuggestions().map((suggestion, index) => (
              <button 
                key={index}
                className="suggestion-chip"
                onClick={() => handleSuggestionClick(suggestion.text)}
              >
                <span className="suggestion-icon">{suggestion.icon}</span>
                <span>{suggestion.text}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="input-area-premium">
        <div className="input-wrapper">
          <textarea
            ref={inputRef}
            className="message-input-premium"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={getPlaceholderText(selectedLanguage)}
            rows="1"
            disabled={isLoading}
          />
          <button 
            className={`send-btn-premium ${isLoading || !inputMessage.trim() ? 'disabled' : ''}`}
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
          >
            <span className="send-icon">→</span>
          </button>
        </div>
        <p className="input-disclaimer">⚠️ AI-generated health information. Consult a doctor for medical advice.</p>
      </div>
    </div>
  );
};

export default ChatInterfaceNew;
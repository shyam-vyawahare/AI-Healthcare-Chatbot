import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import MessageBubble from './MessageBubble';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import './ChatInterface.css';

const ChatInterface = ({ selectedLanguage }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const inputRef = useRef(null);

  // Initialize session on component mount
  useEffect(() => {
    const newSessionId = uuidv4();
    setSessionId(newSessionId);
    
    // Add welcome message
    const welcomeMessage = {
      id: 1,
      text: getWelcomeMessage(selectedLanguage),
      sender: 'bot',
      timestamp: new Date(),
      language: selectedLanguage
    };
    setMessages([welcomeMessage]);
    
    // Focus input
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  // Handle scroll detection - check if user scrolled up manually
  const handleScroll = () => {
    if (messagesContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
      setShouldAutoScroll(isAtBottom);
    }
  };

  // Auto-scroll only if user hasn't scrolled up
  const scrollToBottom = () => {
    if (shouldAutoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Update scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Update welcome message when language changes
  useEffect(() => {
    if (messages.length > 0 && messages[0].sender === 'bot') {
      const updatedWelcome = {
        ...messages[0],
        text: getWelcomeMessage(selectedLanguage),
        language: selectedLanguage
      };
      setMessages([updatedWelcome, ...messages.slice(1)]);
    }
  }, [selectedLanguage]);

  const getWelcomeMessage = (lang) => {
    const messages = {
      'en': "👋 Hello! I'm your AI Health Assistant. I can provide information about diseases, symptoms, and preventive healthcare. Ask me anything health-related! 🏥",
      'hi': "👋 नमस्ते! मैं आपका AI स्वास्थ्य सहायक हूं। मैं बीमारियों, लक्षणों और निवारक स्वास्थ्य देखभाल के बारे में जानकारी प्रदान कर सकता हूं। मुझसे स्वास्थ्य से संबंधित कुछ भी पूछें! 🏥",
      'mr': "👋 नमस्कार! मी तुमचा AI आरोग्य सहाय्यक आहे. मी रोग, लक्षणे आणि प्रतिबंधात्मक आरोग्य सेवेबद्दल माहिती देऊ शकतो. मला आरोग्याशी संबंधित काहीही विचारा! 🏥",
      'ta': "👋 வணக்கம்! நான் உங்கள் AI உடல்நல உதவியாளர். நோய்கள், அறிகுறிகள் மற்றும் தடுப்பு சுகாதாரப் பராமரிப்பு பற்றிய தகவல்களை வழங்க முடியும். உடல்நலம் தொடர்பான எதையும் என்னிடம் கேளுங்கள்! 🏥",
      'te': "👋 నమస్కారం! నేను మీ AI ఆరోగ్య సహాయకుడిని. వ్యాధులు, లక్షణాలు మరియు నివారణ ఆరోగ్య సంరక్షణ గురించి సమాచారం అందించగలను. ఆరోగ్య సంబంధిత ఏదైనా నన్ను అడగండి! 🏥",
      'bn': "👋 নমস্কার! আমি আপনার AI স্বাস্থ্য সহায়ক। আমি রোগ, লক্ষণ এবং প্রতিরোধমূলক স্বাস্থ্যসেবা সম্পর্কে তথ্য প্রদান করতে পারি। আমাকে স্বাস্থ্য সম্পর্কিত কিছু জিজ্ঞাসা করুন! 🏥"
    };
    return messages[lang] || messages['en'];
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    // Reset auto-scroll when sending new message
    setShouldAutoScroll(true);

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
    setIsTyping(true);

    try {
      const response = await axios.post('http://localhost:5000/api/chat', {
        message: inputMessage,
        session_id: sessionId,
        language: selectedLanguage
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
    } catch (error) {
      console.error('Error sending message:', error);
      
      let errorText = getErrorMessage(selectedLanguage);
      if (error.response?.data?.response) {
        errorText = error.response.data.response;
      }

      const errorMessage = {
        id: Date.now() + 1,
        text: errorText,
        sender: 'bot',
        timestamp: new Date(),
        isError: true,
        language: selectedLanguage
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  };

  const getErrorMessage = (lang) => {
    const errors = {
      'en': "⚠️ Sorry, I'm having trouble connecting. Please check if the backend server is running on http://localhost:5000 and try again.",
      'hi': "⚠️ क्षमा करें, मुझे कनेक्ट करने में समस्या हो रही है। कृपया जांचें कि बैकेंड सर्वर चल रहा है और पुनः प्रयास करें।",
      'mr': "⚠️ क्षमस्व, मला कनेक्ट करण्यात अडचण येत आहे. कृपया बॅकेंड सर्वर चालू आहे का ते तपासा आणि पुन्हा प्रयत्न करा.",
      'ta': "⚠️ மன்னிக்கவும், இணைப்பதில் சிக்கல் உள்ளது. பேக்கெண்ட் சர்வர் இயங்குகிறதா என சரிபார்த்து மீண்டும் முயற்சிக்கவும்.",
      'te': "⚠️ క్షమించండి, కనెక్ట్ చేయడంలో సమస్య ఉంది. బ్యాకెండ్ సర్వర్ నడుస్తుందో లేదో తనిఖీ చేసి మళ్లీ ప్రయత్నించండి.",
      'bn': "⚠️ দুঃখিত, সংযোগ করতে সমস্যা হচ্ছে। অনুগ্রহ করে ব্যাকএন্ড সার্ভার চলছে কিনা চেক করে আবার চেষ্টা করুন।"
    };
    return errors[lang] || errors['en'];
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = async () => {
    if (sessionId) {
      try {
        await axios.delete(`http://localhost:5000/api/clear-conversation/${sessionId}`);
      } catch (error) {
        console.error('Error clearing conversation:', error);
      }
    }
    
    // Reset messages with welcome message
    setMessages([{
      id: Date.now(),
      text: getWelcomeMessage(selectedLanguage),
      sender: 'bot',
      timestamp: new Date(),
      language: selectedLanguage
    }]);
    setShouldAutoScroll(true);
  };

  const getPlaceholderText = (lang) => {
    const placeholders = {
      'en': "Type your health question here...",
      'hi': "अपना स्वास्थ्य प्रश्न यहां टाइप करें...",
      'mr': "तुमचा आरोग्य प्रश्न इथे टाइप करा...",
      'ta': "உங்கள் உடல்நல கேள்வியை இங்கே தட்டச்சு செய்க...",
      'te': "మీ ఆరోగ్య ప్రశ్నను ఇక్కడ టైప్ చేయండి...",
      'bn': "আপনার স্বাস্থ্য প্রশ্ন এখানে টাইপ করুন..."
    };
    return placeholders[lang] || placeholders['en'];
  };

  // NEW: Working PDF Export Function
  const exportToPDF = async () => {
    try {
      // Show loading indicator
      const exportBtn = document.querySelector('.export-pdf-btn');
      const originalText = exportBtn.innerHTML;
      exportBtn.innerHTML = '⏳ Generating PDF...';
      exportBtn.disabled = true;

      // Create a container for PDF content
      const pdfContainer = document.createElement('div');
      pdfContainer.style.cssText = `
        position: absolute;
        left: -9999px;
        top: 0;
        width: 800px;
        background: white;
        padding: 40px;
        font-family: Arial, sans-serif;
      `;
      
      // Add header
      pdfContainer.innerHTML = `
        <div style="text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 10px;">
          <h1 style="margin: 0; font-size: 28px;">🏥 AarogyaAI Health Chat</h1>
          <p style="margin: 10px 0 0;">Exported on: ${new Date().toLocaleString()}</p>
          <p style="margin: 5px 0 0;">Language: ${selectedLanguage.toUpperCase()}</p>
        </div>
        <div style="padding: 20px;">
      `;
      
      // Add all messages
      messages.forEach((msg, index) => {
        const time = new Date(msg.timestamp).toLocaleTimeString();
        const isUser = msg.sender === 'user';
        const senderName = isUser ? 'You' : 'AarogyaAI';
        const senderIcon = isUser ? '👤' : '🤖';
        
        // Clean text (remove emojis if needed, but keep them)
        const cleanText = msg.text.replace(/\*/g, ''); // Remove markdown asterisks
        
        pdfContainer.innerHTML += `
          <div style="margin-bottom: 20px; text-align: ${isUser ? 'right' : 'left'};">
            <div style="display: inline-block; max-width: 85%; padding: 12px 16px; border-radius: 12px; background: ${isUser ? '#DCF8C6' : '#f0f0f0'}; border: 1px solid #e0e0e0; box-shadow: 0 1px 2px rgba(0,0,0,0.1); text-align: left;">
              <div style="font-weight: bold; margin-bottom: 5px; color: ${isUser ? '#075E54' : '#667eea'};">
                ${senderIcon} ${senderName}
              </div>
              <div style="color: #333; line-height: 1.5; white-space: pre-wrap; font-size: 12px;">${cleanText}</div>
              <div style="font-size: 10px; color: #999; margin-top: 5px;">${time}</div>
            </div>
          </div>
        `;
      });
      
      pdfContainer.innerHTML += `
        </div>
        <div style="text-align: center; padding: 20px; margin-top: 30px; font-size: 10px; color: #999; border-top: 1px solid #e0e0e0;">
          <p>⚠️ Medical Disclaimer: This information is for educational purposes only. Always consult a healthcare provider for medical advice.</p>
          <p>Generated by AarogyaAI - Your AI Health Assistant</p>
        </div>
      `;
      
      document.body.appendChild(pdfContainer);
      
      // Use html2canvas to capture the content
      const canvas = await html2canvas(pdfContainer, {
        scale: 2,
        logging: false,
        useCORS: true,
        backgroundColor: '#ffffff'
      });
      
      // Remove the temporary container
      document.body.removeChild(pdfContainer);
      
      // Create PDF
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });
      
      const imgWidth = 210; // A4 width in mm
      const pageHeight = 297; // A4 height in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let position = 0;
      
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
      
      // Add new page if content exceeds one page
      let heightLeft = imgHeight - pageHeight;
      let currentPosition = -pageHeight;
      
      while (heightLeft > 0) {
        position = heightLeft - imgHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 0, currentPosition, imgWidth, imgHeight);
        heightLeft -= pageHeight;
        currentPosition -= pageHeight;
      }
      
      // Save the PDF
      pdf.save(`aarogyaai_chat_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.pdf`);
      
      // Reset button
      exportBtn.innerHTML = originalText;
      exportBtn.disabled = false;
      
      // Optional: Show success message
      const successMsg = getPDFSuccessMessage(selectedLanguage);
      const tempMsg = document.createElement('div');
      tempMsg.textContent = successMsg;
      tempMsg.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #4caf50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        z-index: 9999;
        animation: fadeOut 3s ease-out;
      `;
      document.body.appendChild(tempMsg);
      setTimeout(() => tempMsg.remove(), 3000);
      
    } catch (error) {
      console.error('PDF Export error:', error);
      alert(getPDFErrorMessage(selectedLanguage));
      
      // Reset button
      const exportBtn = document.querySelector('.export-pdf-btn');
      if (exportBtn) {
        exportBtn.innerHTML = '📄 Export PDF';
        exportBtn.disabled = false;
      }
    }
  };

  const getPDFSuccessMessage = (lang) => {
    const messages = {
      'en': "✅ PDF exported successfully!",
      'hi': "✅ पीडीएफ सफलतापूर्वक निर्यात हुआ!",
      'mr': "✅ पीडीएफ यशस्वीरित्या निर्यात केले!",
      'ta': "✅ PDF வெற்றிகரமாக ஏற்றுமதி செய்யப்பட்டது!",
      'te': "✅ PDF విజయవంతంగా ఎగుమతి చేయబడింది!",
      'bn': "✅ পিডিএফ সফলভাবে রপ্তানি করা হয়েছে!"
    };
    return messages[lang] || messages['en'];
  };

  const getPDFErrorMessage = (lang) => {
    const errors = {
      'en': "❌ Failed to export PDF. Please try again.",
      'hi': "❌ पीडीएफ निर्यात करने में विफल। कृपया पुनः प्रयास करें।",
      'mr': "❌ पीडीएफ निर्यात करण्यात अयशस्वी. कृपया पुन्हा प्रयत्न करा.",
      'ta': "❌ PDF ஏற்றுமதி செய்யத் தவறியது. மீண்டும் முயற்சிக்கவும்.",
      'te': "❌ PDF ఎగుమతి విఫలమైంది. దయచేసి మళ్లీ ప్రయత్నించండి.",
      'bn': "❌ পিডিএফ রপ্তানি করতে ব্যর্থ হয়েছে। অনুগ্রহ করে আবার চেষ্টা করুন।"
    };
    return errors[lang] || errors['en'];
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div className="chat-header-info">
          <div className="bot-avatar">🤖</div>
          <div className="bot-status">
            <h3>AarogyaAI Health Assistant</h3>
            <span className="status online">● Online</span>
          </div>
        </div>
        <div className="chat-actions">
          <button className="export-pdf-btn" onClick={exportToPDF} title="Export chat to PDF">
            📄 Export PDF
          </button>
          <button className="clear-chat-btn" onClick={clearChat} title="Clear chat">
            🗑️
          </button>
        </div>
      </div>

      <div 
        className="messages-container" 
        ref={messagesContainerRef}
        onScroll={handleScroll}
      >
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {isTyping && (
          <div className="typing-indicator">
            <div className="typing-bubble">
              <span className="typing-dot">•</span>
              <span className="typing-dot">•</span>
              <span className="typing-dot">•</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <textarea
          ref={inputRef}
          className="message-input"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={getPlaceholderText(selectedLanguage)}
          rows="1"
          disabled={isLoading}
        />
        <button 
          className={`send-button ${isLoading ? 'disabled' : ''}`}
          onClick={sendMessage}
          disabled={isLoading || !inputMessage.trim()}
        >
          {isLoading ? '⏳' : '📤'}
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
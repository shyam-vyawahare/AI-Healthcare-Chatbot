import React from 'react';
import './QuickButtons.css';

const QuickButtons = ({ selectedLanguage, onSendMessage }) => {
  // This component expects onSendMessage prop from parent
  // If not provided, it will try to find the sendMessage function from ChatInterface
  // For standalone use, we'll create a direct API call

  const quickQuestions = {
    'en': [
      { text: "🤒 Fever symptoms", query: "What are the symptoms of fever and how should I manage it?" },
      { text: "🤧 COVID-19 info", query: "Tell me about COVID-19 symptoms and prevention" },
      { text: "🦟 Dengue prevention", query: "How can I prevent dengue fever?" },
      { text: "💊 Diabetes awareness", query: "What are the early signs of diabetes?" },
      { text: "🧠 Headache relief", query: "What can I do for a severe headache?" },
      { text: "🏥 When to see doctor", query: "When should I see a doctor for my symptoms?" }
    ],
    'hi': [
      { text: "🤒 बुखार के लक्षण", query: "बुखार के लक्षण क्या हैं और इसका प्रबंधन कैसे करें?" },
      { text: "🤧 कोविड-19 जानकारी", query: "मुझे COVID-19 के लक्षण और बचाव के बारे में बताएं" },
      { text: "🦟 डेंगू बचाव", query: "डेंगू बुखार से कैसे बचाव करें?" },
      { text: "💊 मधुमेह जागरूकता", query: "मधुमेह के शुरुआती लक्षण क्या हैं?" },
      { text: "🧠 सिरदर्द राहत", query: "गंभीर सिरदर्द के लिए क्या कर सकता हूं?" },
      { text: "🏥 डॉक्टर कब दिखाएं", query: "लक्षणों के लिए डॉक्टर को कब दिखाना चाहिए?" }
    ],
    'mr': [
      { text: "🤒 तापाची लक्षणे", query: "तापाची लक्षणे काय आहेत आणि ते कसे व्यवस्थापित करावे?" },
      { text: "🤧 कोविड-19 माहिती", query: "मला COVID-19 ची लक्षणे आणि प्रतिबंध याबद्दल सांगा" },
      { text: "🦟 डेंग्यू प्रतिबंध", query: "डेंग्यू तापापासून स्वतःचे संरक्षण कसे करावे?" },
      { text: "💊 मधुमेह जागरूकता", query: "मधुमेहाची सुरुवातीची लक्षणे कोणती?" },
      { text: "🧠 डोकेदुखी आराम", query: "तीव्र डोकेदुखीसाठी मी काय करू शकतो?" },
      { text: "🏥 डॉक्टरकडे कधी जा", query: "लक्षणांसाठी डॉक्टरकडे कधी जावे?" }
    ],
    'ta': [
      { text: "🤒 காய்ச்சல் அறிகுறிகள்", query: "காய்ச்சலின் அறிகுறிகள் என்ன, அதை எவ்வாறு நிர்வகிப்பது?" },
      { text: "🤧 கோவிட்-19 தகவல்", query: "COVID-19 அறிகுறிகள் மற்றும் தடுப்பு பற்றி சொல்லுங்கள்" },
      { text: "🦟 டெங்கு தடுப்பு", query: "டெங்கு காய்ச்சலை எவ்வாறு தடுப்பது?" },
      { text: "💊 நீரிழிவு விழிப்புணர்வு", query: "நீரிழிவு நோயின் ஆரம்ப அறிகுறிகள் யாவை?" },
      { text: "🧠 தலைவலி நிவாரணம்", query: "கடுமையான தலைவலிக்கு நான் என்ன செய்ய முடியும்?" },
      { text: "🏥 மருத்துவரை எப்போது பார்க்க வேண்டும்", query: "அறிகுறிகளுக்கு மருத்துவரை எப்போது பார்க்க வேண்டும்?" }
    ],
    'te': [
      { text: "🤒 జ్వరం లక్షణాలు", query: "జ్వరం యొక్క లక్షణాలు ఏమిటి మరియు దానిని ఎలా నిర్వహించాలి?" },
      { text: "🤧 కోవిడ్-19 సమాచారం", query: "COVID-19 లక్షణాలు మరియు నివారణ గురించి చెప్పండి" },
      { text: "🦟 డెంగ్యూ నివారణ", query: "డెంగ్యూ జ్వరాన్ని ఎలా నివారించాలి?" },
      { text: "💊 మధుమేహం అవగాహన", query: "మధుమేహం యొక్క ప్రారంభ సంకేతాలు ఏమిటి?" },
      { text: "🧠 తలనొప్పి ఉపశమనం", query: "తీవ్రమైన తలనొప్పి కోసం నేను ఏమి చేయగలను?" },
      { text: "🏥 డాక్టర్ ఎప్పుడు చూడాలి", query: "లక్షణాల కోసం నేను ఎప్పుడు డాక్టర్ను చూడాలి?" }
    ],
    'bn': [
      { text: "🤒 জ্বরের লক্ষণ", query: "জ্বরের লক্ষণগুলি কী এবং কীভাবে এটি পরিচালনা করবেন?" },
      { text: "🤧 কোভিড-১৯ তথ্য", query: "আমাকে COVID-19 এর লক্ষণ ও প্রতিরোধ সম্পর্কে বলুন" },
      { text: "🦟 ডেঙ্গু প্রতিরোধ", query: "কীভাবে ডেঙ্গু জ্বর প্রতিরোধ করবেন?" },
      { text: "💊 ডায়াবেটিস সচেতনতা", query: "ডায়াবেটিসের প্রাথমিক লক্ষণগুলি কী কী?" },
      { text: "🧠 মাথাব্যথা উপশম", query: "তীব্র মাথাব্যথার জন্য আমি কী করতে পারি?" },
      { text: "🏥 কখন ডাক্তার দেখাবেন", query: "লক্ষণগুলির জন্য কখন ডাক্তার দেখাবেন?" }
    ]
  };

  const handleQuickQuestion = async (query) => {
    // If onSendMessage prop is provided, use it
    if (onSendMessage) {
      onSendMessage(query);
      return;
    }

    // Otherwise, try to find the input field and send button in the DOM
    // This is a fallback for when the component is used standalone
    const inputField = document.querySelector('.message-input');
    const sendButton = document.querySelector('.send-button');
    
    if (inputField && sendButton) {
      // Set the value
      inputField.value = query;
      // Trigger input event to update React state
      const event = new Event('input', { bubbles: true });
      inputField.dispatchEvent(event);
      // Click send button after a small delay
      setTimeout(() => {
        sendButton.click();
      }, 100);
    } else {
      // If we can't find the elements, log to console
      console.log('Quick question clicked:', query);
      alert(`Quick question: ${query}\n\nNote: Make sure the chat interface is loaded properly.`);
    }
  };

  const currentQuestions = quickQuestions[selectedLanguage] || quickQuestions['en'];

  return (
    <div className="quick-buttons-container">
      <div className="quick-buttons-header">
        <span className="quick-icon">⚡</span>
        <span className="quick-title">Quick Questions</span>
        <span className="quick-subtitle">Click any for instant answer</span>
      </div>
      <div className="quick-buttons-grid">
        {currentQuestions.map((question, index) => (
          <button
            key={index}
            className="quick-button"
            onClick={() => handleQuickQuestion(question.query)}
          >
            {question.text}
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickButtons;
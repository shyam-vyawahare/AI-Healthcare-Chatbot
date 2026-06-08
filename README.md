🏥 AarogyaAI - AI Powered Healthcare Chatbot

AarogyaAI is a multilingual AI-powered healthcare chatbot designed to provide accessible health information and guidance in multiple Indian languages. Built using React, Flask, and Google Gemini AI, the platform helps users understand common health concerns, receive symptom-based guidance, and access healthcare information in their preferred language.

---

🌟 Features

🤖 AI-Powered Healthcare Assistance

- Symptom-based health guidance
- Context-aware healthcare conversations
- AI-generated responses using Google Gemini
- Natural language understanding

🌐 Multilingual Support

Supports 6 languages:

- English
- Hindi (हिंदी)
- Marathi (मराठी)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Bengali (বাংলা)

🔍 Smart Language Detection

- Automatically detects user language
- Responds in the same language used by the user
- No separate translation service required

👤 User Authentication

- Secure JWT-based authentication
- User registration and login
- Protected user sessions

💬 Chat Management

- Persistent conversation history
- Session management
- Easy access to previous chats

📄 PDF Export

- Export healthcare conversations as PDF
- Download consultation summaries
- Easy record keeping

🚨 Emergency Detection

- Detects potentially critical health situations
- Provides emergency guidance
- Encourages immediate medical attention when required

🎁 Guest Mode

- Use without registration
- Limited free messages for quick access
- Seamless upgrade to registered account

---

🏗️ System Architecture

User
 │
 ▼
React Frontend
 │
 ▼
Flask REST API
 │
 ▼
Google Gemini AI
 │
 ▼
JSON Database

Architecture Flow:

Browser (React)
      ↕
Flask Backend API
      ↕
Google Gemini AI
      ↕
JSON Database

---

⚙️ Tech Stack

Frontend

- React.js 18.2
- Axios
- CSS3
- jsPDF
- LocalStorage

Backend

- Python 3.10
- Flask 3.0
- JWT Authentication
- REST APIs

Artificial Intelligence

- Google Gemini 2.0 Flash

Database

- JSON Database

---

🔄 Workflow

1. User opens AarogyaAI.
2. User selects Guest Mode or Login/Register.
3. User chooses preferred language.
4. User enters a healthcare-related query.
5. React frontend sends request to Flask backend.
6. Backend validates the request.
7. Emergency detection module checks for critical symptoms.
8. Query is forwarded to Google Gemini AI.
9. Gemini detects language and generates a healthcare response.
10. Response is returned in the user's language.
11. Chat history is stored.
12. User may export the conversation as PDF.

---

🔐 JWT Authentication Flow

User Login
     │
     ▼
Credential Verification
     │
     ▼
JWT Token Generation
     │
     ▼
Token Sent to Frontend
     │
     ▼
Stored in LocalStorage
     │
     ▼
Protected API Requests
     │
     ▼
Token Verification
     │
     ▼
Access Granted / Denied

---

📊 Project Highlights

Feature| Description
AI Model| Google Gemini 2.0 Flash
Languages Supported| 6
Authentication| JWT
Chat Persistence| LocalStorage + JSON DB
User Modes| Guest & Registered
PDF Export| Available
Emergency Detection| Available
Response Generation| AI Powered

---

🚀 Installation

Clone Repository

git clone https://github.com/your-username/aarogya-ai.git
cd aarogya-ai

---

Backend Setup

cd backend
pip install -r requirements.txt
python app.py

Backend runs on:

http://localhost:5000

---

Frontend Setup

cd frontend
npm install
npm start

Frontend runs on:

http://localhost:3000

---

📁 Project Structure

AarogyaAI/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── app.py
│   ├── routes/
│   ├── services/
│   ├── database/
│   └── requirements.txt
│
├── README.md
└── .env

---

🎯 Use Cases

- General healthcare guidance
- Symptom understanding
- Health awareness
- Multilingual healthcare support
- Quick medical information access
- Educational healthcare assistance

---

🔮 Future Scope

- Voice-based interaction
- Doctor appointment booking
- Hospital locator integration
- Medical image analysis
- Electronic Health Records (EHR)
- Mobile application deployment
- Personalized healthcare recommendations
- Wearable device integration

---

👨‍💻 Developed By

Final Year Engineering Project

Department of Electronics & Computer Engineering

---

⚠️ Important Note

AarogyaAI uses Artificial Intelligence to generate healthcare-related responses. While every effort is made to provide useful and relevant information, AI-generated responses may occasionally be incomplete, inaccurate, outdated, or unsuitable for specific medical situations.

Users should independently verify critical information before making healthcare decisions.

---

🚑 Medical Disclaimer

AarogyaAI is intended for educational and informational purposes only and does not provide professional medical diagnosis, treatment, or emergency care.

The chatbot should not be considered a substitute for qualified healthcare professionals. Always consult a licensed doctor or healthcare provider for medical advice, diagnosis, treatment, or emergencies.

If you are experiencing severe symptoms or a medical emergency, immediately contact emergency services or seek professional medical assistance.pip install -r requirements.txt
python app.py
Frontend Setup
cd frontend
npm install
npm start

---

# 🎓 Creators

## Shyam Vyawahare 🍁
Backend developer, API ans AI executive

## Ashish Sarda 🍂
Frontend Developer and AI Engineer

---

# 📄 License

This project is developed for educational and research purposes.

---

# 🌟 Acknowledgement

Special thanks to all contributors and open-source technologies that supported the development of this AI-powered healthcare solution.

---

# 💬 Note
This project is currently under development, there maybe some bugs or invalid responses and answers given by the Aarogya AI can be wrong for some questions. Do not rely on an online AI advices for your health issues. Using this AI for healthcare is just an informative and awareness solution, consulting a real Doctor is always recommended.

# 🏥 AarogyaAI - Multilingual Health Chatbot

> *"Because health info shouldn't need a translator."*

---

## What is this?

AI chatbot that speaks **6 Indian languages** - English, Hindi, Marathi, Tamil, Telugu, Bengali.

No copy-pasting into Google Translate. Just type in your language, get answers in the same language.

**Try guest mode (3 free messages) or sign up.**

---

## Why I built this

My grandmother speaks Marathi. Finding reliable health info in her language? Impossible.

So I built this.

---

## Tech Stack (short)

| Layer | What |
|-------|------|
| Frontend | React 18, CSS3, Axios |
| Backend | Python, Flask, JWT |
| AI | Google Gemini 2.0 Flash |
| Auth | JWT + SHA-256 |
| DB | JSON (dev), LocalStorage |

**Gemini handles BOTH health responses AND translation** - no external API costs.

---

## Features that matter

✅ **6 languages** - Real-time switching  
✅ **Guest mode** - 3 messages, no signup  
✅ **Emergency detection** - "heart attack" → "Call 108"  
✅ **Chat history** - Date-wise in sidebar  
✅ **PDF export** - Share with doctors  
✅ **State persistence** - Refresh doesn't log you out  
✅ **Dark theme** - Because why not

---

## Quick Start (2 min)

```bash
# Backend
cd backend
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key" > .env
python app.py

# Frontend (new terminal)
cd frontend
npm install
npm start
```

Open `localhost:3000`

---

## What makes this different?

| Feature | AarogyaAI | Others |
|---------|-----------|--------|
| Speaks Hindi/Marathi/Tamil | ✅ | ❌ |
| Guest access | ✅ (3 msgs) | ❌ |
| Remembers conversation | ✅ | ❌ |
| PDF export | ✅ | ❌ |

---

## Challenges I fixed

- **Cut-off responses** → Increased token limit to 1200
- **Slow translation** → Made Gemini do it natively
- **Blank PDF export** → 2 days debugging html2canvas
- **State loss on refresh** → localStorage sync

---

## What's next

- Voice input (for elderly users)
- Mobile app (React Native)
- Medicine reminders
- PostgreSQL for production

---

## Team

| Name | Role |
|------|------|
| Ashish Sarda | Frontend + AI integration |
| Shyam Vyawahare | Backend + Auth |

---

## Run in production?

```bash
# Backend: Gunicorn + Nginx
# Frontend: Vercel / Netlify
# Add PostgreSQL instead of JSON
```

---

## License

MIT - Use it, break it, fix it.

---

**⭐ Star this if it helped you. Helps me get interviews.**

[GitHub Repo](https://github.com/yourusername/AarogyaAI) | [Live Demo](https://aarogyaai.example.com)

---

*3 weeks. Late nights. No boilerplate. Just code.*

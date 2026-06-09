import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [guestId, setGuestId] = useState(null);
  const [guestMessageCount, setGuestMessageCount] = useState(0);
  const [guestMaxMessages, setGuestMaxMessages] = useState(3);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState('home');
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);

  // Load all persisted state on mount
  useEffect(() => {
    const loadPersistedState = async () => {
      // Load auth state
      const storedToken = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');
      const storedGuestId = localStorage.getItem('guestId');
      const storedGuestCount = localStorage.getItem('guestMessageCount');
      
      // Load app state
      const storedPage = localStorage.getItem('currentPage');
      const storedLanguage = localStorage.getItem('selectedLanguage');
      const storedMessages = localStorage.getItem('chatMessages');
      const storedSessionId = localStorage.getItem('sessionId');

      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
        
        // Verify token is still valid
        try {
          const response = await axios.get('http://localhost:5000/api/auth/me', {
            headers: { Authorization: `Bearer ${storedToken}` }
          });
          if (response.data.user) {
            setUser(response.data.user);
          }
        } catch (error) {
          // Token expired, clear storage
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setToken(null);
          setUser(null);
        }
      }
      
      if (storedGuestId && !storedToken) {
        setGuestId(storedGuestId);
        setGuestMessageCount(parseInt(storedGuestCount) || 0);
      }
      
      // Restore app state
      if (storedPage && storedPage !== 'home' && storedPage !== 'team' && storedPage !== 'login' && storedPage !== 'signup') {
        setCurrentPage(storedPage);
      }
      
      if (storedLanguage) {
        setSelectedLanguage(storedLanguage);
      }
      
      if (storedMessages) {
        try {
          const parsedMessages = JSON.parse(storedMessages);
          setMessages(parsedMessages);
        } catch (e) {
          console.error('Error parsing stored messages:', e);
        }
      }
      
      if (storedSessionId) {
        setSessionId(storedSessionId);
      } else {
        const newSessionId = uuidv4();
        setSessionId(newSessionId);
        localStorage.setItem('sessionId', newSessionId);
      }
      
      setIsLoading(false);
    };
    
    loadPersistedState();
  }, []);

  // Persist state changes
  useEffect(() => {
    if (currentPage) {
      localStorage.setItem('currentPage', currentPage);
    }
  }, [currentPage]);

  useEffect(() => {
    if (selectedLanguage) {
      localStorage.setItem('selectedLanguage', selectedLanguage);
    }
  }, [selectedLanguage]);

  useEffect(() => {
    if (messages.length > 0) {
      // Only store last 50 messages to avoid localStorage limit
      const messagesToStore = messages.slice(-50);
      localStorage.setItem('chatMessages', JSON.stringify(messagesToStore));
    }
  }, [messages]);

  const uuidv4 = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  };

  const createGuestSession = async () => {
    try {
      const response = await axios.post('http://localhost:5000/api/auth/guest');
      const { guest_id, max_messages, message_count } = response.data;
      setGuestId(guest_id);
      setGuestMaxMessages(max_messages);
      setGuestMessageCount(message_count);
      localStorage.setItem('guestId', guest_id);
      localStorage.setItem('guestMessageCount', message_count);
      return { success: true };
    } catch (error) {
      console.error('Guest session creation failed:', error);
      return { success: false };
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (userData) => {
    try {
      const response = await axios.post('http://localhost:5000/api/auth/signup', userData);
      const { token, user } = response.data;
      setToken(token);
      setUser(user);
      setGuestId(null);
      setCurrentPage('chat');
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.removeItem('guestId');
      localStorage.removeItem('guestMessageCount');
      localStorage.setItem('currentPage', 'chat');
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Signup failed' };
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post('http://localhost:5000/api/auth/login', { email, password });
      const { token, user } = response.data;
      setToken(token);
      setUser(user);
      setGuestId(null);
      setCurrentPage('chat');
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.removeItem('guestId');
      localStorage.removeItem('guestMessageCount');
      localStorage.setItem('currentPage', 'chat');
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Login failed' };
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await axios.post('http://localhost:5000/api/auth/logout', {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    }
    
    setUser(null);
    setToken(null);
    setMessages([]);
    setCurrentPage('home');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('chatMessages');
    localStorage.removeItem('currentPage');
    createGuestSession();
  };

  const incrementGuestMessage = async () => {
    if (!guestId) return false;
    
    try {
      const response = await axios.post('http://localhost:5000/api/auth/guest/increment', {
        guest_id: guestId
      });
      const { remaining, message_count } = response.data;
      setGuestMessageCount(message_count);
      localStorage.setItem('guestMessageCount', message_count);
      return { remaining, canChat: remaining > 0 };
    } catch (error) {
      console.error('Failed to increment guest count:', error);
      return { remaining: 0, canChat: false };
    }
  };

  const checkGuestLimit = async () => {
    if (!guestId) return { canChat: true, remaining: guestMaxMessages };
    
    try {
      const response = await axios.post('http://localhost:5000/api/auth/guest/check', {
        guest_id: guestId
      });
      return response.data;
    } catch (error) {
      return { remaining: 0, canChat: false };
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await axios.put('http://localhost:5000/api/auth/profile', profileData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const { user: updatedUser } = response.data;
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Update failed' };
    }
  };

  const getChatHistory = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/auth/chat-history', {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
      return { history: {}, all_chats: [] };
    }
  };

  const saveChat = async (chatData) => {
    if (!token) return;
    
    try {
      await axios.post('http://localhost:5000/api/auth/chat-history', chatData, {
        headers: { Authorization: `Bearer ${token}` }
      });
    } catch (error) {
      console.error('Failed to save chat:', error);
    }
  };

  const addMessage = (message) => {
    setMessages(prev => [...prev, message]);
  };

  const clearMessages = () => {
    setMessages([]);
    localStorage.removeItem('chatMessages');
  };

  const navigateTo = (page) => {
    setCurrentPage(page);
    localStorage.setItem('currentPage', page);
  };

  const value = {
    // State
    user,
    token,
    guestId,
    isAuthenticated: !!user,
    isGuest: !user && !!guestId,
    guestMessageCount,
    guestMaxMessages,
    isLoading,
    currentPage,
    selectedLanguage,
    messages,
    sessionId,
    
    // Setters
    setSelectedLanguage,
    setMessages,
    addMessage,
    clearMessages,
    navigateTo,
    
    // Auth methods
    signup,
    login,
    logout,
    createGuestSession,
    
    // Guest methods
    incrementGuestMessage,
    checkGuestLimit,
    
    // User methods
    updateProfile,
    getChatHistory,
    saveChat,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
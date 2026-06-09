// Utility functions for state persistence

export const saveState = (key, value) => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error('Error saving state:', error);
      return false;
    }
  };
  
  export const loadState = (key, defaultValue = null) => {
    try {
      const saved = localStorage.getItem(key);
      if (saved) {
        return JSON.parse(saved);
      }
      return defaultValue;
    } catch (error) {
      console.error('Error loading state:', error);
      return defaultValue;
    }
  };
  
  export const clearState = (keys) => {
    try {
      keys.forEach(key => localStorage.removeItem(key));
      return true;
    } catch (error) {
      console.error('Error clearing state:', error);
      return false;
    }
  };
  
  // Session management
  export const saveSession = (sessionData) => {
    sessionStorage.setItem('currentSession', JSON.stringify(sessionData));
  };
  
  export const loadSession = () => {
    const session = sessionStorage.getItem('currentSession');
    return session ? JSON.parse(session) : null;
  };
  
  export const clearSession = () => {
    sessionStorage.removeItem('currentSession');
  };
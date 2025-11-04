import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI, storeTokens, clearTokens, storeUser, getStoredUser } from '../services/api';

interface User {
  email: string;
  full_name?: string;
  two_factor_enabled: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<any>;
  loginWith2FA: (email: string, password: string, totpCode: string) => Promise<any>;
  register: (email: string, password: string, fullName?: string) => Promise<any>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const storedUser = await getStoredUser();
      setUser(storedUser);
    } catch (error) {
      console.error('Error loading user:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await authAPI.login(email, password);
    
    // Check if 2FA is required
    if (response.requires_2fa) {
      return { requires_2fa: true };
    }

    // Normal login
    await storeTokens(response.access_token, response.refresh_token);
    await storeUser(response.user);
    setUser(response.user);
    
    return { success: true, user: response.user };
  };

  const loginWith2FA = async (email: string, password: string, totpCode: string) => {
    const response = await authAPI.loginWith2FA(email, password, totpCode);
    
    await storeTokens(response.access_token, response.refresh_token);
    await storeUser(response.user);
    setUser(response.user);
    
    return { success: true, user: response.user };
  };

  const register = async (email: string, password: string, fullName?: string) => {
    const response = await authAPI.register(email, password, fullName);
    
    await storeTokens(response.access_token, response.refresh_token);
    await storeUser(response.user);
    setUser(response.user);
    
    return { success: true, user: response.user };
  };

  const logout = async () => {
    await authAPI.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        loginWith2FA,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

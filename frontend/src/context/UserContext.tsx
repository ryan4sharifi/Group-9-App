// context/UserContext.tsx
import React, { createContext, useContext, useState, useEffect, type ReactNode } from "react";

interface UserContextType {
  userId: string | null;
  role: string | null;
  setUserId: (id: string | null) => void;
  setRole: (role: string | null) => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [userId, setUserId] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);

  
  useEffect(() => {
    const storedUserId = sessionStorage.getItem("user_id");
    const storedRole = sessionStorage.getItem("role");
    if (storedUserId) setUserId(storedUserId);
    if (storedRole) setRole(storedRole);
  }, []);

  return (
    <UserContext.Provider value={{ userId, setUserId, role, setRole }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) throw new Error("useUser must be used within UserProvider");
  return context;
};
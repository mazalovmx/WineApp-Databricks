"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import type { Locale } from "@/lib/translations";
import { me } from "@/lib/api";

type AppState = {
  locale: Locale;
  setLocale: (l: Locale) => void;
  user: { user_id: string; locale: string } | null;
  setUser: (u: { user_id: string; locale: string } | null) => void;
  token: string | null;
  refreshAuth: () => void;
};

const AppContext = createContext<AppState | null>(null);

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");
  const [user, setUser] = useState<{ user_id: string; locale: string } | null>(null);
  const [token, setToken] = useState<string | null>(null);

  const refreshAuth = () => {
    const t = localStorage.getItem("token");
    setToken(t);
    if (t) {
      me()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem("token");
          setToken(null);
          setUser(null);
        });
    } else {
      setUser(null);
    }
  };

  useEffect(() => {
    refreshAuth();
  }, []);

  useEffect(() => {
    const stored = localStorage.getItem("locale") as Locale | null;
    if (stored === "en" || stored === "ru") setLocaleState(stored);
  }, []);

  const setLocale = (l: Locale) => {
    setLocaleState(l);
    localStorage.setItem("locale", l);
  };

  return (
    <AppContext.Provider value={{ locale, setLocale, user, setUser, token, refreshAuth }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}

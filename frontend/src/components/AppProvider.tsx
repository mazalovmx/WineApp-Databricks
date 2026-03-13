"use client";
import { AppProvider as AppProviderContext } from "@/context/AppContext";

export function AppProvider({ children }: { children: React.ReactNode }) {
  return <AppProviderContext>{children}</AppProviderContext>;
}

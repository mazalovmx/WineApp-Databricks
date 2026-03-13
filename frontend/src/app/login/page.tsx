"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Header } from "@/components/Header";
import { useApp } from "@/context/AppContext";
import { getTranslations } from "@/lib/translations";
import { login } from "@/lib/api";

export default function LoginPage() {
  const { locale, refreshAuth } = useApp();
  const t = getTranslations(locale);
  const router = useRouter();
  const [userId, setUserId] = useState("A");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(userId, password);
      refreshAuth();
      router.push("/");
    } catch {
      setError("Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />
      <main className="mx-auto max-w-sm px-4 py-12">
        <h1 className="mb-6 text-2xl font-semibold text-amber-900">
          {t.login}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-stone-700">
              {t.user}
            </label>
            <select
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="mt-1 w-full rounded border border-amber-200 px-3 py-2"
            >
              <option value="A">User A</option>
              <option value="B">User B</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700">
              {t.password}
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded border border-amber-200 px-3 py-2"
              required
            />
          </div>

          {error && <p className="text-red-600">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-amber-600 py-2 font-medium text-white hover:bg-amber-700 disabled:opacity-50"
          >
            {loading ? "..." : t.login}
          </button>
        </form>

        <p className="mt-4 text-sm text-stone-500">
          Passwords from USER_A_PASSWORD / USER_B_PASSWORD in backend .env
        </p>
      </main>
    </div>
  );
}

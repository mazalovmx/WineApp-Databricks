"use client";
import Link from "next/link";
import { useApp } from "@/context/AppContext";

export function Header() {
  const { locale, setLocale, token } = useApp();
  return (
    <header className="border-b border-amber-200/40 bg-amber-50/30 px-4 py-3">
      <div className="mx-auto flex max-w-4xl items-center justify-between">
        <Link href="/" className="text-xl font-semibold text-amber-900">
          🍷 Wine Finder
        </Link>
        <nav className="flex items-center gap-4">
          <Link href="/" className="text-sm text-amber-800 hover:underline">
            {locale === "ru" ? "Главная" : "Home"}
          </Link>
          <Link href="/tried" className="text-sm text-amber-800 hover:underline">
            {locale === "ru" ? "Пробовал" : "Tried"}
          </Link>
          <Link href="/rate" className="text-sm text-amber-800 hover:underline">
            {locale === "ru" ? "Оценить" : "Rate"}
          </Link>
          <Link href="/settings" className="text-sm text-amber-800 hover:underline">
            {locale === "ru" ? "Настройки" : "Settings"}
          </Link>
          <button
            onClick={() => setLocale(locale === "en" ? "ru" : "en")}
            className="rounded bg-amber-200 px-2 py-1 text-sm font-medium text-amber-900 hover:bg-amber-300"
          >
            {locale === "en" ? "RU" : "EN"}
          </button>
          {!token && (
            <Link
              href="/login"
              className="rounded bg-amber-600 px-3 py-1 text-sm text-white hover:bg-amber-700"
            >
              {locale === "ru" ? "Войти" : "Login"}
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}

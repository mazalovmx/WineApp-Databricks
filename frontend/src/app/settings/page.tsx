"use client";

import { useState } from "react";
import { Header } from "@/components/Header";
import { useApp } from "@/context/AppContext";
import { getTranslations } from "@/lib/translations";
import { triggerRun } from "@/lib/api";

export default function SettingsPage() {
  const { locale, setLocale, user } = useApp();
  const t = getTranslations(locale);
  const [running, setRunning] = useState(false);
  const [runMessage, setRunMessage] = useState<string | null>(null);

  const handleManualRun = async () => {
    setRunning(true);
    setRunMessage(null);
    try {
      await triggerRun();
      setRunMessage("Pipeline started.");
    } catch (e) {
      setRunMessage(e instanceof Error ? e.message : "Failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />
      <main className="mx-auto max-w-2xl px-4 py-8">
        <h1 className="mb-6 text-2xl font-semibold text-amber-900">
          {t.settings}
        </h1>

        <div className="space-y-6">
          <section>
            <h2 className="mb-2 font-medium text-stone-700">{t.user}</h2>
            <p className="text-stone-600">
              {user ? `Logged in as User ${user.user_id}` : "Not logged in"}
            </p>
          </section>

          <section>
            <h2 className="mb-2 font-medium text-stone-700">{t.language}</h2>
            <div className="flex gap-2">
              <button
                onClick={() => setLocale("en")}
                className={`rounded px-4 py-2 ${
                  locale === "en"
                    ? "bg-amber-600 text-white"
                    : "bg-amber-100 text-amber-900 hover:bg-amber-200"
                }`}
              >
                {t.english}
              </button>
              <button
                onClick={() => setLocale("ru")}
                className={`rounded px-4 py-2 ${
                  locale === "ru"
                    ? "bg-amber-600 text-white"
                    : "bg-amber-100 text-amber-900 hover:bg-amber-200"
                }`}
              >
                {t.russian}
              </button>
            </div>
          </section>

          <section>
            <h2 className="mb-2 font-medium text-stone-700">{t.manual_run}</h2>
            <p className="mb-2 text-sm text-stone-600">
              Trigger the recommendation pipeline manually.
            </p>
            <button
              onClick={handleManualRun}
              disabled={running}
              className="rounded-lg bg-amber-600 px-4 py-2 font-medium text-white hover:bg-amber-700 disabled:opacity-50"
            >
              {running ? "Running…" : t.manual_run}
            </button>
            {runMessage && (
              <p className="mt-2 text-sm text-stone-600">{runMessage}</p>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/Header";
import { useApp } from "@/context/AppContext";
import { getTranslations } from "@/lib/translations";
import { getTriedWines } from "@/lib/api";

export default function TriedPage() {
  const { locale } = useApp();
  const t = getTranslations(locale);
  const [wines, setWines] = useState<Array<{
    wine_id: number;
    wine_name: string;
    type: string | null;
    rating: number;
    comment: string | null;
    tried_at: string | null;
    rated_at: string | null;
  }>>([]);
  const [query, setQuery] = useState("");
  const [wineType, setWineType] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTriedWines(query || undefined, wineType || undefined)
      .then(setWines)
      .catch(() => setWines([]))
      .finally(() => setLoading(false));
  }, [query, wineType]);

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />
      <main className="mx-auto max-w-4xl px-4 py-8">
        <h1 className="mb-6 text-2xl font-semibold text-amber-900">
          {t.tried_wines}
        </h1>

        <div className="mb-6 flex flex-wrap gap-4">
          <input
            type="text"
            placeholder={t.search}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="rounded border border-amber-200 px-3 py-2 text-sm"
          />
          <select
            value={wineType}
            onChange={(e) => setWineType(e.target.value)}
            className="rounded border border-amber-200 px-3 py-2 text-sm"
          >
            <option value="">{t.filter_by_type}</option>
            <option value="red">{t.red}</option>
            <option value="white">{t.white}</option>
            <option value="rose">{t.rose}</option>
            <option value="sparkling">{t.sparkling}</option>
          </select>
        </div>

        {loading && <p className="text-stone-600">Loading…</p>}

        {!loading && wines.length === 0 && (
          <p className="text-stone-600">{t.no_tried}</p>
        )}

        {!loading && wines.length > 0 && (
          <ul className="space-y-3">
            {wines.map((w) => (
              <li
                key={w.wine_id}
                className="rounded-lg border border-amber-200/60 bg-white p-4 shadow-sm"
              >
                <div className="flex justify-between">
                  <span className="font-medium">{w.wine_name}</span>
                  <span className="text-amber-700">
                    {t.rating}: {w.rating}/5
                  </span>
                </div>
                {w.type && (
                  <p className="mt-1 text-sm text-stone-500">{w.type}</p>
                )}
                {w.comment && (
                  <p className="mt-2 text-sm text-stone-600">{w.comment}</p>
                )}
                {w.rated_at && (
                  <p className="mt-2 text-xs text-stone-400">
                    Rated {new Date(w.rated_at).toLocaleDateString()}
                  </p>
                )}
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}

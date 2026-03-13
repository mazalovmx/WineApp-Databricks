"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Header } from "@/components/Header";
import { useApp } from "@/context/AppContext";
import { getTranslations } from "@/lib/translations";
import { getRecommendations, health } from "@/lib/api";

export default function HomePage() {
  const { locale } = useApp();
  const t = getTranslations(locale);
  const [recs, setRecs] = useState<Array<{
    kind: string;
    rank: number;
    wine_name: string;
    price_mxn: number | null;
    explanation: string;
    product_url: string | null;
    store_name: string | null;
  }>>([]);
  const [lastRun, setLastRun] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getRecommendations(), health()])
      .then(([r, h]) => {
        setRecs(r);
        setLastRun(h.last_successful_run);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed"))
      .finally(() => setLoading(false));
  }, []);

  const buys = recs.filter((x) => x.kind === "recommended_buys");
  const favorites = recs.filter((x) => x.kind === "cheapest_favorites");

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />
      <main className="mx-auto max-w-4xl px-4 py-8">
        <p className="mb-6 text-sm text-stone-500">
          {t.last_refresh}: {lastRun ? new Date(lastRun).toLocaleString() : t.never}
        </p>

        {error && (
          <div className="rounded-lg border border-amber-300 bg-amber-50 p-4 text-amber-800">
            {error}
          </div>
        )}

        {loading && <p className="text-stone-600">Loading…</p>}

        {!loading && !error && (
          <>
            <section className="mb-10">
              <h2 className="mb-4 text-xl font-semibold text-amber-900">
                {t.recommended_buys}
              </h2>
              {buys.length === 0 ? (
                <p className="text-stone-600">{t.no_recommendations}</p>
              ) : (
                <ul className="space-y-3">
                  {buys.map((r) => (
                    <li
                      key={`${r.kind}-${r.rank}`}
                      className="rounded-lg border border-amber-200/60 bg-white p-4 shadow-sm"
                    >
                      <div className="flex justify-between">
                        <span className="font-medium">{r.wine_name}</span>
                        {r.price_mxn != null && (
                          <span className="text-amber-800">
                            ${r.price_mxn.toFixed(2)} MXN
                          </span>
                        )}
                      </div>
                      <p className="mt-2 text-sm text-stone-600">{r.explanation}</p>
                      {r.store_name && (
                        <p className="mt-1 text-xs text-stone-500">{r.store_name}</p>
                      )}
                      {r.product_url && (
                        <a
                          href={r.product_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mt-2 inline-block text-sm text-amber-700 hover:underline"
                        >
                          View offer →
                        </a>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </section>

            <section>
              <h2 className="mb-4 text-xl font-semibold text-amber-900">
                {t.cheapest_favorites}
              </h2>
              {favorites.length === 0 ? (
                <p className="text-stone-600">
                  Rate wines 4+ to see them here.
                </p>
              ) : (
                <ul className="space-y-3">
                  {favorites.map((r) => (
                    <li
                      key={`${r.kind}-${r.rank}`}
                      className="rounded-lg border border-amber-200/60 bg-white p-4 shadow-sm"
                    >
                      <div className="flex justify-between">
                        <span className="font-medium">{r.wine_name}</span>
                        {r.price_mxn != null && (
                          <span className="text-amber-800">
                            ${r.price_mxn.toFixed(2)} MXN
                          </span>
                        )}
                      </div>
                      <p className="mt-2 text-sm text-stone-600">{r.explanation}</p>
                      {r.store_name && (
                        <p className="mt-1 text-xs text-stone-500">{r.store_name}</p>
                      )}
                      {r.product_url && (
                        <a
                          href={r.product_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mt-2 inline-block text-sm text-amber-700 hover:underline"
                        >
                          View offer →
                        </a>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}

"use client";

import { useState } from "react";
import { Header } from "@/components/Header";
import { useApp } from "@/context/AppContext";
import { getTranslations } from "@/lib/translations";
import { submitRating } from "@/lib/api";

export default function RatePage() {
  const { locale } = useApp();
  const t = getTranslations(locale);
  const [wineId, setWineId] = useState("");
  const [rating, setRating] = useState(3);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<"success" | "error" | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const wid = parseInt(wineId, 10);
    if (isNaN(wid) || wid < 1) {
      setMessage("error");
      return;
    }
    setSubmitting(true);
    setMessage(null);
    try {
      await submitRating(wid, rating, comment);
      setMessage("success");
      setWineId("");
      setComment("");
    } catch {
      setMessage("error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50">
      <Header />
      <main className="mx-auto max-w-2xl px-4 py-8">
        <h1 className="mb-6 text-2xl font-semibold text-amber-900">
          {t.add_rating}
        </h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-stone-700">
              Wine ID
            </label>
            <input
              type="number"
              min={1}
              value={wineId}
              onChange={(e) => setWineId(e.target.value)}
              className="mt-1 w-full rounded border border-amber-200 px-3 py-2"
              required
            />
            <p className="mt-1 text-xs text-stone-500">
              Find wine IDs from recommendations or tried wines.
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700">
              {t.rating} (1–5)
            </label>
            <select
              value={rating}
              onChange={(e) => setRating(parseInt(e.target.value, 10))}
              className="mt-1 w-full rounded border border-amber-200 px-3 py-2"
            >
              {[1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-stone-700">
              {t.comment}
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={3}
              className="mt-1 w-full rounded border border-amber-200 px-3 py-2"
            />
          </div>

          {message === "success" && (
            <p className="text-green-700">Rating saved.</p>
          )}
          {message === "error" && (
            <p className="text-red-600">Failed to save. Check wine ID.</p>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="rounded-lg bg-amber-600 px-4 py-2 font-medium text-white hover:bg-amber-700 disabled:opacity-50"
          >
            {t.submit}
          </button>
        </form>
      </main>
    </div>
  );
}

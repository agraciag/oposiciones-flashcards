"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:7999';

interface Flashcard {
  id: number;
  front: string;
  back: string;
  article_number: string | null;
  law_name: string | null;
  repetitions: number;
  interval_days: number;
}

type Quality = "again" | "hard" | "good" | "easy";

export default function StudyPage() {
  const [flashcard, setFlashcard] = useState<Flashcard | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(true);
  const [noCards, setNoCards] = useState(false);
  const [studying, setStudying] = useState(false);

  useEffect(() => {
    fetchNextCard();
  }, []);

  const fetchNextCard = async () => {
    setLoading(true);
    setShowAnswer(false);
    try {
      const response = await fetch(`${API_URL}/api/study/next`);
      const data = await response.json();

      if (data === null) {
        setNoCards(true);
        setFlashcard(null);
      } else {
        setFlashcard(data);
        setNoCards(false);
      }
    } catch (error) {
      console.error("Error fetching next card:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (quality: Quality) => {
    if (!flashcard || studying) return;

    setStudying(true);

    try {
      const response = await fetch(`${API_URL}/api/study/review`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          flashcard_id: flashcard.id,
          quality: quality,
          time_spent_seconds: 30,
        }),
      });

      if (response.ok) {
        // Fetch next card
        await fetchNextCard();
      }
    } catch (error) {
      console.error("Error reviewing card:", error);
    } finally {
      setStudying(false);
    }
  };

  const qualityButtons = [
    { quality: "again" as Quality, label: "Otra vez", color: "bg-red-600 hover:bg-red-700", emoji: "❌" },
    { quality: "hard" as Quality, label: "Difícil", color: "bg-orange-600 hover:bg-orange-700", emoji: "😰" },
    { quality: "good" as Quality, label: "Bien", color: "bg-blue-600 hover:bg-blue-700", emoji: "✅" },
    { quality: "easy" as Quality, label: "Fácil", color: "bg-green-600 hover:bg-green-700", emoji: "😊" },
  ];

  if (loading) {
    return (
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto text-center">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-300 rounded w-48 mx-auto mb-4"></div>
            <div className="h-64 bg-gray-300 rounded"></div>
          </div>
        </div>
      </main>
    );
  }

  if (noCards) {
    return (
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="text-6xl mb-4">🎉</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              ¡Excelente trabajo!
            </h2>
            <p className="text-gray-600 mb-6">
              No hay tarjetas pendientes de revisión en este momento.
              <br />
              Vuelve más tarde para continuar con tu estudio.
            </p>
            <Link
              href="/"
              className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              Volver al Inicio
            </Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <Link
            href="/"
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            ← Volver
          </Link>
          {flashcard && (
            <div className="text-sm text-gray-600">
              Repeticiones: {flashcard.repetitions} | Intervalo: {flashcard.interval_days} días
            </div>
          )}
        </div>

        {/* Flashcard */}
        {flashcard && (
          <div className="bg-white rounded-lg shadow-xl p-8 mb-6">
            {/* Metadata */}
            {flashcard.law_name && (
              <div className="mb-4 text-sm text-gray-500">
                {flashcard.article_number && `${flashcard.article_number} - `}
                {flashcard.law_name}
              </div>
            )}

            {/* Front (Question) */}
            <div className="mb-8">
              <div className="text-sm font-semibold text-gray-700 mb-2">
                PREGUNTA
              </div>
              <div className="text-xl font-medium text-gray-900">
                {flashcard.front}
              </div>
            </div>

            {/* Answer (Hidden initially) */}
            {!showAnswer ? (
              <button
                onClick={() => setShowAnswer(true)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors text-lg"
              >
                Mostrar Respuesta
              </button>
            ) : (
              <>
                <div className="mb-6 pb-6 border-t border-gray-200 pt-6">
                  <div className="text-sm font-semibold text-gray-700 mb-2">
                    RESPUESTA
                  </div>
                  <div className="text-lg text-gray-900 whitespace-pre-line">
                    {flashcard.back}
                  </div>
                </div>

                {/* Quality Buttons */}
                <div className="space-y-3">
                  <div className="text-sm font-semibold text-gray-700 mb-3">
                    ¿Qué tal lo recordaste?
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    {qualityButtons.map((btn) => (
                      <button
                        key={btn.quality}
                        onClick={() => handleReview(btn.quality)}
                        disabled={studying}
                        className={`${btn.color} text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
                      >
                        <span className="mr-2">{btn.emoji}</span>
                        {btn.label}
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-gray-700">
          <p className="font-semibold mb-2">💡 Sistema SM-2:</p>
          <ul className="space-y-1 text-gray-600">
            <li>• <strong>Otra vez:</strong> Reinicia el aprendizaje de esta tarjeta</li>
            <li>• <strong>Difícil:</strong> Reducir intervalo de revisión</li>
            <li>• <strong>Bien:</strong> Aumentar intervalo normal</li>
            <li>• <strong>Fácil:</strong> Aumentar intervalo significativamente</li>
          </ul>
        </div>
      </div>
    </main>
  );
}
